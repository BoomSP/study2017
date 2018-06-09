from sklearn.externals import joblib
import MeCab
import csv, time
from gensim import corpora, matutils, models
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
import json

#-引数のtextをもとに各事由コードの尤度を算出し，良いスコアのコードを20件返す
#-辞書型
#-{
#-	"number1":{
#-		"code":$(CODE1),
#-		"proba":$(PROBA1)
#-	},
#-	"number2":{
#-		"code":$(CODE2),
#-		"proba":$(PROBA2)
#-	},
#-	...
#-}


def main(sentence):

	#-[/モデル・辞書ロード]
	model = joblib.load('./src/data/MODEL.sav')
	dictionary = corpora.Dictionary.load_from_text("./src/data/DICTIONARY.txt")
	tfidfModel = models.TfidfModel.load("./src/data/TF-IDF.model")
	#-[]

	#-[入力文書のベクトル化]
	tupleData = dictionary.doc2bow(getNV(sentence))
	corpusTfIdf = [text for text in tfidfModel[tupleData]]
	vector      = matutils.corpus2dense([corpusTfIdf], num_terms=len(dictionary)).T
	#-[]----------------------------


	predictData = model.predict_proba(vector)

	bestArray =  sorted( [(v,i) for (i,v) in enumerate(predictData[0])], reverse=True)

	f = open("./src/data/CODE.csv", "r")
	reader = csv.reader(f)
	for row in reader:codeList = row
	nLabel_proba = []
	nLabel = []
	for labelTuple in bestArray:
		nLabel_proba.append(labelTuple[0])
		nLabel.append(codeList[int(labelTuple[1])])

	resultDict = {}
	for i in range(0,20):
		resultDict["number"+str(i+1)] = {"code":nLabel[i], \
								"proba":str(int(nLabel_proba[i]*10000))}

	return resultDict

##[名詞動詞抽出関数]#######################################################
def getNV(sentence):
	mecab = MeCab.Tagger('mecabrc')
	mecab.parse('')
	node = mecab.parseToNode(sentence)
	node = node.next
	nounArr = []
	while node:
		if (node.feature.split(',')[0] in ['名詞', '動詞']):
			nounArr.append(node.surface)
			#print(node.surface)
		node = node.next
	return nounArr
######################################################################

if __name__ == "__main__":
	main("液晶")
