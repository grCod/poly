#! /usr/bin/python
# -*- coding: utf-8 -*-

import random
from base64 import b64encode
import re 


class Strings(object) : 
	
	ints = "1234567890"
	chars = "abcdeffhijklmnopqrstuvwxyzABCDWFGHIJKLMNOPQRSTUVWXYZ"
	s_chars = "!@#%^*()[]"
	u_chars = "ABCDWFGHIJKLMNOPQRSTUVWXYZ"
	l_chars = "abcdeffhijklmnopqrstuvwxyz"
	an_chars = "1234567890abcdeffhijklmnopqrstuvwxyzABCDWFGHIJKLMNOPQRSTUVWXYZ" 
	all_chars = "1234567890-=!@#$%^&*()_+qwertyuiop[]QWERTYUIOP{}asdfghjkl;'\\ASDFGHJKL:\"|zxcvbnm,./ZXCVBNM<>? \n\t"
	
	def rndStr(self, size, charset): 
		return ''.join(random.choice(charset) for _ in range(size))
	
	def rndInt(self, min, max): 
		return random.randint(min, max) 
	
	def rndChr(self, string): 
		return random.choice(string)


class Encoders(Strings): 
	
	def __init__(self, shell): 
		self.shell_data = shell
		self.shell_encoded = ""
	
	def Base64(self): 
		self.shell_encoded = b64encode(self.shell_data)
		return self.shell_encoded
	
	def OrdPlus(self): 
		ord_plus = self.rndInt(1, 1000)
		chr_join = self.rndStr(1, self.chars)
		self.shell_encoded = chr_join.join([ str(ord(s) + ord_plus) for s in self.shell_data ])
		return (self.shell_encoded, ord_plus, chr_join)
	
	def Random(self): 
		cs1 = self.Str2Rnd(self.all_chars) 
		cs2 = self.Str2Rnd(cs1) 
		shell_data = self.UTF8Encode(self.shell_data)
		self.shell_encoded = ''.join([ cs2[cs1.index(c)] if c in cs1 else c for c in shell_data ]) 
		return (self.shell_encoded, cs1, cs2)
	
	def Rot90(self): 
		shell_data = self.UTF8Encode(self.shell_data)
		rows = self.rndInt(2, (400 if len(shell_data) > 400 else len(shell_data) - 2))
		while len(shell_data) % rows != 0 : shell_data += ' '
		block_size = len(shell_data) / rows
		table = [ shell_data[ block_size * i : block_size * (i + 1) ] for i in range(rows) ] 
		self.shell_encoded = ''.join([ ''.join([ r[i] for r in table ]) for i in range(block_size) ])
		return (self.shell_encoded, rows) 
	
	def Str2Rnd(self, str1): 
		str2 = ""
		str1_copy = str1 
		while len(str2) < len(str1) : 
			c = self.rndChr(str1_copy)
			if c in str2 or str1.find(c) == len(str2) : continue
			str2 += c
			str1_copy = str1_copy.replace(c, '')
		return str2
	
	def UTF8Encode(self, string): 
		text = '' 
		for c in string : 
			try : text += c.encode('utf-8')
			except : text += ' '
		return text


class Junk(Strings): 
	
	def Php(self, vars): 
		junk  = [ '/* ' + ' '.join(self.rndStr(self.rndInt(8, 16), self.an_chars) for _ in range(self.rndInt(2, 6))) + ' */' ]
		junk += [ vars[0] + ' = "' + self.rndStr(self.rndInt(60, 120), self.an_chars) + '"; ' ]
		junk += [ vars[1] + ' = "' + self.rndStr(self.rndInt(40, 60), self.an_chars) + '" . "' + self.rndStr(self.rndInt(40, 60), self.an_chars) + '"; ' ]
		junk += [ 'if(@' + vars[2] + ' == "' + self.rndStr(self.rndInt(40, 60), self.an_chars) + '") { echo "' + self.rndStr(self.rndInt(40, 80), self.an_chars) + '"; } ' ]
		junk += [ 'while(' + str(self.rndInt(0, 19)) + ' > ' + str(self.rndInt(20, 80)) + ') { @' + vars[2] + ' .= "' + self.rndStr(self.rndInt(60, 120), self.an_chars) + '"; }' ]
		junk += [ 'foreach(str_split("' + self.rndStr(self.rndInt(60, 120), self.chars) + '") as ' + vars[3] + ') { @' + vars[1] + ' += ' + vars[3] + '; } ' ]
		return junk
	
	def Asp(self, vars): 
		junk = [ '\' ' + ' '.join(self.rndStr(self.rndInt(8, 16), self.an_chars) for _ in range(self.rndInt(2, 6))) ]
		junk += [ 'dim ' + vars[0] + ' : ' + vars[0] + ' = "' + self.rndStr(self.rndInt(60, 120), self.an_chars) + '" ' ] 
		junk += [ 'dim ' + vars[1] + ' : ' + vars[1] + ' = "' + self.rndStr(self.rndInt(40, 60), self.an_chars) + '" & "' + self.rndStr(self.rndInt(40, 60), self.an_chars) + '" ' ]
		junk += [ 'if ' + str(self.rndInt(1, 19)) + ' > ' + str(self.rndInt(20, 80)) + ' then dim ' + vars[2] + ' : ' + vars[2] + ' = "' + self.rndStr(self.rndInt(60, 120), self.chars) + '" ' ] 
		junk += [ 'for ' + vars[3] + ' = 1 to len("' + self.rndStr(self.rndInt(60, 120), self.an_chars) + '") : next ' ]
		return junk
	
	def Aspx(self, vars): 
		var_ini = 'string '
		junk = [ '/* ' + ' '.join(self.rndStr(self.rndInt(8, 16), self.an_chars) for _ in range(self.rndInt(2, 6))) + ' */' ]
		junk += [ var_ini + vars[0] + ' = "' + self.rndStr(self.rndInt(60, 120), self.an_chars) + '"; ' ]
		junk += [ var_ini + vars[1] + ' = "' + self.rndStr(self.rndInt(40, 60), self.an_chars) + '" + "' + self.rndStr(self.rndInt(40, 60), self.an_chars) + '"; ' ]
		junk += [ 'foreach( char ' + vars[2] + ' in "' + self.rndStr(self.rndInt(60, 120), self.an_chars) + '" ) { ' + vars[2] + '.ToString(); }' ]
		junk += [ 'while(' + str(self.rndInt(1, 39)) + ' > ' + str(self.rndInt(40, 80)) + ') { Convert.ToInt32("' + self.rndStr(self.rndInt(40, 50), self.ints) + '"); }' ]
		junk += [ 'public string ' + vars[3] + '( string ' + vars[0] + ' ) { return ' + vars[0] + ' + "' + self.rndStr(self.rndInt(60, 120), self.an_chars) + '"; } ' ]
		return junk
	
	def Js(self, vars): 
		junk = [ '/* ' + ' '.join(self.rndStr(self.rndInt(8, 16), self.an_chars) for _ in range(self.rndInt(2, 6))) + ' */' ]
		junk += [ 'var ' + vars[0] + ' = "' + self.rndStr(self.rndInt(60, 120), self.an_chars) + '"; ' ]
		junk += [ 'var ' + vars[1] + ' = "' + self.rndStr(self.rndInt(40, 60), self.an_chars) + '" + "' + self.rndStr(self.rndInt(40, 60), self.an_chars) + '"; ' ]
		junk += [ 'if(' + str(self.rndInt(1, 19)) + ' > ' + str(self.rndInt(20, 80)) + ') { alert("' + self.rndStr(self.rndInt(60, 120), self.an_chars) + '"); } ' ]
		junk += [ 'while(' + str(self.rndInt(1, 39)) + ' > ' + str(self.rndInt(40, 80)) + ') { var ' + vars[2] + ' = "' + self.rndStr(self.rndInt(60, 120), self.an_chars) + '"; } ' ]
		return junk
	
	def Html(self): 
		junk = [ '<!-- ' + ' '.join(self.rndStr(self.rndInt(8, 16), self.an_chars) for _ in range(self.rndInt(3, 6))) + ' -->' ]
		junk += [ '<input type=hidden value=' + self.rndStr(self.rndInt(18, 24), self.chars) + '>' ]
		return junk
	
	def Add(self, code, vars): 
		pass


class PhpParser : 
	
	def __init__(self, shell): 
		self.code = shell
		self.php_reserved = [ 
			'$GLOBALS', '$_SERVER', '$_REQUEST', '$_POST', '$_GET', 
			'$_FILES', '$_ENV', '$_COOKIE', '$_SESSION', 
			'$argc', '$argv', '$this->' 
		] 
	
	def arraySort(self, array): 
		tmp = []
		for a in array : 
			if a not in tmp : tmp += [a]
		return sorted(tmp, key=len, reverse=True)
	
	def StripTags(self, code = None): 
		if code == None : code = self.code
		code = code.strip()
		if code.lower()[:5] == "<?php" : code = code[5:]
		if code[:2] == "<?" : code = code[2:]
		if code[-2:] == "?>" : code = code[:-2]
		return code
	
	def stripComments(self, code = None): 
		if code == None : code = self.code
		comments = sorted(self.Parts(code, 'comments'), key=len, reverse=True)
		for comment in comments : code = code.replace(comment, '')
		return code
	
	def Parts(self, part, get): 
		clean_var = lambda v : v.split(' ')[0].split('.')[0].split(',')[0].split('=')[0].split(')')[0]
		code_rexp = { 
			"php":"<\?.*?[\n}{;]\s*\?>", "js":"<script.+?</script>", "html":"<html.+?</html>", 
			"php_vars":"(\$[\w]*)\s*=", "js_vars":"var\s*([\w]*)\s*[=;,]", 
			"functions":"function\s+([\w]*)\s*\(", "classes":"class\s+([\w]*)\s*{", 
			"strings":r"(\".*?(?<!\\(?<!\\\\(?<!\\\\\\)))\")|('.*?(?<!\\(?<!\\\\(?<!\\\\\\)))')", 
			"comments":"[\n\t\)}{;]\s*(//.*?\n)|[\n\t;]\s*(#.*?\n)|(/\*.*?\*/)" 
		} 
		if get in [ 'php', 'js', 'html', 'strings', 'comments' ] : 
			rexp = re.compile(code_rexp[get], re.DOTALL|re.IGNORECASE) 
		else : 
			rexp = re.compile(code_rexp[get], re.IGNORECASE)
		if get == 'php_vars' : 
			parts = [ 
				clean_var(r) 
				for r in re.findall(rexp, part) 
				if clean_var(r) != '' and clean_var(r).split('[')[0] not in self.php_reserved 
			] 
		elif get in ['strings', 'comments'] : 
			parts = [ ''.join(r) for r in re.findall(rexp, part) if len(r) > 0 ]
		else : 
			parts = [ r.strip() for r in re.findall(rexp, part) if r.strip() != '' ]
		return self.arraySort([ part.strip() for part in parts if part.strip() != '' ])
	
	def getParts(self, code = None): 
		if code == None : code = self.code
		place_holder = '====' + Strings().rndStr(40, Strings().an_chars) + '===='
		php = self.arraySort(self.Parts(code,'php'))
		for p in php : code = code.replace(p, place_holder) 
		js = self.arraySort([ j for p in self.Parts(code, 'js') for j in p.split(place_holder) if j.strip() != '' ]) 
		for j in js : code = code.replace(j, place_holder)  
		html = self.arraySort([ h for h in code.split(place_holder) if h.strip() != '' ])
		vars = self.arraySort([ v for p in php for v in self.Parts(p, 'php_vars') ]) 
		strings= self.arraySort([ s for p in php for s in self.Parts(self.stripComments(p), 'strings') ]) 
		comments = self.arraySort([ c for p in php for c in self.Parts([ p.replace(s, '') for s in strings ][-1], 'comments') ]) 
		return { 'php':php, 'js':js, 'html':html, 'vars':vars, 'strings':strings, 'comments':comments } 


class AspParser : 
	
	def __init__(self, shell): 
		self.code = shell
	
	def arraySort(self, array): 
		tmp = []
		for a in array : 
			if a not in tmp : tmp += [a]
		return sorted(tmp, key=len, reverse=True)
	
	def stripTags(self, code = None):
		if code == None : code = self.code
		code = code.strip()
		if code[:2] == "<%" : code = code[2:]
		if code[-2:] == "%>" : code = code[:-2]
		return code
	
	def stripHead(self, code = None): 
		if code == None : code = self.code
		for asp in self.getParts()['asp'] : 
			if re.match('<%\s*@\s*language\s*=\s*[\s\'"]vbscript', asp, re.IGNORECASE) : 
				code = code.replace(asp, '')
		return code

	def stripComments(self, code = None): 
		if code == None : code = self.code
		comments = self.Parts(code, 'comments') 
		for comment in comments : code = code.replace(comment, '')
		return code
		
	def Parts(self, part, get='asp'): 
		code_rexp = { 
			'asp':'(<%.*?%>)', 'js':'<script.+?</script>', 'html':'<html.+?</html>', 
			'asp_vars':'dim\s*(.*?)[:\n]', 'js_vars':'var\s*([\w]*)\s*[=;,]', 
			"functions":"function\s+([\w]*)\s*\(", "subs":"sub\s+([\w]*)\s*\(", 
			'strings':'(".*?")', 'comments':'(\'.*?)\n' 
		}
		if get in [ 'asp', 'js', 'html', 'strings' ] : rexp = re.compile(code_rexp[get], re.DOTALL|re.IGNORECASE) 
		else : rexp = re.compile(code_rexp[get], re.IGNORECASE)
		if get == 'asp_vars' : parts = [ p for part in re.findall(rexp, part) for p in part.split(',') ] 
		else : parts = [ part for part in re.findall(rexp, part) ]
		return list(set([ part.strip() for part in parts if part.strip() != '' ]))
	
	def getParts(self, code = None): 
		if code == None : code = self.code
		place_holder = '====' + Strings().rndStr(40, Strings().an_chars) + '===='
		asp = self.Parts(code,'asp')
		for a in asp : code = code.replace(a, place_holder) 
		js = self.arraySort([ j for p in self.Parts(code, 'js') for j in p.split(place_holder) if j.strip() != '' ]) 
		for j in js : code = code.replace(j, place_holder)  
		html = self.arraySort([ h for h in code.split(place_holder) if h.strip() != '' ])
		vars = self.arraySort([ v for p in asp for v in self.Parts(p, 'asp_vars') ]) 
		strings= self.arraySort([ s for p in asp for s in self.Parts(p, 'strings') ]) 
		comments = self.arraySort([ c for p in asp for c in self.Parts(p, 'comments') ])  
		return { 'asp':asp, 'js':js, 'html':html, 'vars':vars, 'strings':strings, 'comments':comments }


class AspxParser : 
	pass

