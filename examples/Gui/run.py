"""
This script sets up the necessary paths and executes the main function from the GUI package.

Script Overview:
- Imports the 'os' module to manage file paths.
- Determines the directory of the current script.
- Appends the path to the 'GuiFiles' directory to the system path.
- Constructs the path to the 'main.py' script within the 'GuiFiles' directory.
- Prints the path to the 'main.py' script.
- Sets up the data path for additional resources.
- Initializes an empty list 'setup' to store setup function names.
- Reads the content of the 'main.py' script.
- Iterates through the lines of the script to identify and extract setup function names.
- Executes the content of the 'main.py' script.
- Executes the identified setup functions from the 'main.py' script.

Usage:
- Ensure that the 'GuiFiles' directory contains the required files and scripts.
- Run this script to set up paths and execute the main function with setup procedures.

Note: This script relies on the structure of the 'GuiFiles' directory and the 'main.py' script.

Author: Sean Mongan
Date: 08/11/2023
"""

import os
self_dir = os.path.dirname(__file__)

os.sys.path.append(os.path.join(self_dir,'GuiFiles'))
main_path = os.path.join(self_dir, 'GuiFiles', 'main.py')
print(main_path)

data_path = os.path.join(self_dir, 'GuiFiles')
setup = []

with open(main_path) as f:
    file = f.read()
for x in file.split('\n'):
    if x.strip().startswith('def setup_'):
        setup.append(x.split('def ')[1].split('(')[0])
exec(file)