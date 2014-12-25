import sys
import os
import subprocess

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


try:
	retcode = subprocess.call(["java", "-version"])
	if retcode < 0:
		print >> sys.stderr, "Java not in Path", -retcode
	else:
		print >> sys.stderr, "Child returned", retcode
except OSError as e:
    print >>sys.stderr, "Execution failed:", e

# print >> sys.stderr, "Current Working directory:", os.getcwd()
appdir = os.path.dirname(os.path.dirname(__file__))

if not appdir:
    appdir = os.getcwd();
else:
    print >> sys.stderr, "App directory:", appdir


# check current OS for process detection
currentOS = os.name

c1 = os.path.join(appdir, "bin", "apache-flume-1.3.1-bin", "lib", "*")
c2 = os.path.join(appdir, "bin", "apache-flume-1.3.1-bin", "lib", "flume-ng-node-1.3.1.jar")
c3 = os.path.join(appdir, "bin", "dtFlume.jar")

classpath = c1 + os.pathsep + c2 + os.pathsep + c3

print >> sys.stderr, "Class path:", classpath

log4j = os.path.join(appdir,"bin", "apache-flume-1.3.1-bin", "conf", "log4j.properties")

flumeconf = os.path.join(appdir,"bin","flume-conf.properties");

pidfilename = os.path.join(appdir, 'flume.pid')


#print >> sys.stderr, "java  -Xmx20m -Dlog4j.configuration=file:" + log4j + " -cp " + classpath + " org.apache.flume.node.Application -f flume-conf.properties -n agent1"

cmdline = "java  -Xmx20m -Dlog4j.configuration=file:" + log4j + " -cp " + classpath + " org.apache.flume.node.Application -f " + flumeconf + " -n agent1"

if currentOS == 'posix':
	if os.access(pidfilename, os.F_OK):
		flumeFilepid = int(open(pidfilename).read())
		if os.path.exists("/proc/%s" % flumeFilepid): 
			#print "Process already running as PID ", flumeFilepid
			print >>sys.stderr, "Process already running as PID ", flumeFilepid
			sys.exit(1)
		else:
			#print "PID file exists but process is no longer running. Removing pidfile"
			print >>sys.stderr, "PID file exists but process is no longer running. Removing pidfile"
			os.remove(pidfilename)
	try:
		p = subprocess.Popen(['java', '-Xmx20m', '-Dlog4j.configuration=file:%s' % log4j,'-cp', classpath, 'org.apache.flume.node.Application', '-f', flumeconf, '-n', 'agent1'], stdout=subprocess.PIPE)
		flumepid = p.pid
		pidfile = open(pidfilename, 'w')
		pidfile.write(str(p.pid))
		pidfile.close()
		cmdout,cmderr =  p.communicate()
		retcode = p.wait()
		if retcode < 0:
			print >>sys.stderr, "Child was terminated by signal", -retcode
		else:
			print >>sys.stderr, "Child returned", retcode
	except OSError as e:
			print >>sys.stderr, "Execution failed:", e
else:
	if currentOS == 'nt':
		print "Windows based OS"
		flumeFilepid = int(open(pidfilename).read())
		tasklistcmd = 'tasklist /fi \"PID eq %i\"' % flumeFilepid		
		tasklist = subprocess.check_output(tasklistcmd).strip()
		if "INFO" not in tasklist:
			print "Flume or process with same PID already running"
		else:
			try:
				p = subprocess.Popen(['java', '-Xmx20m', '-Dlog4j.configuration=file:%s' % log4j,'-cp', classpath, 'org.apache.flume.node.Application', '-f', flumeconf, '-n', 'agent1'], stdout=subprocess.PIPE)
				flumepid = p.pid
				pidfile = open(pidfilename, 'w')
				pidfile.write(str(p.pid))
				pidfile.close()
				cmdout,cmderr =  p.communicate()
				retcode = p.wait()
				if retcode < 0:
					print >>sys.stderr, "Child was terminated by signal", -retcode
				else:
					print >>sys.stderr, "Child returned", retcode
			except OSError as e:
				print >>sys.stderr, "Execution failed:", e	
	else:
		print "Unsupported OS"
		sys.exit(1)
