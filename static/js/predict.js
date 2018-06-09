$(function(){

  var host = "ws://"+document.domain+':'+location.port+"/predict";
  var socket = new WebSocket(host);

	//-[推定実行]------------------------------------------------------------------//
  $("#predict").on("click",function(){
    text = $("#text").val()																											//テキストボックスの内容を取得

		$("#result").empty();
		$("#result").append("<div class=\"panel panel-default\">"+									//出力結果用パネル
													"<div id=\"inputText\"></div>"+												//入力内容表示div
													"<div id=\"codeTable\"class=\"panel-body\"</div>"+		//結果表示テーブル用div
												"</div>");

		$("#inputText").append("<br><p><i><b>「 </b>"+text+"<b> 」</b></i></p>");		//入力内容を表示
		if(text==""){
			$('#inputErrorModal_sample').modal();;
		}else{
    	socket.send(text);																												//テキストボックスの内容を送信
		}
	});
	//----------------------------------------------------------------------------//

	//-[ソケットメッセージ受信]-------------------------------------------------------//
  socket.onmessage = function(message){

		$("#codeTable").empty();
		$("#codeTable").append("<table class=\"table table-striped table-hover\">"+
															"<thead><tr>"+
																"<th>尤度順位</th><th>故障事由コード</th><th>故障事由</th><th>確率 [%×100]</th>"+
															"</tr></thead>"+
															"<tbody id=\"codeTbody\"></tbody>"+
														"</table>");

		//-[推定結果の表示]-----------------------------------------------------------//
		obj = JSON.parse(message.data)																							//推定結果[json]のパース
		var table = document.getElementById("codeTbody");														//Tobody要素の取得
		for (var i=0; i<20;i++){
			var row = table.insertRow(-1);
			var td1 = row.insertCell(-1)
			td1.innerText = (i+1)
			var td2 = row.insertCell(-1)
			td2.innerText = obj["number"+(i+1)].code
			var td3 = row.insertCell(-1)
			td3.innerText = obj["number"+(i+1)].codeText
			var td4 = row.insertCell(-1)
			td4.innerText = obj["number"+(i+1)].proba
		}
		//--------------------------------------------------------------------------//
	}
	//----------------------------------------------------------------------------//

	$('.smplBtn').on('click', function(){
		var id =  $(this).attr("id");
		if(id=="smpl1"){
			$("#text").val("ＬＩＮＥで文字入力をする際に、キーボードが出てくるが文字入力できない。")
		}else if(id=="smpl2"){
			$("#text").val("サンプルテキスト2")
		}else{
			$("#text").val("サンプルテキスト3")
		}
	});

})
