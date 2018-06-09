# コード最大データ数最大2000件で新規コーパスを作る
# コードリストを作る。


import csv
import re
import mojimoji
import random

def main(fileList):

	#-[学習用コーパスファイル]
	f = open('./src/data/TRAIN_CORPUS.csv', 'w')
	writer = csv.writer(f)

	codeList = []
	codeText = []
	maxNum = 2000

	for fName in fileList :
		print(fName)
		f = open("./corpus/"+fName, 'r')
		reader = csv.reader(f)
		for row in reader :
			if (len(row[2]) != 0) :
				sentence = re.sub(r'.*　−　',"",row[1])
				sentence = mojimoji.zen_to_han(sentence, kana=False)
				sentence = sentence.lower()
				code     = mojimoji.zen_to_han(row[2][:3], kana=False).upper()
				if re.match(r'[A-Z0-9][0-9][0-9]',code) and (code not in codeList):
					codeList.append(code)
					codeText.append([sentence])
				else:
					for i in range(len(codeList)):
						if codeList[i] == code:
							codeText[i].append(sentence)

	for i in range(len(codeList)):
		if len(codeText[i]) > maxNum:
			sentenceList = random.sample(codeText[i], maxNum)
		else:
			sentenceList = codeText[i]
		for sentence in sentenceList:
			writer.writerow([sentence,codeList[i]])

	f = open('./src/data/CODE.csv', 'w')
	writer = csv.writer(f)
	writer.writerow(sorted(codeList))
