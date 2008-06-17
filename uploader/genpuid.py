import subprocess, platform
import re
from hplatform import get_genpuid_path

if platform.system() not in ('Darwin', 'Linux'):
	import clr
	import System
	from System.Diagnostics import Process

	def gen_win(filename):
		p = Process()
		p.StartInfo.FileName = r'.\genpuid'
		p.StartInfo.Arguments = r'ffa7339e1b6bb1d26593776b4257fce1 -noanalysis'\
				+'"'+filename+'"'

		p.StartInfo.UseShellExecute = False
		p.StartInfo.CreateNoWindow = True
		p.StartInfo.RedirectStandardOutput = True
		p.Start()
		p.WaitForExit()

		return p.StandardOutput.ReadToEnd()
	plat_gen = gen_win
else:
	def gen_posix(filename):
		prog = subprocess.Popen(
					[get_genpuid_path(), 'ffa7339e1b6bb1d26593776b4257fce1', 
							'-noanalysis', filename],
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE)
		prog.stderr.read()
		return prog.stdout.read()

	plat_gen = gen_posix	

def gen(filename):
	match = re.search(r'puid: ([0-9a-z-]+)', plat_gen(filename))
	if not match:
		return None
	
	return match.group(1)
