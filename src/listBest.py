from sklearn.externals import joblib
#import MeCab
import csv, time
from gensim import corpora, matutils, models
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
import json
from src import NounVerb

def main(sentence):
	model = joblib.load('./src/data/TRAIN_MODEL.sav')

	dictionary = corpora.Dictionary.load_from_text("./src/data/DICT.txt")
	tfidfModel = models.TfidfModel.load("./src/data/TF-IDF.model")


	#print("please sentence")
	#sentence = input()
	tupleData = dictionary.doc2bow(NounVerb.getNV(sentence))
	corpusTfIdf = [text for text in tfidfModel[tupleData]]
	vector      = matutils.corpus2dense([corpusTfIdf], num_terms=len(dictionary)).T
	nBest = model.predict_proba(vector)

	fiveBest =  sorted( [(v,i) for (i,v) in enumerate(nBest[0])], reverse=True)
	ansChar = ['5','a','b','c','d','e','f','g','h','i','j','m','o','p','u','w','x','y','z']
	result = []
	for row in fiveBest:
		result.append(ansChar[int(row[1])])

	return result




if __name__ == "__main__":
	main()
