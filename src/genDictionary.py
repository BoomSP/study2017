from gensim import corpora
import MeCab
import csv

def main():
	f = open("./src/data/TRAIN_CORPUS.csv", "r")

	reader = csv.reader(f)

	array = []

	for row in reader:

		array.append(getNoun(row[1]))

	corpusDict = corpora.Dictionary(array)
	corpusDict.filter_extremes(no_below=5, no_above=0.5)
	corpusDict.save_as_text("./src/data/DICTIONARY.txt")


def getNoun(sentence):
	mecab = MeCab.Tagger('mecabrc')
	mecab.parse('')
	node = mecab.parseToNode(sentence)
	node = node.next
	nounArr = []
	while node:
		if (node.feature.split(',')[0] == '名詞'):
			nounArr.append(node.surface)
			#print(node.surface)
		node = node.next
	return nounArr


if __name__ == "__main__" :
	main()
