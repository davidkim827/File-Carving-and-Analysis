# File-Carving-and-Analysis

This project takes in (2 specific given disk images, but can uncomment the argparsing portion of the code) disk images, 
carves the files from them (using the subprocess module and using tsk_recover function from theThe Sleuth Kit package), 
walks through and analyzes every output file for its filename, MD5hash, and, if possible, metadata. The script then goes to
puttting all of them in a SQLite database format, then queries all of the information, outputting it in to a final report text file.

This code is not for re-use by any student, and I am not responsible for any code reuse that others employ.
