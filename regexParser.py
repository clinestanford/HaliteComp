import re
import sys

def print_the_total(bot, data):
	string = bot + ', came in rank #(\d)'
	needle = re.compile(string)
	result = needle.findall(data)
	runningTotal = 0
	for match in result:
		runningTotal += int(match)
	print(bot, runningTotal)


firstBot = sys.argv[1]
secondBot = sys.argv[2]
thirdBot = sys.argv[3]
fourthBot = sys.argv[4]


with open('regexText.txt', 'r') as myfile:
	data=myfile.read().replace('\n', '')
	print_the_total(firstBot[:-3], data)
	print_the_total(secondBot[:-3], data)
	print_the_total(thirdBot[:-3], data)
	print_the_total(fourthBot[:-3], data)