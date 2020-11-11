import glob
import os
import json


print('note: this routine must run in a directory where the only .txt files are the files to be parsed')
# generate congregated data file from raw

objs = []

order_files = glob.glob(os.getcwd() + "/*.txt")
for i, file_name in enumerate(order_files):
	with open('temp.txt', "w") as clean_file:
		with open(file_name, "r") as file:
			print('parsing: ' + file_name)
			for line in file:
				line = list(line)
				if len(line) < 3:
					clean_file.write("".join(line))
					continue
				if line[-2] == ' ' and line[-3] == '.':
					line[-3] = ','
					line[-2] = '\n'
				line = "".join([el if el != '=' else ':' for el in line])
				clean_file.write(line)
	with open('temp.txt', "r") as clean_file:
		temp = json.loads(clean_file.read())
		respFormatted = json.dumps(temp, indent=4, separators=(",", ":"))
		objs.append(respFormatted)
print('finished parsing')
print('writing clean proper format to master...')
with open("master_orders.txt", "w") as master:
	for obj in objs:
		master.write(obj)
print('cleanup...')
os.remove('temp.txt')
print('done!')