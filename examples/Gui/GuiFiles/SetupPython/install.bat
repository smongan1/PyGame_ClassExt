cd /D "%~dp0"
call SetupPython\python-3.11.3-amd64.exe
IF EXIST SetupPython\python_path.txt (GOTO installpy)
call SetupPython\find_python_path.bat
echo "running Batch_Search.bat"
call SetupPython\Batch_Search.bat

:installpy
FOR /F "tokens=*" %%x in (SetupPython\python_path.txt) DO (
	SET python=%%x
)

call %python% -m pip install --upgrade pip

start %python% SetupPython\install.py