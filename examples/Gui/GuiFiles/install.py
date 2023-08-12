import subprocess
import os

with open('SetupPython\python_path.txt') as f:
    pypath = f.read()
pypath = pypath.split('\n')[0]
pypath = os.path.split(pypath)
pypath = os.path.join(*pypath[:-1])
self_dir = os.path.dirname(__file__)
fpath = os.path.dirname(self_dir)
os.sys.path.append(os.path.join(fpath,'CaseHelper_dist'))
c =  os.path.join(pypath,'Scripts','pip.exe')
c2 = 'install'
c3 = '--upgrade'
c4 = '--force-reinstall'
c5 = os.path.join(fpath, 'SetupPython', 'requirements.txt')
with open(c5) as f:
    packages = f.read().split('\n')
subprocess.call([c, c2, c3, 'certifi'])
for package in packages:
    subprocess.call([c, c2, c3, c4, package])
for run_file in ['run.bat', 'reinstall.bat']:#,'run.py', 'main.py']:
    with open(os.path.join(self_dir, run_file )) as f:
        data = f.read()
    with open(os.path.join(fpath, run_file), 'w') as f:
        f.write(data)

with open(os.path.join(fpath, 'install.bat')) as f:
    data = f.read()
with open(os.path.join(self_dir,  'install.bat'), 'w') as f:
    f.write(data)

os.remove(os.path.join(fpath, 'install.bat'))