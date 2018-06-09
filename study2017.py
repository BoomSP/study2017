from flask import Flask, render_template, jsonify, request
from flask_sockets import Sockets

import json, glob, csv, os, re
from time import sleep
from datetime import datetime
from src import train, predict, csvPrepare, genDictionary
import time
from collections import OrderedDict


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False												#日本語文字化け対策
app.config["JSON_SORT_KEYS"] = False 											#jsonデータのソートを無効
sockets = Sockets(app)

#[モデルバインディング]#############################################################

#-[APIバインディング]-------------------------------------------------------------#
@app.route('/api/predict')
def predictApi():																#httpを用いたコードの推定

	text = request.args.get('text')												#パラメータ取得 ?text=$(TEXT)
	if text is None: text = request.form["text"]

	if text is not None:														#推定可能
		result = predict.main(text)
		return jsonify(status="200 Success",text=text, result=result)

	else :
		return jsonify(status="400 Bad Request")								#パラメータ不良[失敗]

@app.route('/api/add')
def uploadApi():

	text = request.args.get('text')												#パラメータ取得 ?text=$(TEXT)
	if text is None: text = request.form["text"]
	code = request.args.get('code')												#パラメータ取得 &code=$(CODE) 英数字3文字
	if code is None: code = request.form["code"]


	if (text is not None) and (code is not None):

		if not re.match(r"^[A-Z0-9][0-9]{2}$", code):
			return jsonify(status="400 Bad Request.",\
				message="故障事由コード：「A-Zまたは0の接頭1字と2桁の数字」（半角英数字3字）")

		#-[csvへの追加]----------------------------------------------------------#
		touchCSV()																#追加先ファイルの確認

		date = datetime.now().strftime('%y%m%d')
		number = len(open("./corpus/corpus"+date+".csv").readlines())

		f = open("./corpus/corpus"+date+".csv", 'a')
		writer = csv.writer(f)
		writer.writerow([str(number+1), text, code])
		#-----------------------------------------------------------------------#

		info = {"datetime":datetime.now().strftime('%Y/%m/%d %H:%M:%S'),\
				"fileName":"corpus"+date+".csv", "dataNum":str(number)}			#データ追加に関する情報[追加日時, 追加ファイル名, ファイル内データ番号]
		data = {"text":text, "code":code}										#追加したデータ[故障情報,故障事由コード]

		return jsonify(status="200 Success",additionData=data, info=info)		#追加成功

	else:
		return jsonify(status="400 Bad Request")								#パラメータ不良[失敗]
#-------------------------------------------------------------------------------#

#-[Webページバインディング]--------------------------------------------------------#
@app.route('/')																	#トップページ
def index():
	return render_template('index.html')

@app.route('/api_usage')															#【済】故障事由コード推定ページ
def api_usage_page():
	return render_template('api_usage.html')


@app.route('/predict')															#【済】故障事由コード推定ページ
def predict_page():
	return render_template('predict.html')

@app.route('/add')																#【済】コーパス追加ページ
def add_page():
	return render_template('add.html')

@app.route('/edit/')															#コーパス編集ページ
def edit_page():
	return render_template('edit.html')

@app.route('/edit/<fileDate>')													#コーパス編集ページ
def edit_page_parse(fileDate):
	return render_template('edit.html')
#-------------------------------------------------------------------------------#

#################################################################################


@sockets.route('/')			# 機械学習を実行
def index_socket(ws):

	#-[学習モデル最終更新日時取得]--------------------------------------------------#
	f = open("./data/lastDate.sav","r")
	data = f.readlines()
	#---------------------------------------------------------------------------#
	csvList = data[1].split(",")

	result = {"date":data[0],"time":data[2],"fList":csvList}

	ws.send(json.dumps(result, ensure_ascii=False))

@sockets.route('/learn')	#機械学習を実行
def learn_socket(ws):
	while not ws.closed:
		trainConf = ws.receive()
		if trainConf is not None:

			#-[前学習データ消去]--------------------------------------------------#
			tmpF = glob.glob("./src/data/*")
			for tmpf in tmpF:
				os.remove(tmpf)
			fileList= trainConf.split(',')
			#-------------------------------------------------------------------#

			#-[機械学習]---------------------------------------------------------#
			csvPrepare.main(fileList)	#前処理
			totalTime = train.main()				#学習
			#-------------------------------------------------------------------#

			#-[学習詳細保存]------------------------------------------------------#
			f = open("./data/lastDate.sav","w")
			date = datetime.now().strftime('%y%m%d%H%M')
			date = "20"+date[0:2]+"年"+date[2:4]+"月"+date[4:6]+"日"+date[6:8]+"時"+date[8:10]+"分\n"
			f.write(date)
			fListStr = ""
			for fName in fileList:
				fListStr += fName+","
			f.write(fListStr[:-1]+"\n")
			f.write(totalTime[:-1]+"."+totalTime[-1]+"\n")
			#-------------------------------------------------------------------#
			#sleep(5)
			ws.send("SUCCESS")


@sockets.route('/predict')	#【済】
def predict_socket(ws):
	while not ws.closed:
		text = ws.receive()														#ソケットメッセージ取得
		predictDict = predict.main(text)												#

		for i in range(0,20):
			f = open("./data/CODE_TEXT.csv", 'r')
			reader = csv.reader(f)
			for row in reader:
				if row[0] == predictDict["number"+str(i+1)]["code"] :
					predictDict["number"+str(i+1)]["codeText"]= row[1]

		ws.send(json.dumps(predictDict))												#

@sockets.route('/corpusToday')	#【済】
def corpusToday_socket(ws):
		date = datetime.now().strftime('%y%m%d')
		fname = "./corpus/corpus"+date+".csv"

		#-[csvDict作成]------------------------------------------------------#
		touchCSV()

		csvDict = OrderedDict()
		i=1
		f = open(fname, 'r')
		reader = csv.reader(f)
		for row in reader:
			csvDict[str(i)] = {"id":row[0],  "text":row[1], "code":row[2] }
			i+=1
		#-------------------------------------------------------------------#

		result = {"date":date,"csvData":csvDict}

		ws.send(json.dumps(result, ensure_ascii=False))

@sockets.route('/add') #【済】
def add_socket(ws):
	while not ws.closed:
		data = ws.receive()
		if data is not None:
			data = data.split(',')												#[text, code]
			date = datetime.now().strftime('%y%m%d')
			fname = "./corpus/corpus"+date+".csv"

			#-[csvへの追加]------------------------------------------------------#
			touchCSV()															#追加先ファイルの確認

			number = len(open(fname).readlines())

			f = open(fname, 'a')
			writer = csv.writer(f)
			writer.writerow([str(number+1), data[0], data[1]])
			#-------------------------------------------------------------------#

			#-[csvDict作成]------------------------------------------------------#
			csvDict = OrderedDict()
			i=1
			f = open(fname, 'r')
			reader = csv.reader(f)
			for row in reader:
				csvDict[str(i)] = {"id":row[0],  "text":row[1], "code":row[2] }
				i+=1
			#-------------------------------------------------------------------#

			result = {"date":date,"csvData":csvDict}

			ws.send(json.dumps(result, ensure_ascii=False))

@sockets.route('/update') #【済】
def update_socket(ws):
		data = ws.receive()														#[date, id, text, code]
		if data is not None:
			data = data.split(',')
			fname = "./corpus/corpus"+data[0]+".csv"

			#-[更新およびcsvDict作成]---------------------------------------------//
			csvDict = OrderedDict()
			i=1
			f = open(fname, 'r')
			reader = csv.reader(f)
			for row in reader:
				if str(row[0]) == data[1]:
					csvDict[str(i)] = {"id":data[1], "text":data[2],"code":data[3]}
				else:
					csvDict[str(i)] = {"id":row[0],  "text":row[1], "code":row[2] }
				i+=1
			#-------------------------------------------------------------------#

			#-[実csvデータへの書き込み]--------------------------------------------#
			f = open(fname, 'w')
			writer = csv.writer(f)
			for val in csvDict.values():
				writer.writerow([val["id"],val["text"],val["code"]])
			#-------------------------------------------------------------------#

			result = {"date":data[0],"csvData":csvDict}

			ws.send(json.dumps(result, ensure_ascii=False))

@sockets.route('/delete') #【済】
def delete_socket(ws):
		data = ws.receive()
		if data is not None:
			data = data.split(',')
			fname = "./corpus/corpus"+data[0]+".csv"

			#-[削除およびcsvDic作成]-----------------------------------------------#
			csvDict = OrderedDict()
			i=1
			f = open(fname, 'r')
			reader = csv.reader(f)
			for row in reader:
				if str(row[0]) != data[1]:
					csvDict[str(i)] = {"id":str(i), "text":row[1], "code":row[2]}
					i+=1
			#-------------------------------------------------------------------#

			#-[実csvデータへの書き込み]--------------------------------------------#
			f = open(fname, 'w')
			writer = csv.writer(f)
			for val in csvDict.values():
				writer.writerow([val["id"],val["text"],val["code"]])
			#-------------------------------------------------------------------#

			result = {"date":data[0],"csvData":csvDict}

			ws.send(json.dumps(result, ensure_ascii=False))

#-[コーパス]
@sockets.route('/corpusList')	#コーパスリストを取得
def corpusList_socket(ws):
		fList = glob.glob('./corpus/corpus*.csv')
		fList.sort()

		csvListDict = OrderedDict()
		i=1
		for row in fList:
			num = len(open(row).readlines())
			fDate = row.replace("./corpus/corpus","").replace(".csv","")
			csvListDict[str(i)] = {"fDate":fDate, "dataNum":str(num)}
			i+=1

		fList = glob.glob('./corpus/DEFAULT*.csv')
		fList.sort()
		defListDict = OrderedDict()
		i=1
		for row in fList:
			num = len(open(row).readlines())
			fDate = row.replace("./corpus/DEFAULT","").replace(".csv","")
			defListDict[str(i)] = {"fDate":fDate, "dataNum":str(num)}
			i+=1


		result = {"csvList":csvListDict, "defList":defListDict}

		ws.send(json.dumps(result, ensure_ascii=False))

@sockets.route('/corpusParse')	#その日のコーパスを取得
def corpusParse_socket(ws):
	data = ws.receive()
	print(data)
	if data is not None:														#data:パースするファイル名
		fname = "./corpus/corpus"+data+".csv"
		if not os.path.exists(fname):
			ws.send(json.dumps({"status":"ERROR"}, ensure_ascii=False))

		date = data

		#-[csvDict作成]------------------------------------------------------#
		csvDict = OrderedDict()
		i=1
		f = open(fname, 'r')
		reader = csv.reader(f)
		for row in reader:
			csvDict[str(i)] = {"id":row[0],  "text":row[1], "code":row[2] }
			i+=1
		#-------------------------------------------------------------------#

		result = {"status":"SUCCESS","date":date,"csvData":csvDict}

		ws.send(json.dumps(result, ensure_ascii=False))



def touchCSV():																	#今日のcsvファイルがない場合作成
	date = datetime.now().strftime('%y%m%d')
	fname = "./corpus/corpus"+date+".csv"
	if not os.path.exists(fname) :
		f = open(fname, 'a')
		return False															#ファイルなし(空csv作成)
	else:
		return True																#ファイルあり

if __name__ == '__main__':
	app.run(debug=True)
