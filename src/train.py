
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import cross_val_score
import csv
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import make_scorer, f1_score, accuracy_score, precision_score, recall_score
import numpy as np
import MeCab
from gensim import corpora, matutils, models
from sklearn.externals import joblib
from src import NounVerb

import time

def main():

	vector = []
	code   = []

	start = time.time()
###############################################
	f = open("./src/data/TRAIN_CORPUS.csv","r")
	reader = csv.reader(f)
	array = []
	for row in reader: array.append(NounVerb.getNV(row[0]))
	dictionary = corpora.Dictionary(array)
	dictionary.filter_extremes(no_below=50, no_above=0.5)
	dictionary.save_as_text("./src/data/DICTIONARY.txt")
###############################################

	f = open("./src/data/TRAIN_CORPUS.csv","r")
	reader = csv.reader(f)
	tupleData = []
	for row in reader:
		rowTuple = dictionary.doc2bow(NounVerb.getNV(row[0]))
		tupleData.append(rowTuple)
	tfidfModel  = models.TfidfModel(tupleData)
	tfidfModel.save("./src/data/TF-IDF.model")

###############################################
	#ベクトル生成
	vector = []
	code = []

	f = open("./src/data/TRAIN_CORPUS.csv","r")
	reader = csv.reader(f)
	for row in reader:
		tupleData = dictionary.doc2bow(NounVerb.getNV(row[0]))
		corpusTfIdf = [text for text in tfidfModel[tupleData]]
		vec      = matutils.corpus2dense([corpusTfIdf], num_terms=len(dictionary)).T[0]
		vector.append(vec)
		code.append(row[1])

	#分類先生成
	f = open("./src/data/CODE.csv", "r")
	reader = csv.reader(f)
	for row in reader:
		codeList = row

###############################################

	model = MultinomialNB(alpha=0.25)
	model.partial_fit(vector, code, codeList)
	joblib.dump(model, "./src/data/MODEL.sav")

###############################################

	end = time.time() - start

	return str(int(end*10))		#[戻り値]学習所要時間


if __name__=='__main__':
	main()
