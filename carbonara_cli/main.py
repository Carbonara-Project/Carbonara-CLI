import sys
import time
import requests
import progressbar
import json
import os
import appdirs
import getpass
from guanciale import *

dirs = appdirs.AppDirs("carbonara_cli")
token_path = os.path.join(os.path.dirname(dirs.user_config_dir), "carbonara_cli.token")

CARBONARA_URL = "https://carbonaraproject.com"
#CARBONARA_URL = "http://localhost:8000"
CLIENT_ID="2MBBuSf2kKNhHyDMjKi80jJPeJqzhYdzsOxzHM3z"

token = None

def get_token():
    global token
    
    request_token = False
    try:
        token_file = open(token_path)
        token = token_file.read()
        token_file.close()
    except:
        request_token = True
    
    #verify token
    if not request_token:
        headers = {"Authorization": "Bearer " + token}
        try:
            r = requests.head(CARBONARA_URL, headers=headers)
        except:
            return "cannot verify auth token"
        
        if r.status_code == 401 or r.status_code == 403: #token expired
            request_token = True
        elif r.status_code != 200:
            return "cannot verify auth token"
    
    if request_token:
        print LCYAN + " >> Login to Carbonara " + NC
        username = raw_input("Username: ")
        password = getpass.getpass("Password: ")
        auth_body = {
            "client_id": CLIENT_ID,
            "grant_type": "password",
            "username": username,
            "password": password
        }
        try:
            r = requests.post(CARBONARA_URL + "/users/o/token/", data=auth_body)
        except:
            return "cannot get auth token"
        
        if r.status_code != 200:
            return "cannot get auth token"
        token = r.json()["access_token"]
    
    if token == None:
        return "wrong authentication"
    
    try:
        token_file = open(token_path, "w")
        token_file.write(token)
        token_file.close()
    except:
        printwarn("cannot save auth token")
        pass


def exists(md5):
    err = get_token()
    if err:
        printerr(err)
        exit(1)
    
    headers = {"Authorization": "Bearer " + token}
    try:
        r = requests.head(CARBONARA_URL + "/api/program/?md5=" + md5, headers=headers)
    except:
        printerr("failed to connect to Carbonara")
        exit(1)
    if r.status_code == 404:
        return False
    elif r.status_code == 200 or r.status_code == 204:
        return True
    else:
        printerr("invalid response")
        exit(1)


def identify(bi):
    procs_dict = {}
    
    payload = {}
    for p in bi.procs:
        if p["size"] > 32:
            payload[bi.md5+":"+str(p["offset"])] = 3
            procs_dict[p["offset"]] = p["name"]
    
    r = None
    headers = {"Authorization": "Bearer " + token}
    err=False
    try:
        print(" >> Querying Carbonara...")
        r = requests.post(CARBONARA_URL + "/api/simprocs/", headers=headers, json=payload)
        if r.status_code != 200:
            print(r.content)
            err = True
    except Exception as ee:
        print ee
        err = True
    if err:
        printerr("cannot get similar procedures")
        
    resp = r.json()
    
    result = {}
    
    for k in resp:
        if len(resp[k]) == 0:
            continue
        off = int(k.split(":")[1])
        
        for r in resp[k]:
            if r["match"] >= 85 and r["md5"] != bi.md5:
                #print r["md5"] + "  " + r["name"]
                result[r["md5"]] = result.get(r["md5"], 0) +1
            else:
                break
    
    bins = sorted(result, key=result.get, reverse=True)
    print("")
    for md5 in bins:
        print("  %s : %d%%" % (md5, result[md5] * 100.0 / len(bi.procs)))
    print("")



def main():
    args = {}
    binary = None
    hasdb = False

    config.populate()

    #report status on stdout using a progressbar
    class ProgressBarStatus(status.Status):
        def __init__(self, maxval):
            self.pgbar = progressbar.ProgressBar(redirect_stdout=True, max_value=maxval)
        
        def update(self, num):
            self.pgbar.update(num)
            
        def __enter__(self):
            return self.pgbar.__enter__()

        def __exit__(self, type, value, traceback):
            self.pgbar.__exit__(type, value, traceback)

    status.Status = ProgressBarStatus

    r2plugin = False
    if "R2PIPE_IN" in os.environ:
        r2plugin = True
    
    if (len(sys.argv) < 2 or sys.argv[1] == "-help") and not r2plugin:
        print LMAG_BG + "  usage  " + NC + " carb [OPTIONS] <binary file> "
        exit(0)
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-e" or sys.argv[i] == "--exists":
            args["exists"] = 1
        elif sys.argv[i] == "-p" or sys.argv[i] == "--proc":
            if i == len(sys.argv) -1:
                printerr("arg '--proc': expected one argument")
                exit(1)
            args["proc"] = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == "-s" or sys.argv[i] == "--save":
            args["save"] = 1
        elif sys.argv[i] == "-i" or sys.argv[i] == "--identify":
            args["identify"] = 1
        elif sys.argv[i] == "-l" or sys.argv[i] == "--load":
            if i == len(sys.argv) -1:
                printerr("arg '--load': expected one argument")
                exit(1)
            args["load"] = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == "-a" or sys.argv[i] == "--arch":
            if i == len(sys.argv) -1:
                printerr("arg '--arch': expected one argument")
                exit(1)
            args["arch"] = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == "-b" or sys.argv[i] == "--bits":
            if i == len(sys.argv) -1:
                printerr("arg '--bits': expected one argument")
                exit(1)
            args["bits"] = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == "-r2proj":
            if i == len(sys.argv) -1:
                printerr("arg '-r2proj': expected one argument")
                exit(1)
            if hasdb:
                printwarn("arg '%s': disassembly database already specified, ignored " % sys.argv[i+1])
                i += 1
                continue
            args["r2"] = sys.argv[i+1]
            hasdb = True
            i += 1
        elif sys.argv[i] == "-idb":
            if i == len(sys.argv) -1:
                printerr("arg '-idb': expected one argument")
                exit(1)
            if hasdb:
                printwarn("arg '%s': disassembly database already specified, ignored " % sys.argv[i+1])
                i += 2
                continue
            hasdb = True
            args["idb"] = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == "-idacmd":
            if i == len(sys.argv) -1:
                printerr("arg '-idacmd': expected one argument ")
                exit(1)
            config.idacmd = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == "-ida64cmd":
            if i == len(sys.argv) -1:
                printerr("arg '-ida64cmd': expected one argument")
                exit(1)
            config.ida64cmd = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == "-radare2":
            if i == len(sys.argv) -1:
                printerr("arg '-radare2': expected one argument")
                exit(1)
            config.radare2 = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == "-reconfig":
            config.generateConfig()
        elif sys.argv[i] == "-writeconfig":
            config.writeConfig()
        elif binary == None:
            binary = sys.argv[i]
        elif hasdb:
            printwarn("arg '%s': disassembly database already specified, ignored" % sys.argv[i])
        else:
            dbfile = sys.argv[i]
            ext = os.path.splitext(dbfile)[-1]
            if ext == ".idb" or ext == ".i64":
                args["idb"] = dbfile
            else:
                print " >> no project type info, Radare2 assumed"
                args["r2"] = dbfile
        i += 1

    if binary == None and not r2plugin:
        printerr("binary file not provided")
        exit(1)
    
    start_time = time.time()
    
    if "identify" in args and "proc" in args:
        printerr("a binary can't be identified with only a procedure")
        exit(1)
    
    if "bits" in args and "arch" not in args:
        printerr("if you set custom bits you must also set a custom arch")
        exit(1)
    
    arch_bits = {"arch": None, "bits": None}
    if "arch" in args:
        arch_bits["arch"] = args["arch"].lower()
    if "bits" in args:
        arch_bits["bits"] = args["bits"]
    
    try:
        if r2plugin and binary == None:
            bi = BinaryInfo(R2PLUGIN, **arch_bits)
        else:
            bi = BinaryInfo(binary, **arch_bits)
    except IOError as err:
        print()
        printerr(err)
        exit(1)
    
    if "exists" in args:
        print LCYAN + " >> Result: " + str(exists(bi.md5)) + NC
        exit(0)
    
    if "identify" in args:
        if exists(bi.md5) == True:
            print(" >> The binary is already on the server")
            if "idb" in args:
                bi.grabProcedures("idapro", args["idb"])
            elif "r2" in args:
                bi.grabProcedures("radare2", args["r2"])
            else:
                bi.grabProcedures("radare2")
            identify(bi)
            exit(0)
        else:
            print(" >> The binary is not present in the server, so it must be analyzed.")
    
    
    savedproc = False
    if "load" in args:
        infile = open(args["load"], "r")
        saved = infile.read()
        infile.close()
        if args["load"].endswith("procedure.json"):
            savedproc = True
    else:
        if "proc" not in args:
            bi.addAdditionalInfo()
            bi.addStrings()
        
        if "idb" in args:
            bi.grabProcedures("idapro", args["idb"])
        elif "r2" in args:
            bi.grabProcedures("radare2", args["r2"])
        else:
            bi.grabProcedures("radare2")
        
    if "proc" in args or savedproc:
        if savedproc:
            data = json.loads(saved)
        else:
            data = bi.processSingle(args["proc"])
            if data == None:
                printerr("procedure not found")
                exit(1)
        
        err = None
        if "save" not in args:
            err = get_token()
            if token:
                #TODO chech status code
                headers = {"Authorization": "Bearer " + token}
                try:
                    print(" >> Uploading to Carbonara...")
                    r = requests.post(CARBONARA_URL + "/api/procedure/update/", headers=headers, files={"report":json.dumps(data)})
                    if r.status_code != 200:
                        err = True
                except:
                    err = True
        if err or "save" in args:
            if err and err != True:
                printwarn(err)
            fname = os.path.basename(bi.filename) + "_" + hex(data["procedure"]["offset"]) + ".procedure.json"
            if err:
                printwarn("failed to upload to Carbonara, the output will be saved in a file (" + fname + ")")
            try:
                data = json.dumps(data, indent=2)
            except IOError as err:
                printerr(err)
                exit(1)
            outfile = open(fname, "w")
            outfile.write(data)
            outfile.close()
        else:
            print(" >> Successful upload")
    else:
        if "load" in args:
            data = json.loads(saved)
        else:
            data = bi.processAll()
        
        err = None
        if "save" not in args:
            err = get_token()
            if token:
                headers = {"Authorization": "Bearer " + token}
                binfile = open(bi.filename, "rb")
                try:
                    print(" >> Uploading to Carbonara...")
                    remain = []
                    if len(data["procs"]) > 16:
                        remain = data["procs"][16:]
                        data["procs"] = data["procs"][:16]
                    
                    r = requests.post(CARBONARA_URL + "/api/report/", headers=headers, files={
                        "binary":(os.path.basename(bi.filename), binfile.read()),
                        "report":json.dumps(data)
                        })
                    if r.status_code != 200:
                        print r.content
                        err = True
                    else:
                        while len(remain) > 0:
                            if len(remain) > 16:
                                remain = remain[16:]
                                data["procs"] = remain[:16]
                            else:
                                remain = []
                                data["procs"] = remain
                            
                            r = requests.post(CARBONARA_URL + "/api/procs-report/", headers=headers, files={
                            "report":json.dumps({
                                "md5": data["program"]["md5"],
                                "procs": data["procs"]
                                })
                            })
                            if r.status_code != 200:
                                print r.content
                                err = True
                                break
                            
                except:
                    err = True
                binfile.close()
        if err or "save" in args:
            if err and err != True:
                printwarn(err)
            fname = os.path.basename(bi.filename) + ".analysis.json"
            if err:
                printwarn("failed to upload to Carbonara, the output will be saved in a file (" + fname + ")")
            try:
                data = json.dumps(data, indent=2)
            except IOError as err:
                printerr(err)
                exit(1)
            outfile = open(fname, "w")
            outfile.write(data)
            outfile.close()
        else:
            print(" >> Successful upload")
    
    if "identify" in args:
        identify(bi)
    
    del bi  
    print " >> elapsed time: " + str(time.time() - start_time)


if __name__ == "__main__":
    main()

