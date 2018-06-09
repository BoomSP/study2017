
var corpusListHost = "ws://"+document.domain+':'+location.port+"/corpusList";
var corpusListSocket = new WebSocket(corpusListHost);

var corpusParseHost = "ws://"+document.domain+':'+location.port+"/corpusParse";
var corpusParseSocket = new WebSocket(corpusParseHost);

var updateHost = "ws://"+document.domain+':'+location.port+"/update";
var updateSocket = new WebSocket(updateHost);
var deleteHost = "ws://"+document.domain+':'+location.port+"/delete";
var deleteSocket = new WebSocket(deleteHost);

$(function(){

	corpusParseSocket.onopen = function(){
		var path= location.pathname;
		fDate = path.replace(/.+edit\//g, "")
		if (fDate != ""){
			corpusParseSocket.send(fDate)
		}
	}
	//-[現在のコーパスを取得し，ドロップダウンリストに表示]-------------------------------//
  corpusListSocket.onmessage = function(message){

		console.log(message.data)
    var tmpObj = JSON.parse(message.data)
		var obj = tmpObj.csvList

		//-[ドロップダウンリストへの表示]------------------------------------------------//
    $(".fListDD").empty();
		for (var i=0;i<Object.keys(obj).length;i++){
			fDate = obj[(i+1)].fDate
			dateStr = "20"+fDate.slice(0,2)+"年"+fDate.slice(2,4)+"月"+fDate.slice(4,6)+"日"
      $(".fListDD").append("<li role=\"presentation\">"+
									"<a class=\"select\" href=\"/edit/"+fDate+"\">"+dateStr+"</a></li>")
		}
		//--------------------------------------------------------------------------//
	}
	//----------------------------------------------------------------------------//

	//-[]
	corpusParseSocket.onmessage = function(message){
		obj = JSON.parse(message.data);
		if(obj.status=="SUCCESS"){
			$("#date").empty();
			$("#date").append(obj.date)
			if(Object.keys(obj.csvData).length > 0){
				tableDraw(obj.csvData)
			}else{
				var data = message.data.split(",")
				var date = data[0]
				$("#codeTable").empty();
				$("#codeTable").append("<font color=\"#AAAAAA\">ここに登録されたコーパスが表示されます</font>")
			}
		}else{
			$("#date").empty();
			$("#codeTable").empty();
		}
	}
	//----------------------------------------------------------------------------//


	//-[更新ボタン投下]-------------------------------------------------------------//
  $("#update").on("click",function(){

		newID = $("#newID").val()

    text  = $("#newText").val()
		text  = text.replace(/,/g, "、")
		text  = text.replace(/\n/g, "")

		code  = $("#newCode").val()

		if(text=="" || code=="" || !code.match(/^[0-9A-Z][0-9]{2}$/)){
			$('#inputErrorModal').modal();;
		}else{
			updateSocket.send([$("#date").text(), newID, text, code]);
		}
	});
	//----------------------------------------------------------------------------//

	//-[削除ボタン投下]-------------------------------------------------------------//
	$("#deleteBtn").on("click",function(){
		delID = $("#delID").val()
    deleteSocket.send([$("#date").text(), delID]);
	});
	//----------------------------------------------------------------------------//
	updateSocket.onmessage = function(message){location.reload(true)}
	deleteSocket.onmessage = function(message){location.reload(true)}

})


var tableDraw = function(message) {

	console.dir(message)
	obj = message;
	console.dir(obj)
    $("#codeTable").empty();
		$("#codeTable").append("<table class=\"table table-striped table-hover\">"+
														"<thead><tr>"+
                            "<th class=\"col-md-1\">No</th>"+
														"<th class=\"col-md-9\">故障情報</th>"+
                            "<th class=\"col-md-1\">故障事由コード</th>"+
                            "<th class=\"col-md-1\"></th>"+
                            "<th class=\"col-md-1\"></th>"+
                            "</tr></thead>"+
														"<tbody id=\"codeTbody\"></tbody></table>");

		var table = document.getElementById("codeTbody");

		for (var i=0; i<Object.keys(obj).length;i++){
			var row = table.insertRow(-1);

			var td1 = row.insertCell(-1)
			td1.innerText=obj[(i+1)].id

			var td2 = row.insertCell(-1)
			td2.innerText=obj[(i+1)].text

			var td3 = row.insertCell(-1)
			td3.innerText=obj[""+(i+1)].code

      var td0 = row.insertCell(-1)
			td0.innerHTML="<button class=\"edit btn btn-primary \" data-toggle=\"modal\" data-target=\"#editModal\">編集</button></div>"

      var td4 = row.insertCell(-1)
			td4.innerHTML="<button class=\"delete btn btn-danger\" data-toggle=\"modal\" data-target=\"#deleteModal\">削除</button></div>"

		}
    $(".edit").on("click",function(){
      console.dir($(this).closest('tr').children('td').eq(0).text());
			var idNum = $(this).closest('tr').children('td').eq(0).text()
      var code  = $(this).closest('tr').children('td').eq(2).text()
      var text  = $(this).closest('tr').children('td').eq(1).text()
      console.log(text);

			$("#id2").append("<input id=\"newID\" type=\"hidden\" value=\""+idNum+"\">")

      $("#code2").empty();
      $("#code2").append("<input id=\"newCode\" class=\"form-control pull-left\""+
      " placeholder=\"半角英数字\" style=\"width:100px;\" pattern=\"^([a-zA-Z0-9]{3,3})$\" value=\""+code+"\">")

      $("#text2").empty();
      $("#text2").append("<textarea id=\"newText\" class=\"form-control\" rows=3 placeholder=\"100文字までです。\">"+text+"</textarea>")


  	});
    $(".delete").on("click",function(){
      console.dir($(this).closest('tr').children('td').eq(0).text());
			console.dir($(this).closest('tr').children('td').eq(0).text());
			var idNum = $(this).closest('tr').children('td').eq(0).text()
      var code  = $(this).closest('tr').children('td').eq(2).text()
      var text  = $(this).closest('tr').children('td').eq(1).text()
      console.log(text);

			$("#idDel").append("<input id=\"delID\" type=\"hidden\" value=\""+idNum+"\">")

      $("#codeDel").empty();
      $("#codeDel").append(code)

      $("#textDel").empty();
      $("#textDel").append(text)


  	});


};
