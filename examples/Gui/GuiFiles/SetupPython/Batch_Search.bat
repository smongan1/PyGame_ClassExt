IF EXIST SetupPython\python_path_temp.txt (GOTO run)
goto eof2
:run
set lineskip=1
:LOOP
set filedata=""
FOR /F "tokens=* skip=%lineskip%"  %%x in (SetupPython\python_path_temp.txt) DO (
	set filedata="%%x"
	SET loop1cnt=1
	goto loop1
)
	
:LOOP1
echo %filedata%
SET loop1var=""
FOR /F "tokens=%loop1cnt%" %%a in (%filedata%) DO (
	SET loop1var="%%a"
	SET loop2cnt=1
	goto loop2
)

:LOOP2
SET loop2var=""
FOR /F "tokens=%loop2cnt% delims=\" %%w in (%loop1var%) DO (
	SET loop2var="%%w"
	goto incloop2
)
:incloop2
IF %loop2var%=="" (goto incLOOP1)
echo %loop1var:"=%\Python311\python.exe > SetupPython\python_path.txt
IF %loop2var%=="Python" (GOTO eof)
SET /A loop2cnt+=1
goto loop2

:incLOOP1
IF %loop1var%=="" (GOTO incloop)
SET /A loop1cnt+=1
goto LOOP1

:incloop
IF %filedata%==""(GOTO eof)
SET /A lineskip+=1
GOTO loop

goto eof


:eof
del SetupPython\python_path_temp.txt
:eof2