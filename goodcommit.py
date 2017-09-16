#!/usr/bin/env python

from __future__ import print_function
import os
import subprocess
import sys

localFile = []
remoteFile = []

watchList = dict()
diffList = dict()
reviewerList = []
reviewDetailList = []
testplanList = []
topdir = ''

def findWatchers(fileName):
	global topdir
	#print('findWatchers: ', topdir + '/' + fileName)
	fp = open(topdir + '/' + fileName)
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
					if listComment == []:
						continue
					if ("///" == listComment[0]) and (len(listComment) > 2):
						if "@testplan:" == listComment[1]:
							for item in listComment[2:]:
								testPlan.append(item)
					if ("///" == listComment[0]) and (len(listComment) == 2):
						if "@endwatch" == listComment[1]:
							break
				endLineNum = lineNum
				watchList[fileName].append(['watcher', watcherName, testPlan, startlineNum, endLineNum])
	#print(watchList)



def findDiffList(lines):

	global topdir
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

	if localFile == []:
		print('no different')
		sys.exit(0)
	
	print('checking ', localFile)

	for item in localFile:
		#print('local file :', item)
		findWatchers(item)

	#for item in remoteFile:
		#print('remote file:', item)

	#print('diffList =', diffList)


def findReviewerAndTestPlan():
	for fn in localFile:
		print('file', fn)
		for i, diffs in enumerate(diffList[fn]):
			print('\tdiff ', diffs)
			for j, watcher in enumerate(watchList[fn]):
				if (watcher[0] == 'author'):
					reviewerList.append(watcher[1])
					continue
				print('\t\tWatcher: ', watcher[3], watcher[4])
				checkrange = range(watcher[3], watcher[4])
				if (diffs[0] in checkrange) or (diffs[1] in checkrange):
					print('\t\t\tmatched')
					reviewerList.append(watcher[1][0])
					testplanList.append(watcher[2][0])

def parseGitBlame():

	for file in remoteFile:
		#print('execute git blame', file)
		global topdir
		blameOutput = subprocess.check_output(['git', 'blame', '-f', topdir + '/' + file])
		#print(blame)
		blamLines = blameOutput.splitlines()
		lastReviewInfo = []
		for item in diffList[file]:
			for line in range(item[0], item[1]):
				#print(blamLines[line])
				commitId = blamLines[line].split()[0]
				author = blamLines[line].split()[2].lstrip('(')
				if commitId != '00000000':
					#print('blame ', commitId, ' ', author)
					reviewerList.append(author)
					reviewinfo = [author, file, commitId, [item[0], item[1]]]
					if (lastReviewInfo != reviewinfo):
						reviewDetailList.append(reviewinfo)
					lastReviewInfo = reviewinfo



def main():

	from optparse import OptionParser

	
	parser = OptionParser()
	parser.add_option("-b", "--blame",
					action="store_true", dest="blame", default=False,
					help="run git blame to find the reviewer")
	parser.add_option("-d", "--detail",
					action="store_true", dest="detail", default=False,
					help="print details")

	(options, args) = parser.parse_args()
	

	global topdir
	
	try:
		diff_output = subprocess.check_output(['git', 'diff', '--staged'])
	except:
		print('error to execute')
		sys.exit(0)

	topdir = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).strip('\n')
	print('top dir', topdir)
	diff_lines = diff_output.splitlines()
	findDiffList(diff_lines)
	findReviewerAndTestPlan()
	
	if options.blame == True:
		parseGitBlame()
	
	
	print('\n\n------------ result ------------');
	
	if options.detail == True:
		print('reviews detail: ')
		for name in reviewDetailList:
			print('\t', name)
			logs = subprocess.check_output(['git', 'log', '-1', name[2]])
			#print(logs)
			logs = logs.splitlines()
			print('\t\t', logs[4])
	
	print('reviewer : ')
	for name in set(reviewerList):
		print('\t', name)

		
	print('test plan: ')
	for name in set(testplanList):
		print('\t', name)
	#print(diff_output)
main()
