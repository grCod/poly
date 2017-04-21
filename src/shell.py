#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
from util import Strings


class Shell(Strings) : 
	
	def __init__(self, shell_type): 
		self.shell_code = shell_type
		self.vars = []
	
	def makeVars(self): 
		var = self.rndStr(1, self.chars) + self.rndStr(self.rndInt(6, 12), self.an_chars)
		return self.makeVars() if var in self.vars else var 
	
	def makeVals(self, data, junk = '', size = (100, 160)): 
		parts = []
		if len(data) <= size[1] : 
			parts += [data] 
		else : 
			i = 0 
			while i < len(data) : 
				r = self.rndInt(size[0], size[1]) 
				parts += [ data[i : i + (len(data) - i if i + r > len(data) else r)] ]
				i += r
		if junk != '' : parts = [ self.addJunk(part, junk) for part in parts ]
		return parts
	
	def makeJunk(self, data, chars, size = 1): 
		jnk_str = ""
		while jnk_str in data : jnk_str += self.rndChr(chars)
		while len(jnk_str) < size : jnk_str += self.rndChr(chars)
		return jnk_str
	
	def addJunk(self, part, junk): 
		r = [ i for i in range(self.rndInt(1, 4), (len(part) - 1), self.rndInt(16, 24)) ] 
		part = ''.join([ part[i] + junk if i in r else part[i] for i in range(len(part)) ])
		return part
	
	def Read(self, path = None): 
		shell_path = self.shell_path if path == None else path
		try : 
			with open(shell_path, 'r') as f : shell_data = f.read()
		except : 
			exit("Can't access file: " + shell_path) 
		else : 
			return shell_data.strip()
	
	def Write(self, shell): 
		file_name = self.rndStr(self.rndInt(4, 8), self.an_chars) + '.' + self.shell_code.lower()
		file_path = os.path.join(self.Path.output, file_name)
		try : 
			with open(file_path, 'w') as f : f.write(shell)
		except : 
			print('Couldn\'t write file: {}'.format(file_path))
		else : 
			print('File: \'{}\' saved.'.format(file_name))
	
	class Path : 
		
		this = os.path.dirname(os.path.abspath(__file__))
		root = os.path.abspath(os.path.join(this, os.pardir))
		shells = os.path.join(root, 'shells')
		output = os.path.join(root, 'output')
		php = os.path.join(shells, 'shell.php')
		asp = os.path.join(shells, 'shell.asp')
		aspx = os.path.join(shells, 'shell.aspx')

