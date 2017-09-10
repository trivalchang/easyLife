#!/usr/bin/env python

from __future__ import print_function
import os
import subprocess

localFile = []
remoteFile = []

diffContent = dict()

def findWatchers(fileName):
	fp = open(fileName)
	diffContent[fileName] = []
	lineNum = 0
	for line in fp:
		lineNum += 1
		if line.split() == []:
			continue
		listComment = line.split()
		if ("///" == listComment[0]) and (len(listComment) > 2):
			if "@author:" == listComment[1]:
				#print('author', line)
				diffContent[fileName].append(['author', listComment[2]])
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
							endLineNum = lineNum
							break
				diffContent[fileName].append(['watcher', watcherName, testPlan, startlineNum, endLineNum])


def findDiffFile(lines):

	for line in lines:
		if 'diff' in line:
			#print(line)
			if 'diff' == line.split()[0]:
				print(line.split()[0])
				local = line.split()[2].lstrip('a/')
				remote = line.split()[3].lstrip('b/')
				localFile.append(line.split()[2].lstrip('a/'))
				remoteFile.append(line.split()[3].lstrip('b/'))



	for item in localFile:
		print('local file :', item)
		findWatchers(item)

	for item in remoteFile:
		print('remote file:', item)




def parseGitBlame():

	for file in remoteFile:
		blame = subprocess.check_output(['git', 'blame', file])
		print(blame)



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
