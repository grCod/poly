#! /usr/bin/python 
# -*- coding: utf-8 -*- 

import argparse
from src.php import Php
from src.asp import Asp
from src.aspx import Aspx


ap = argparse.ArgumentParser()
ap.add_argument('-c', help= 'Shell code. [ php, asp, aspx ]', required = True)
ap.add_argument('-e', help= 'Encoding method. [ b64, ord, rnd, rot ]', default = 'b64')
ap.add_argument('-p', help= 'Path to shell.', default = None) 
ap.add_argument('-j', help= 'Add junk code.', action = 'store_true', default = False)
args = ap.parse_args()

shell_type = args.c.lower() if args.p is None else args.p.split('.')[-1].lower()
shell_encoding = args.e.lower()
shell_path = args.p 
junk = args.j 

if shell_type not in [ 'php', 'asp', 'aspx' ] : 
	exit("{} shells are not supported.".format(shell_type)) 
if shell_encoding not in [ 'b64', 'ord', 'rnd', 'rot' ] : 
	exit("'{}' encoding is not supported.".format(shell_encoding)) 
if shell_type == 'php' : 
	poly = Php(shell_path) 
if shell_type == 'asp' : 
	poly = Asp(shell_path) 
if shell_type == 'aspx' : 
	poly = Aspx(shell_path) 
if poly.shell_text == None : 
	exit("Can't access file: {}".format(poly.shell_path))
encoded = poly.Encode(shell_encoding) 
encoded_shell = poly.Create(encoded, junk) 
poly.Write(encoded_shell)

