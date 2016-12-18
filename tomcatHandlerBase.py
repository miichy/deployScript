#!/usr/bin/env python
# coding=utf-8

import sys
import shutil
import os
import traceback
import commands
import time

class RunShellError(RuntimeError):
	"""docstring for RunShellError"""
	msg = ""
	def __init__(self, msg):
		self.msg = msg
		

class BaseHandler(object):
	"""docstring for BaseHandler"""
	app_name = ""
	git_root_dir = ""
	ant_build_sub_dir = ""
	java_home = ""
	tomcat_home = ""
	xdoclet_home = ""
	git_tag = ""
	src_dir = ""
	deploy_dir = ""
	war_filename = ""
	fixBuildScriptInfos = ()
	fixPropsFiles = ()

	def __init__(self):
		pass

	def error(self,str):
		print '\033[1;41;5m [ERROR] ',str,' \033[0m'

	def info(self,str):
		print '\033[1;36m [INFO] ',str,' \033[0m'

	def sleep(self,s):
		if s >= 0:
			for num in xrange(0,s):
				sys.stdout.write('\rWait for %d seconds...     '%(s - num))
				sys.stdout.flush()
				time.sleep(1)
		sys.stdout.write('\r                     \n')
		sys.stdout.flush()

	def run(self,cmd,showCmd = True,raiseOnError = True,workDir = ""):
		if showCmd:
			self.info("execute run : " + cmd)

		if workDir != "":
			os.chdir(workDir)

		(status,output) = commands.getstatusoutput(cmd)
		if status != 0 and raiseOnError:
			raise RunShellError(output)

		return(status,output.strip())

	def prepareParam(self):
		if self.git_root_dir == '':
			self.git_root_dir = self.app_name
		if self.war_filename == '':
			self.war_filename = "%s_*.war" % self.app_name
		if len(sys.argv) <= 1:
			error('Please Input the git branch or git tag name')
			sys.exit(1)

		self.git_tag = sys.argv[1]
		self.src_dir = "/data/apps/.src/%s" % self.git_root_dir
		self.deploy_dir = "/data/apps/webroot/%s" % self.app_name

		self.info("         Application Name(app_name) : %s" % self.app_name)
		self.info("           GIT项目名称(git_root_dir) : %s" % self.git_root_dir)
		self.info("            GIT 分支或TAG号(git_tag) : %s" % self.git_tag)
		self.info("      构建后war包文件名(war_filename) : %s" % self.war_filename)
		self.info("                   源码路径(src_dir) : %s" % self.src_dir)
		self.info("             目标部署路径(deploy_dir) : %s" % self.deploy_dir)
		self.info(" ANT构建配置子目录(ant_build_sub_dir) : %s" % self.ant_build_sub_dir)
		self.info("               JAVA path(java_home) : %s" % self.java_home)
		self.info("           TOMCAT path(tomcat_home) : %s" % self.tomcat_home)
		self.info("         xdoclet path(xdoclet_home) : %s" % self.xdoclet_home)

	def prepareDir(self,dir):
		if os.path.isdir(dir):
			self.info("Cleaning the directory %s" % dir)
			shutil.rmtree(dir)
		os.mkdir(dir)

	def chechoutCode(self):
		self.info("Checking out the code ...")
		(status,output) = self.run(cmd='git reset --hard HEAD',workDir = self.src_dir)
		print output
		(status,output) = self.run(cmd="git checkout %s" % self.git_tag,workDir = self.src_dir)
		print output
		self.run(cmd="git fetch --prune",workDir = self.src_dir)
		(status,output) = self.run(cmd="git checkout %s" % self.git_tag,workDir = self.src_dir)
		print output
		self.run(cmd="git pull",workDir = self.src_dir)
		(status,output) = self.run(cmd="git checkout %s" % self.git_tag,workDir = self.src_dir)
		print output

	def beforeBuild(self):
		self.info("prepare build script .... ")
		self.run(cmd="cp %s/build/%s/build.properties %s/build/%s/build.properties.bak" % \
			(self.src_dir,\
				self.ant_build_sub_dir,\
				self.src_dir,\
				self.ant_build_sub_dir),raiseOnError=False)
		for fixBuildScriptInfo in self.fixBuildScriptInfos:
			self.run(cmd="sed -i 's/%s/%s/g' %s/build/%s/%s" % \
				(fixBuildScriptInfo['oldText'].replace('/','\/'),\
					fixBuildScriptInfo['newText'].replace('/','\/'),\
					self.src_dir,\
					self.ant_build_sub_dir,\
					fixBuildScriptInfo['filePath']),raiseOnError=False)

	def build(self):
		self.info("Building ....   ")
		(status,output) = self.run(cmd='ant' ,workDir = "%s/build/%s" % (self.src_dir,self.ant_build_sub_dir))
		print output

	def shutdownTomecat(self):
		self.info("Shutdowning Tomcat ....")
		self.run(cmd="%s/bin/shutdown.sh" % self.tomcat_home,raiseOnError=False)
		self.sleep(5)
		(status,output) = self.run(cmd="ps -ef | grep %s |grep -v grep |grep -v cronolog | awk '{print $2}' " % (self.tomcat_home),raiseOnError = False)
		if output != "":
			self.info("Can not shutdown tomcat normally.5 seconds later,kill the tomcat pid : %s " % output)
			self.sleep(5)
			self.run(cmd="kill -9 %s" % output,raiseOnError=False)

	def install(self):
		self.info("Deploy the war package ...  ")
		self.run(cmd = "cp %s/release/%s  %s/%s.war" % (self.src_dir,self.war_filename,self.deploy_dir,self.app_name))
		(status,output) = self.run(cmd='jar -xvf %s.war' % self.app_name,workDir = "%s" % self.deploy_dir)
		print output
		self.run(cmd="rm %s/%s.war" % (self.deploy_dir,self.app_name),raiseOnError=False)
		self.run(cmd="echo '%s automatedly deploy the branch or tag %s' > /data/apps/.build/info/%s.txt " % (self.app_name,self.git_tag,self.app_name),raiseOnError = False)

	def afterInstall(self):
		for fixPropsFile in self.fixPropsFiles:
			self.run(cmd="sed -i 's/%s/%s/g' %s/%s" % \
				(fixPropsFile['oldText'].replace('/','\/'),\
					fixPropsFile['newText'].replace('/','\/'),\
					self.deploy_dir,\
					fixPropsFile['filePath']),raiseOnError=False)

	def startupTomcat(self):
		self.info("Startup Tomcat ....")
		(status,output) = self.run(cmd = "%s/bin/startup.sh" % self.tomcat_home,raiseOnError=False)
		print output

	def main(self):
		try:
			self.__init__()
			self.prepareParam()
			self.prepareDir(self.deploy_dir)
			self.prepareDir("%s/release" % self.src_dir)

			self.chechoutCode()
			self.beforeBuild()
			self.build()
			self.shutdownTomecat()
			self.install()
			self.afterInstall()
			self.startupTomcat()

			self.info("Successfully Deploy %s ( Branch or Tag : %s)" % (self.app_name,self.git_tag))
		except RunShellError,e:
			self.error("Failed to execute,error detail : \n" + e.msg)
			sys.exit(9999)
		except Exception,e:
			self.error("Failed to execute,error detail : \n" + traceback.format_exc())
			sys.exit(9999)



if __name__ == '__main__':
	b = BaseHandler()
	b.beforeBuild()	