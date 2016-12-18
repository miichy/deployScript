#!/usr/bin/env python
# coding=utf-8

import tomcatHandlerBase
import os

class  tomcat6Handler(tomcatHandlerBase.BaseHandler):
	"""docstring for  tomcat6Handler"""
	def __init__(self):
		super(tomcat6Handler,self).__init__()
		self.java_home = '/data/tools/jdk/jdk6'
		self.tomcat_home = '/data/tools/tomcat/tomcat6'
		os.environ['JAVA_HOME'] = self.java_home
