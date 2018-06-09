from gensim import corpora
import MeCab
import csv
from src import NounVerb

def main():
	f = open("./src/data/TRAIN_CORPUS.csv", "r")

	reader = csv.reader(f)

	array = []

	for row in reader:

		array.append(NounVerb.getNV(row[1]))

	corpusDict = corpora.Dictionary(array)
	corpusDict.filter_extremes(no_below=5, no_above=0.5)
	corpusDict.save_as_text("./src/data/DICTIONARY.txt")



if __name__ == "__main__" :
	main()
