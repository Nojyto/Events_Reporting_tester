import json
import time
import requests
import paramiko
from datetime import datetime


class apiInterface:
    PATHS = {
        "login": "/api/login",
        "info": "/api/info",
        "modem": "/api/network/mobile/modems/status_full/",
        "events": "/api/services/events_reporting/config",
        "sms": "/api/services/mobile_utilities/sms_messages/read/config"
    } 

    def __init__(self, cfg, payloadTemplate=None, timeout=30):
        self.host   = cfg["host"]
        self.telnum = cfg["telnum"]
        self.timeout = timeout
        self.login  = {
            "username" : cfg["user"],
            "password" : cfg["pasw"]
        }

        tknobj = requests.post(self.host + self.PATHS["login"], json=self.login, timeout=self.timeout).json()
        if "jwtToken" in tknobj:
            self.token = tknobj["jwtToken"]
        else:
            self.token = tknobj["ubus_rpc_session"]

        self.header = {
            "Authorization": "Bearer " + self.token,
            "Content-type":  "application/json"
        }

        self.model = self.Get(self.PATHS["info"])["data"]["device_name"]
        if self.model != cfg["model"]: raise Exception("Device names does not match")

        self.modemId = self.Get(self.PATHS["modem"])["data"][0]["id"]

        if payloadTemplate is not None:
            self.eventId = self.Post(self.PATHS["events"], json.loads(r'{"data":{}}'))["data"]["id"]
            self.payload = payloadTemplate
            self.payload["data"].update({"id": self.eventId, "telnum": self.telnum})
        else:
            self.Del(self.PATHS["sms"] + f"/{self.modemId}", json.loads(r'{"data": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]}'))


    def __del__(self):
        if hasattr(self, 'eventId'):
            self.Del(self.PATHS["events"], json.loads(f'{{"data":["{self.eventId}"]}}'))


    def updateTemplate(self, eventType, eventSubtype):
        if self.eventId is not None:
            self.payload["data"].update({"event": eventType, "eventMark": eventSubtype})
            rsp = self.Put(self.PATHS["events"] + "/" + self.eventId, self.payload)
            #print(rsp)


    def maintainConnection(req):
        def wrapper(*args):
            startTime = time.time()
            while True:
                try:
                    return req(*args)
                except Exception as e:
                    if time.time() > startTime + args[0].timeout:
                        raise Exception(f"Unable to reestablish connection after {args.self.timeout} seconds of trying. With error: {e}")
                    else:
                        time.sleep(1)
        return wrapper


    @maintainConnection
    def Get(self, path, timeout=None):
        return requests.get(
                    self.host + path,
                    headers=self.header,
                    timeout=self.timeout if timeout is None else timeout
                ).json()


    @maintainConnection
    def Put(self, path, body, timeout=None):
        return requests.put(
                    self.host + path,
                    headers=self.header,
                    json=body,
                    timeout=self.timeout if timeout is None else timeout
                ).json()


    @maintainConnection
    def Post(self, path, body, timeout=None):
        return requests.post(
                    self.host + path,
                    headers=self.header,
                    json=body,
                    timeout=self.timeout if timeout is None else timeout
                ).json()


    @maintainConnection
    def Del(self, path, body, timeout=None):
        return requests.delete(
                    self.host + path,
                    headers=self.header,
                    json=body,
                    timeout=self.timeout if timeout is None else timeout
                ).json()


    # def SSH(self, user, pasw):
    #     try:
    #         client = paramiko.SSHClient()
    #         client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #         client.connect(self.host.removeprefix("http://"), username=user, password=pasw)
    #         time.sleep(3)
    #         # chan = client.invoke_shell()
    #         time.sleep(3)
    #         client.close()
    #     except:
    #         pass


def TestEvent(eventType, eventSubtype, obj, apiSend, apiRecv):
    # Updates template message which is used to update the event reporting instance
    apiSend.updateTemplate(eventType, eventSubtype)
    realTime = datetime.now()
    
    # Sends the apropriate request to toggle the event
    for req in obj["req"]:
        method, payload = list(req.items())[0]
        jj = None
        match method:
            case "get":
                jj = apiSend.Get(obj["path"])
            case "post":
                jj = apiSend.Post(obj["path"], payload)
            case "put":
                jj = apiSend.Put(obj["path"], payload)
            case "del":
                jj = apiSend.Del(obj["path"], payload)
            case "ssh":
                break
                # print(payload["user"], payload["pasw"])
                # jj = apiSend.SSH(payload["user"], payload["pasw"])
            case _:
                jj = "err"
        time.sleep(3)
        #print(method, "--> rsp: ", jj)

    # Wait for sms
    time.sleep(3)

    # Read sms log of the device/ generate expected output
    expected = f'Router name - {apiSend.model}; Event type - {obj["rsp"]["type"]}; Event text - {obj["rsp"]["text"]}; Time stamp - {realTime.strftime("%Y-%m-%d %H:%M:%S")}'
    didpass  = "Failed"
    msg      = "N/A"
    sender   = "N/A"

    smsLog = apiRecv.Get(apiRecv.PATHS["sms"])
    if smsLog["data"]:
        msg = smsLog["data"][0]["message"]
        sender = smsLog["data"][0]["sender"]
        if msg[:-8:] == expected[:-8:] and sender == apiRecv.telnum:
            didpass = "Passed"

    # Deletes the received messages
    apiRecv.Del(apiRecv.PATHS["sms"] + f"/{apiRecv.modemId}", json.loads(r'{"data": ["0", "1", "2", "3", "4", "5"]}'))

    return expected, msg, apiSend.telnum, sender, didpass
