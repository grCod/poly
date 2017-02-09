#! /usr/bin/python 
# -*- coding: utf-8 -*- 

import argparse
from src.php import Php
from src.asp import Asp
from src.aspx import Aspx


ap = argparse.ArgumentParser()
ap.add_argument('-c', help= 'Shell type. [ php, asp, aspx ]', default = 'php')
ap.add_argument('-e', help= 'Encoding method. [ b64, ord, rnd, rot ]', default = 'b64')
ap.add_argument('-p', help= 'Path to shell.', default = None) 
ap.add_argument('-j', help= 'Add junk.', action = 'store_true', default = False)
args = ap.parse_args()

shell_type = args.c.split('.')[-1].lower() if args.p == None else args.p.split('.')[-1].lower()
encoding_type = args.e.lower()
shell_path = args.p 
junk = args.j 

asp_test = 'C:\\users\\i\\documents\\scripts\\poly\\test\\shell.asp'

if shell_type not in [ 'php', 'asp', 'aspx' ] : exit("'" + shell_type + "' not supported.") 
if encoding_type not in [ 'b64', 'ord', 'rnd', 'rot' ] : exit("Encoding not supported.") 
if shell_type == 'php' : poly = Php(shell_path) 
if shell_type == 'asp' : poly = Asp(shell_path) 
if shell_type == 'aspx' : poly = Aspx(shell_path) 
if poly.shell_text == None : exit("Can't read file: " + poly.shell_path)
if encoding_type == 'b64' : encoded_shell = poly.Base64(junk) 
if encoding_type == 'ord' : encoded_shell = poly.OrdPlus(junk) 
if encoding_type == 'rnd' : encoded_shell = poly.Random(junk) 
if encoding_type == 'rot' : encoded_shell = poly.RotPlus(junk) 
poly.Write(encoded_shell)

