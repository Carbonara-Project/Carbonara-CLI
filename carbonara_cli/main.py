import sys
import time
import requests
import progressbar
from guanciale import *

def main():
    if len(sys.argv) < 2 or sys.argv[1] == "-help":
        print "usage: python carbonara-cli.py [OPTIONS] <binary file>"
        print
        exit(0)

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

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-r2proj":
            if i == len(sys.argv) -1:
                print "error: arg '-r2proj': expected one argument"
                print "ABORT"
                exit(1)
            if hasdb:
                print "error: arg '%s': disassembly database specified yet, ignored" % sys.argv[i+1]
                continue
            args["r2"] = sys.argv[i+1]
            hasdb = True
            i += 1
        elif sys.argv[i] == "-idb":
            if i == len(sys.argv) -1:
                print "error: arg '-idb': expected one argument"
                print "ABORT"
                exit(1)
            if hasdb:
                print "error: arg '%s': disassembly database specified yet, ignored" % sys.argv[i+1]
                continue
            hasdb = True
            args["idb"] = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == "-idacmd":
            if i == len(sys.argv) -1:
                print "error: arg '-idacmd': expected one argument"
                print "ABORT"
                exit(1)
            config.idacmd = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == "-ida64cmd":
            if i == len(sys.argv) -1:
                print "error: arg '-ida64cmd': expected one argument"
                print "ABORT"
                exit(1)
            config.ida64cmd = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == "-radare2":
            if i == len(sys.argv) -1:
                print "error: arg '-radare2': expected one argument"
                print "ABORT"
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
            print "error: arg '%s': disassembly database specified yet, ignored" % sys.argv[i]
        else:
            dbfile = sys.argv[i]
            ext = os.path.splitext(dbfile)[-1]
            if ext == "idb" or ext == "i64":
                args["idb"] = dbfile
            else:
                print "message: no project type info, Radare2 assumed"
                args["r2"] = dbfile
        i += 1

    if binary == None:
        print "error: binary file not provided"
        print "ABORT"
        exit(1)

    start_time = time.time()

    try:
        bi = BinaryInfo(binary)
    except IOError as err:
        print "error: %s" % err
        print "ABORT"
        exit(1)
    if "idb" in args:
        bi.fromIdb(args["idb"])
    elif "r2" in args:
        bi.fromR2Project(args["r2"])
    else:
        bi.generateInfo()
    data = bi.toJson()

    outfile = open(os.path.basename(sys.argv[1]) + ".analisys.json", "w")
    outfile.write(data)
    outfile.close()

    print
    print "elapsed time: " + str(time.time() - start_time)


if __name__ == "__main__":
    main()

