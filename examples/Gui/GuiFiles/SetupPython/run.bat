cd /D "%~dp0"

FOR /F "tokens=*" %%x in (SetupPython\python_path.txt) DO (
	SET python=%%x
)

call %python% SetupPython\run.py