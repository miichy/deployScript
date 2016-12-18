#!/usr/bin/env python
# coding=utf-8

import tomcat7Handler

class DeployApp(tomcat7Handler.tomcat7Handler):
	def __init__(self):
		super(DeployApp,self).__init__()
		self.app_name = 'ABC'
		self.war_filename = "ABC.war"
		self.fixBuildScriptInfos = (\
			{'filePath':'build.properties',\
			'oldText':'tomcat.lib=/tomcat5/common/lib',\
			"newText":"tomcat.lib=%s/lib" % self.tomcat_home},\
			)
		self.fixPropsFile = (\
			{'filePath':'WEB-INF/conf/abc.properties',\
			'oldText':'1.1.1.1:3306',\
			"newText":"2.2.2.3:33033"},\
			{'filePath':'WEB-INF/conf/abc.properties',\
			'oldText':'dev',\
			"newText":"pro"},\
			)
if __name__ == "__main__":
	instance = DeployApp()
	instance.main()