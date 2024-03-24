import os
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
os.system("pip install -r requirements.txt")
