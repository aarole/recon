# Recon script
An all-in-one recon script that can be useful for scanning and fuzzing machines.

## Features
* Port scanning
* Fuzzing web directories

## Dependencies
* Python3
* Nmap
* Requests

## Setup
* Downloading the files
```
git clone https://github.com/aarole/recon.git
cd recon/
```
* Installing requirements
```
pip install -r requirements.txt
```

## Usage
```
python recon.py -i 10.10.10.185 -n magic -w /home/user/hackthebox
```
