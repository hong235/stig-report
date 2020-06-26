import os, sys
import subprocess

#cmd = ['report.py --config report.ini']
#subprocess.Popen([sys.executable, cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
os.system('python report.py --config report.ini')
