# poly
A python script that generates polymorphic webshells.  
Use it to encode your favourite shell and make it practically undetectable.  
if no shell is specified with the -p arguement,  
the default shell in the /webshells directory is used.  
  
**Notice :**  
With asp shells it is recommended to use the default shell. ( /shells/shell.asp )  
Aspx shells may not work on some servers.  
Php works pretty much with every shell, on every server.  
Rnd and rot encodings are not binary safe. ( may produce unprintable characters )  

| Webshells |   |  
| --------- | --------- |  
| php |  |  
| asp | ( vbs ) |  
| aspx | ( c# ) |  
  
| Encodings |   |  
| --------- | --------- |  
| b64  |  base64 encoded text |  
| ord  |  ord() each character plus a random number |  
| rnd  |  each character is mapped to another random character |  
| rot  |  text divided in random number of rows, then rotated by 90 degrees |  

**Disclaimer :**  
This tool is made for educational and research purposes.  
Don't be evil.. 
