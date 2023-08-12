import subprocess
import os

self_dir = os.path.dirname(__file__)
fpath = os.path.dirname(self_dir)
os.sys.path.append(os.path.join(fpath,'CaseHelper_dist'))
main_path = os.path.join(self_dir, 'main.py')
print(main_path)

data_path = os.path.join(fpath, 'CaseHelper_dist')
setup = []

with open(main_path) as f:
    file = f.read()
for x in file.split('\n'):
    if x.strip().startswith('def setup_'):
        setup.append(x.split('def ')[1].split('(')[0])
exec(file)