from modules.fileManagement import readConfig, writeLog
from modules.bashFlags import getFlagObj
from modules.apiIF import apiInterface, TestEvent


class bcod:
    OKGREEN   = "\033[92m"
    WARNING   = "\033[93m"
    ERRORRED  = "\033[91m"
    BOLD      = "\033[1m"
    ENDC      = "\033[0m"
    RMLINE    = "\033[F"
    MVBACK    = "\033[K"


if __name__ == "__main__":
    testLog = []
    args = getFlagObj()
    cfg = readConfig("config.json")

    try:
        apiSend = apiInterface(cfg["settings"]["sender"], cfg["commands"]["dataTemplate"])
        apiRecv = apiInterface(cfg["settings"]["recver"])

        if cfg == None:
            raise Exception(f"{args.configPath} file not found.")

        passedTests = 0
        failedTests = 0
        totalEv  = len(cfg["commands"]["events"])

        print(bcod.BOLD + f"Testing {apiSend.model}:" + bcod.ENDC)
        for itrEv, (eventType, _) in enumerate(cfg["commands"]["events"].items(), 1):
            totalTp = len(cfg["commands"]["events"][eventType].items())
            for itrTp, (eventSubtype, obj) in enumerate(cfg["commands"]["events"][eventType].items(), 1):
                res = [_, _, _, _, didpass] = TestEvent(eventType, eventSubtype, obj, apiSend, apiRecv)
                testLog.append(', '.join(res).replace(';', ' ') + '\n')

                if res[4] == "Passed":
                    print(f"[{itrEv:>1}/{totalEv:>1}][{itrTp:>2}/{totalTp:>2}] Testing event: {(eventType+'::'+eventSubtype):<25}  Status: " + bcod.OKGREEN + "PASSED" + bcod.ENDC)
                    passedTests += 1
                else:
                    print(f"[{itrEv:>1}/{totalEv:>1}][{itrTp:>2}/{totalTp:>2}] Testing event: {(eventType+'::'+eventSubtype):<25}  Status: " + bcod.ERRORRED + "FAILED" + bcod.ENDC)
                    failedTests += 1
                print(bcod.BOLD     + "Total results: " + bcod.ENDC + 
                        bcod.OKGREEN  + str(passedTests)  + bcod.ENDC + "/" +
                        bcod.ERRORRED + str(failedTests)  + bcod.ENDC)
                print((bcod.RMLINE+bcod.MVBACK)*2, end="")
        filePath, fileName = writeLog(args.outputPath, apiSend.model, testLog)
        print("Done. Output file location:", filePath)
    except Exception as e:
        print(bcod.WARNING + bcod.BOLD + f"Error: {e}" + bcod.ENDC)
    else:
        print(bcod.BOLD + f"\nTest's completed succesfully." + bcod.ENDC)
        testLog = []
    finally:
        if testLog:
            writeLog(args.outputPath, apiSend.model, testLog)
        print("Exiting...")

# ka noreciau padaryt/patobulint taciau nezinau kaip
# --tikrint ar yra sms kortele

# Is Config change kas neveikia (ant RUTX_R_00.07.03.3)
# snmpd (del ubus authentication)
# hostblock (del ubus authentication)

# Is kitu tipu neveike
# DHCP (neveike settingu keitimas)
# Reboot (nepavyko implementuot)
# SSH (yra bandymas sshtry.json / nepavyko implementuot)
# Web UI
# New WiFi client (nezinau kaip igyvendint)
# Topology (neveike)
# Port state (praleidau)
# Signal strenght (praleidau)