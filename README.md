# Events Reporting tester

### The script does not use any additional libraries. (Python 3.10.6 was used)

## Device setup before running
The model that is to be tested should host a wifi network and the device that is to receive the sms messages is to be connected with a static dhcp lease.

## Configuration file example
Configuration file consists of:
    -settings section where the required data of the devices is stored
    -commands section where all types and subtypes of commands are stored

```json
{
    "settings": {
        "sender": {
            "model": "RUTX11",
            "host": "http://192.168.1.1",
            "login": {
                "username": "adminer",
                "password": "123123123"
            },
            "telnum": "**********"
        },
        "recver": {
            "model": "RUT955",
            "host": "http://192.168.1.196",
            "login": {
                "username": "adminer",
                "password": "1212121212"
            },
            "telnum": "**********",
        }
    },
    "commands": {
        "dataTemplate": {
            "data": {
                "id": "",
                ".type": "rule",
                "enable": "1",
                "event": "",
                "eventMark": "",
                "action": "sendSMS",
                "message": "Router name - %rn; Event type - %et; Event text - %ex; Time stamp - %ts",
                "recipEmail": "",
                "emailgroup": "",
                "subject": "",
                "recipient_format": "single",
                "telnum": ""
            }
        },
        "events": {
            "Config": {
                "all": {
                    "path": "/api/services/auto_reboot/ping/config",
                    "req": [
                        {
                            "post": {
                                "data": {}
                            }
                        },
                        {
                            "del": {
                                "data": [
                                    "cfg02c21d"
                                ]
                            }
                        }
                    ],
                    "rsp": {
                        "type": "CONFIG",
                        "text": "ping_reboot configuration has been changed"
                    }
                },
                "openvpn": {
                    "path": "/api/services/openvpn/config",
                    "req": [
                        {
                            "post": {
                                "data": {
                                    "id": "teste",
                                    "type": "server"
                                }
                            }
                        },
                        {
                            "del": {
                                "data": [
                                    "teste"
                                ]
                            }
                        }
                    ],
                    "rsp": {
                        "type": "CONFIG",
                        "text": "openvpn configuration has been changed"
                    }
                },
                ...
```

## Instructions

Executing the program with the help flag (-h) will result in the fallowing output
```
usage: main.py [-h] [-i CONFIGPATH] [-o OUTPUTPATH]

options:
  -h, --help            show this help message and exit
  -i CONFIGPATH, --input CONFIGPATH
                        Specifies path of config.json file.
  -o OUTPUTPATH, --output OUTPUTPATH
                        Specify output directory.
```

Program can be run without additional flags assuming the config.json file is provided beside the main.py file.

The program's shows intermediate results and errors in the console. After finishing all the tests the results are save into the specified file (by default: output/{DeviceName}-{Time}.csv)