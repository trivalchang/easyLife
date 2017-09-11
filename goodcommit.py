#!/usr/bin/env python

from __future__ import print_function
import os
import subprocess

localFile = []
remoteFile = []

watchList = dict()
diffList = dict()

def findWatchers(fileName):
	fp = open(fileName)
	watchList[fileName] = []
	lineNum = 0
	for line in fp:
		lineNum += 1
		if line.split() == []:
			continue
		listComment = line.split()
		if ("///" == listComment[0]) and (len(listComment) > 2):
			if "@author:" == listComment[1]:
				#print('author', line)
				watchList[fileName].append(['author', listComment[2]])
			if "@watcher:" == listComment[1]:
				watcherName = [listComment[2]]
				startlineNum = lineNum
				testPlan = []
				for line in fp:
					lineNum += 1
					listComment = line.split()
					if ("///" == listComment[0]) and (len(listComment) > 2):
						if "@testplan:" == listComment[1]:
							testPlan.append(listComment[2])
					if ("///" == listComment[0]) and (len(listComment) == 2):
						if "@endwatch" == listComment[1]:
							break
				endLineNum = lineNum
				watchList[fileName].append(['watcher', watcherName, testPlan, startlineNum, endLineNum])
	print(watchList)



def findDiffFile(lines):

	for line in lines:
		#print(line)
		diffs = line.split()
		if diffs == []:
			continue
		if 'diff' == diffs[0]:
			local = diffs[2][2:]
			remote = diffs[3][2:]

			localFile.append(diffs[2][2:])
			remoteFile.append(diffs[3][2:])
			diffList[local] = []
			continue
		
		if '@@' == diffs[0]:
			num = map(int, diffs[1].lstrip('-').split(','))
			num[1] += num[0]
			diffList[local].append(num)



	for item in localFile:
		#print('local file :', item)
		findWatchers(item)

	for item in remoteFile:
		print('remote file:', item)

	print('diffList =', diffList)



def parseGitBlame():

	for file in remoteFile:
		blame = subprocess.check_output(['git', 'blame', file])
		#print(blame)



def main():
	print('it is a test2')

	cmd = 'git diff'
	#diff_output = os.system(cmd)
	#findDiffFile(diff_output)
	try:
		diff_output = subprocess.check_output(['git', 'diff', '--staged'])
	except:
		print('error to execute')
	diff_lines = diff_output.splitlines()
	findDiffFile(diff_lines)
	parseGitBlame()
	#print(diff_output)
main()
