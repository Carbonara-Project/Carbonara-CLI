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

CARBONARA_URL = "https://carbonara-backend.herokuapp.com"

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
            "client_id": "lhMcNHozKwZIrzoKdnJbozgXGsxKEcxs2hB0cvON",
            "grant_type": "password",
            "username": username,
            "password": password
        }
        try:
            r = requests.post(CARBONARA_URL + "/users/auth/token", data=auth_body)
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
        print LMAG_BG + "  usage  " + NC + " python carbonara-cli.py [OPTIONS] <binary file> "
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
    
    try:
        if r2plugin and binary == None:
            bi = BinaryInfo(R2PLUGIN)
        else:
            bi = BinaryInfo(binary)
    except IOError as err:
        printerr(err)
        exit(1)
    
    if "exists" in args:
        err = get_token()
        if err:
            printerr(err)
            exit(1)
        
        headers = {"Authorization": "Bearer " + token}
        try:
            r = requests.head(CARBONARA_URL + "/api/program/?md5=" + bi.md5, headers=headers)
        except:
            printerr("failed to connect to Carbonara")
            exit(1)
        if r.status_code == 404:
            print LCYAN + " >> The binary is not present in the Carbonara server." + NC
        elif r.status_code == 200:
            print LCYAN + " >> Result: " + CARBONARA_URL + "" + NC
        else:
            printerr("invalid response")
            exit(1)
        exit(0)
    
    if "proc" not in args:
        bi.addAdditionalInfo()
        bi.addStrings()
    
    if "idb" in args:
        bi.grabProcedures("idapro", args["idb"])
    elif "r2" in args:
        bi.grabProcedures("radare2", args["r2"])
    else:
        bi.grabProcedures("radare2")
    
    if "proc" in args:
        pdata = bi.processSingle(args["proc"])
        if pdata == None:
            printerr("procedure not found")
            exit(1)
        try:
            data = json.dumps(pdata, indent=2)
        except IOError as err:
            printerr(err)
            exit(1)
        
        err = get_token()
        if token:
            #TODO chech status code
            headers = {"Authorization": "Bearer " + token}
            try:
                r = requests.post(CARBONARA_URL + "/api/procedure/update", headers=headers)
            except:
                err = True
        if err:
            if err != True:
                printwarn(err)
            fname = os.path.basename(bi.filename) + "_" + hex(pdata["procedure"]["offset"]) + ".procedure.json"
            printwarn("failed to connect to Carbonara, the output will be saved in a file (" + fname + ")")
            outfile = open(fname, "w")
            outfile.write(data)
            outfile.close()
    else:
        try:
            data = json.dumps(bi.processAll(), indent=2)
        except IOError as err:
            printerr(err)
            exit(1)
        
        err = get_token()
        if token:
            headers = {"Authorization": "Bearer " + token}
            try:
                r = requests.post(CARBONARA_URL + "/api/report", headers=headers)
            except:
                err = True
        if err:
            if err != True:
                printwarn(err)
            fname = os.path.basename(bi.filename) + ".analysis.json"
            printwarn("failed to connect to Carbonara, the output will be saved in a file (" + fname + ")")
            outfile = open(fname, "w")
            outfile.write(data)
            outfile.close()
    
    print " >> elapsed time: " + str(time.time() - start_time)


if __name__ == "__main__":
    main()

