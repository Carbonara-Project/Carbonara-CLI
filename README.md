# Carbonara-CLI
CLI client for Carbonara
Analyze a binary and send info to the Carbonara server.

## Install
You can install carbonara_cli from pip or directly from this repo.
We suggest you to use a virtualenv. 

### From pip

```
python -m pip install carbonara_cli
```

### From Github repo

#### Linux
```
sudo apt install git python python-pip
git clone https://github.com/Carbonara-Project/Carbonara-CLI.git
cd Carbonara-CLI
pip install -r requirements.txt
python setup.py install
```

#### Windows
```
git clone https://github.com/Carbonara-Project/Carbonara-CLI.git
cd Carbonara-CLI
python -m pip install -r requirements.txt
python setup.py install
```

## Usage
    
You can use the `carb` script if it is in path or invoke it directly as python module with `python -m carbonara_cli`

```
carb [OPTIONS] <binary executable>
carb [OPTIONS] <binary executable> <IDA Pro database>
carb [OPTIONS] <binary executable> <radare2 project>
```
Options:
```
-h, --help              Show the help
-e, --exists            Know if the binary is already in the Carbonara database
-p, --proc <name>       Analyze and upload only a specified procedure
-s, --save              Save the json report as a file instead of uploading it to Carbonara
-l, --load <path>       Load a json report from the filesystem instead of analyzing the target binary
-i, --identify          Get a list of binaries (md5) that have procedures in common with the target
-a, --arch <name>       Specify by hand the architecture of the binary (useful for blobs)
-b, --bits <32/64>      Specify by hand the bits of the binary (useful for blobs)

-r2proj <path>          Specify the radare2 project to use
-idb <path>             Specify the IDA Pro database to use

-radare2                Specify radare2 executable path
-idacmd <path>          Specify IDA Pro 32 executable (ida.exe) path
-ida64cmd <path>        Specify IDA Pro 64 executable (ida64.exe) path
-reconfig               Force configure file to be regenerated automatically
-writeconfig            Write custom paths (radare and IDA) to config file
```

## Demo

[![asciicast](https://asciinema.org/a/ECF81EJuVWtGCqkw69sZHL3Zi.png)](https://asciinema.org/a/ECF81EJuVWtGCqkw69sZHL3Zi)
