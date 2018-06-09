import csv
import re
import mojimoji

def main(fileList):

	f = open('./src/data/TRAIN_CORPUS.csv', 'w')
	writer = csv.writer(f)

	for fName in fileList :
		print(fName)
		f = open("./corpus/"+fName, 'r')
		reader = csv.reader(f)
		for row in reader :
			if len(row[2]) != 0:
				sentence = re.sub(r'.*　−　',"",row[1])
				sentence = mojimoji.zen_to_han(sentence, kana=False)
				sentence = sentence.lower()
				codeChar = mojimoji.zen_to_han(row[2], kana=False).upper()

				writeRow = [sentence, codeChar]
				writer.writerow(writeRow)


if __name__ == "__main__" :
	main(['./data/testFlask001.csv', './data/testFlask002.csv'])
