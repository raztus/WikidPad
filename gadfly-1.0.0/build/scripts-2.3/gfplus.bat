@echo off
if NOT "%_4ver%" == "" C:\Python23\python.exe -c "from gadfly.scripts.gfplus import main; main()" %$
if     "%_4ver%" == "" C:\Python23\python.exe -c "from gadfly.scripts.gfplus import main; main()" %*