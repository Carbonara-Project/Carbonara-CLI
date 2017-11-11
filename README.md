# Carbonara-CLI
CLI client for Carbonara
Analyze a binary and send info to the Carbonara server.

## Install
We suggest you to use a virtualenv. 

### Linux
```
sudo apt install radare2 python python-pip
pip install -r requirements.txt
python setup.py install
```

### Windows
```
python -m pip install -r requirements.txt
python setup.py install
```

## Usage
```
python -m carbonara_cli [OPTIONS] <binary executable>
python -m carbonara_cli [OPTIONS] <binary executable> <IDA Pro database>
python -m carbonara_cli [OPTIONS] <binary executable> <radare2 project>
```
Options:
```
-radare2                Specify radare2 executable path
-idacmd <path>          Specify IDA Pro 32 executable (ida.exe) path
-ida64cmd <path>        Specify IDA Pro 64 executable (ida64.exe) path
-reconfig               Force configure file to be regenerated automatically
-writeconfig            Write custom paths (radare and IDA) to config file
```
