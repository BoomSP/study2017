from janome.tokenizer import Tokenizer
#import MeCab

#def getNV(sentence):
#	mecab = MeCab.Tagger('mecabrc')
#	mecab.parse('')
#	node = mecab.parseToNode(sentence)
#	node = node.next
#	while node:
#		if (node.feature.split(',')[0] in ['名詞', '動詞']):
#			nounArr.append(node.surface)
#			#print(node.surface)
#		node = node.next
#	return nounArr

def getNV(sentence):
	t = Tokenizer()
	nounArr = []
	for token in t.tokenize(sentence):
		if token.part_of_speech.split(',')[0] in ["名詞", "動詞"]:
			nounArr.append(token.surface)
	return nounArr

if __name__ == "__main__":
	while(True):
		sentence = input()
		print(getNV(sentence))
