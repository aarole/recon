# Python3-based recon script that automates the process of port scanning and fuzzing.
# Copyright (C) 2020  Aditya Arole

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import nmap
import os
import pyfuzz
import sys
import threading


class Machine:
	def __init__(self, ip, name, dir):
		self.ip = ip
		self.name = name
		self.base_dir = os.getcwd()
		self.dir = f"{dir}/{name}"

		try:
			os.mkdir(self.dir)
		except FileExistsError:
			pass
		os.chdir(self.dir)

		self.port_scan(1024)

	
	def port_scan(self, upper_bound):
		scanner = nmap.PortScanner()
		ports_to_scan = f"1-{upper_bound}"
		
		scanner.scan(self.ip, ports=ports_to_scan, arguments="-sC -sV")

		base_dict = scanner._scan_result['scan'][self.ip]['tcp']

		with open(f"{self.name}.nmapout", "w") as outfile:
			for port in base_dict.keys():
				outfile.write(f"Port: {port}\n")
				for detail in base_dict[port].keys():
					outfile.write(f" {detail}: ")
					test_var = base_dict[port][detail]
					
					if type(test_var) is not dict:
						outfile.write(f"{test_var}\n")
					else:
						for key in test_var.keys():
							outfile.write(f"\n  {key}: ")
							if test_var[key].count("\n") > 0:
								outfile.write(f"{test_var[key]}")
							else:
								outfile.write(f"{test_var[key]}")
				outfile.write("\n\n")

		web_ports = [80, 443, 8080, 8443]

		for port in web_ports:
			if scanner[self.ip].has_tcp(port):
				threading.Thread(target=self.fuzz_web_server, args=(port,)).start()

	
	def fuzz_web_server(self, port):
		url = f"http://{self.ip}:{port}/"
		
		names = list()
		# Open the wordlist file
		with open(f"{self.base_dir}/dirs.txt", "r") as wordlist:
			# Read the lines from the wordlist
			lines = wordlist.readlines()

			# Iterate over the lines
			for line in lines:
				# Strip the line
				line = line.strip()

				# If the line is neither a comment nor empty,
				# append the contents to the list of names
				if line[0:1] == "#" or len(line) == 0:
					continue
				else:
					names.append(line)
		
		fuzzer = pyfuzz.Fuzzer(base=url,codes=[200,301,403],extensions=["php","html","js","txt"],output=open(f"{self.name}.fuzzout", "w"),dirs=names,threads=10)
		fuzzer.run()


# Create a method to get the arguments from the command line
def define_args():
	# Define the usage string
	usage_str = """python3 recon.py -i/--ip MACHINE_IP -n/--name MACHINE_NAME -w/--working-directory WORKING_DIRECTORY
	Example: python3 recon.py -i 10.10.10.191 -n Blunder -w /home/user/htb"""
	# Create an ArgumentParser object
	parser = argparse.ArgumentParser(description="Recon script by Aditya Arole (@e1ora)",usage=usage_str)
	# Add the -i, -n and -w arguments
	parser.add_argument("-i","--ip",dest="ip",type=str,metavar="IP",help="IP address of the target machine")
	parser.add_argument("-n","--name",dest="name",type=str,metavar="NAME",help="Name of the target machine")
	parser.add_argument("-w","--working-directory",dest="wd",type=str,metavar="WORKING_DIRECTORY",help="Path to working directory (files will be stored in a subdirectory here)")
	#parser.add_argument("-l","--wordlist",dest="wordlist",type=str,metavar="WORDLIST",help="Wordlist to use while fuzzing")

	# If no arguments are provided, print the help message and exit
	if not len(sys.argv) > 1:
		parser.print_help()
		exit()
	
	# Return the command line arguments
	return parser.parse_args(sys.argv[1:])


def main():
	args = define_args()

	Machine(args.ip, args.name, args.wd)


if __name__ == "__main__":
	main()
