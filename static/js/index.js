var host = "ws://"+document.domain+':'+location.port+"/";
var socket = new WebSocket(host);
var corpusListHost = "ws://"+document.domain+':'+location.port+"/corpusList";
var corpusListSocket = new WebSocket(corpusListHost);



$(function(){

	socket.onmessage = function(message){
		var obj = JSON.parse(message.data)
		$("#lastLearn").empty();
		$("#lastLearn").append("<br>前回の更新日時："+obj.date+"<br>")
		$("#lastLearn").append("前回の学習所要時間： "+obj.time+" 秒<br>")
		$("#lastLearn").append("↓--前回の学習に使用したファイル--↓<br>")
		for (var i=0;i<Object.keys(obj.fList).length;i++){
			$("#lastLearn").append(obj.fList[i]+"<br>")
		}

	}

	var learnHost = "ws://"+document.domain+':'+location.port+"/learn";
	var learnSocket = new WebSocket(learnHost);
	$('#learnBtn').click(function(e){
		var area = $('[name=hoge]:checked').map(function() {
			return $(this).parents('tr').children()[1].innerText;
		}).get();
		$(".modal-title").empty();
		$(".modal-title").append("学習モデルを更新しています（完了には数十秒から数分かかります）");
		$(".modal-body").empty();
		$(".modal-body").append("このウィンドウは閉じても構いません"+
														"（このページは、更新次第自動的に再読込します）");

		learnSocket.send(area)
	})
	learnSocket.onmessage = function(message){
		$(".modal-title").empty();
		$(".modal-title").append("更新完了");
		$(".modal-body").empty();
		$(".modal-body").append("学習モデルの更新を完了しました。（2秒後にページを再読込します）");

		setTimeout(function(){
			location.reload(true)
		}, 2000);
	}

	//----------------------------------------------------------------------------//
	corpusListSocket.onmessage = function(message){

		console.log(message.data)
    var tmpObj = JSON.parse(message.data)

		$("#fListTable").empty();
		$("#fListTable").append("<form name=\"fList\"><table class=\"table table-striped table-hover\">"+
														"<thead><tr>"+
                            "<th class=\"col-md-1\">#</th>"+
														"<th class=\"col-md-9\">ファイル名</th>"+
                            "<th class=\"col-md-1\">データ数</th>"+
                            "</tr></thead>"+
														"<tbody id=\"fListTbody\"></tbody></table></form>");

		var table = document.getElementById("fListTbody");

		obj = tmpObj.csvList
		for (var i=0;i<Object.keys(obj).length;i++){
			var dataNum = obj[(i+1)].dataNum
			var fName = "corpus"+obj[(i+1)].fDate+".csv"

			var row = table.insertRow(-1);

			var td1 = row.insertCell(-1)
			td1.innerHTML="<input name=\"hoge\" type=\"checkbox\" value=\""+dataNum+"\" >"

			var td2 = row.insertCell(-1)
			td2.innerHTML=fName

			var td3 = row.insertCell(-1)
			td3.innerText=dataNum

		}
		obj = tmpObj.defList
		for (var i=0;i<Object.keys(obj).length;i++){
			var dataNum = obj[(i+1)].dataNum
			var fName = "DEFAULT"+obj[(i+1)].fDate+".csv"

			var row = table.insertRow(-1);

			var td1 = row.insertCell(-1)
			td1.innerHTML="<input name=\"hoge\" type=\"checkbox\" value=\""+dataNum+"\" checked>"

			var td2 = row.insertCell(-1)
			td2.innerHTML=fName

			var td3 = row.insertCell(-1)
			td3.innerText=dataNum

		}
		dataNum_total()
		$('[name=hoge]').click(function(e){
		    e.stopPropagation();
				dataNum_total()
		}).parents('tr').click(function(){
		    $(this).find('[name=hoge]').prop('checked', !$(this).find('[name=hoge]').prop('checked'));
				dataNum_total()
		});

	}
	//----------------------------------------------------------------------------//

})

function dataNum_total(){
	sum = 0;
	for (i=0; i<document.fList.length; i++){
		if (document.fList.elements[i].checked){
			sum += eval(document.fList.elements[i].value);
		}
	}
	$("#dataNum").empty();
	$("#dataNum").append("<p>現在選択されているファイル内の総データ数 ： "+sum+"件<p>");
}
