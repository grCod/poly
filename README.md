# poly
A python script that generates polymorphic webshells.  
Use it to encode your favourite shell and make it practically undetectable.  
If no shell is specified with the -p arguement,  the default shell in the /shells directory is used.  
  
>Supported webshells  

| Webshell |   |  
| --------- | --------- |  
| .php |  |  
| .asp | ( vbs ) |  
| .aspx | ( c# ) |  

>Supported encoders  

| Encoding |   |  
| --------- | --------- |  
| b64  |  base64 encoded text with random strings in random intervals |  
| ord  |  ord() each character plus a random number |  
| rnd  |  each character is mapped to another random character |  
| rot  |  text is divided by a random number of rows, then rotated 90 degrees clockwise |  

>C99 shell uploaded on virustotal  

| Encoding | Detection rate |  
| -------- | --------- |
| none | 41 / 56 |  
| b64 | 0 / 52 |  
| ord | 0 / 54 |  
| rnd | 0 / 56 |  
| rot | 0 / 56 |  
  
**Requirements :**  
Python 2.7

**Notice :**  
With asp shells it is recommended to use the default shell. ( /shells/shell.asp )  
Encoded aspx shells may not work on some servers.  
Php works pretty much with every shell, on every server.  
Rnd and rot encodings are not binary safe. ( may produce unprintable characters )  
  
**Disclaimer :**  
This tool is made for educational and research purposes.  
Don't be evil.. 
