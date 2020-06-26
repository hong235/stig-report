import sys
import subprocess

cmd = ['report.py --config report.ini']
subprocess.Popen([cmd])
#subprocess.Popen([sys.executable, cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
