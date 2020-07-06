# Python3-based web application directory & file fuzzer.
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

# Import required libraries
import argparse
import requests
import sys
import threading


# Create the Fuzzer class
class Fuzzer:
	# Define the constructor for the class
	def __init__(self,base,codes,extensions,output,dirs,threads):
		# Set all attributes using the arguments provided
		self.base = base
		self.codes = codes
		self.extensions = extensions
		self.output = output
		self.dirs = dirs
		self.threads = threads

		# Set the wordlist resume point to None
		self.resume = None

		# Append a / to the base URL if not provided
		if self.base[-1] != "/":
			self.base += "/"


	# Define the method to bruteforce the dir discovery
	def brute(self):
		# Execute the following block till the list of names is not empty
		while len(self.dirs):
			# Get the item at the front of the queue and create a list to brute it
			testdir = self.dirs[0]
			self.dirs.remove(testdir)
			testlist = list()

			# Test hidden files like (.htaccess and .htpasswd) without any extensions
			if testdir[0] != ".":
				# Append the item as a dir and as a file (using the extensions provided)
				testlist.append(f"{testdir}/")
				for ext in self.extensions:
					testlist.append(f"{testdir}.{ext}")

			# Attempt all items from the new list
			for attempt in testlist:
				# Append the item to the base URL
				testurl = self.base + attempt
				# Create a variable to store the response code
				code = 100

				# Try to make a GET request and store the code
				try:
					code = requests.get(testurl).status_code

					# If the code is acceptable, create a string containing the code and the attempt
					if code in self.codes:
						line = f"{code} -> {attempt}"
						# If -o flag is not used, print to STDOUT
						if self.output is None:
							print(line)
						# Else, write result to the specified file
						else:
							self.output.write(f"{line}\n")
				# Catch any exception and inform the user
				except Exception as e:
					print(f"Error ({attempt}): {str(e)}")


	# Define the start point for all objects of the class
	def run(self):
		# Spawn threads and start bruteforce discovery of dirs and files
		# Number of threads specified using the -t flag (if not present, default = 10)
		for _ in range(self.threads):
			new_thread = threading.Thread(target=self.brute,args=())
			new_thread.start()
		

# Define a method to parse command line arguments
def define_args():
	# Create a usage string
	usage_str = "python3 pyfuzz.py [-w /path/to/wordlist.txt (or) -n 100-1000] -u http://target.url:[port]/ [-o file] [-c 100,200,300] [-e xml,json]"
	
	# Create an ArgumentParser object
	parser = argparse.ArgumentParser(description="PyFuzz by Aditya Arole (@e1ora)",usage=usage_str)
	
	# Add required arguments
	parser.add_argument("-u","--url",dest="url",type=str,metavar="url",help="URL to fuzz; default port = 80")
	parser.add_argument("-w","--wordlist",dest="wordlist",type=str,metavar="wordlist",help="Path to wordlist text file")
	parser.add_argument("-o","--output",dest="output",type=str,metavar="output",help="Write results to a file; if not specified, results are printed to STDOUT")
	parser.add_argument("-c","--codes",dest="codes",type=str,metavar="codes",help="Acceptable return codes, comma separated (default list: 200,301,403)")
	parser.add_argument("-e","--extensions",dest="extensions",type=str,metavar="extensions",help="Acceptable file extensions, comma separated (default list: php,html,js,txt)")
	parser.add_argument("-t","--threads",dest="threads",type=int,metavar="threads",help="Number of threads (default: 10)")
	parser.add_argument("-n","--numeric",dest="numeric",type=str,metavar="num_range",help="Search for numeric in a certain range (format: -n 100-1000; disabled by default)")
	
	# Set defaults for the arguments
	parser.set_defaults(codes="200,301,403",extensions="php,html,js,txt",threads=10,numeric="")

	# If no arguments provided, print help message and exit
	if not len(sys.argv) > 1:
		parser.print_help()
		exit()
	
	# Return parsed arguments
	return parser.parse_args(sys.argv[1:])


# Define the driver function for the program
def main():
	# Get the command line arguments
	args = define_args()

	# Store the arguments in appropriate variables
	# Store acceptable codes as a list fo integers
	codes = args.codes.split(",")
	codes = [int(x) for x in codes]
	
	# Store the file extensions as a list of strings
	extn = args.extensions.split(",")
	
	# Store the output file
	out_file = args.output
	
	# Create a list to store the contents of the wordlist
	names = list()

	# Open the output file, if specified
	if out_file is None:
		pass
	else:
		out_file = open(out_file,"w")

	# If the -n flag is used, create a wordlist of numbers
	# Else, use the wordlist file
	lb, ub = 0, 0
	if len(args.numeric):
		# Split the argument and store the two values
		lb = int(args.numeric.split()[0])
		ub = int(args.numeric.split()[1]) + 1
		# Append the integers to the list as strings
		for i in range(lb, ub):
			names.append(str(i))
	else:
		# Open the wordlist file
		with open(args.wordlist, "r") as wordlist:
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

	# Create an instance of the Fuzzer class using the variables defined above
	fuzz = Fuzzer(args.url, codes, extn, out_file, names, args.threads)
	# Run the program
	fuzz.run()
		

# Execute the main function if the pyfuzz.py is run
if __name__ == "__main__":
	try:
		main()
	# Exit the program if a KeyboardInterrupt is received
	except KeyboardInterrupt:
		print("Interrupt received. Exiting.")
		sys.exit(0)
