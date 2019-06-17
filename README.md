# File-Carving-and-Analysis

<b><i>Use of any code in this repo in any form for academic purposes is considered cheating, which is not only unfair to your classmates, but as well as yourself. Use at your own risk.</i></b>

This project takes in (2 specific given disk images, but can uncomment the argparsing portion of the code) disk images, 
carves the files from them (using the subprocess module and using tsk_recover function from theThe Sleuth Kit package), 
walks through and analyzes every output file for its filename, MD5hash, and, if possible, metadata. The script then goes to
puttting all of them in a SQLite database format, then queries all of the information, outputting it in to a final report text file.
