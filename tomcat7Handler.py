#!/usr/bin/env python
# coding=utf-8

import tomcatHandlerBase
import os

class  tomcat7Handler(tomcatHandlerBase.BaseHandler):
	"""docstring for  tomcat6Handler"""
	def __init__(self):
		super(tomcat7Handler,self).__init__()
		self.java_home = '/data/tools/jdk/jdk7'
		self.tomcat_home = '/data/tools/tomcat/tomcat7'
		os.environ['JAVA_HOME'] = self.java_home
