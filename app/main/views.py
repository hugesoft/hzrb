#coding:utf-8
from datetime import datetime
from flask import render_template, session, redirect, url_for, request
import urllib2
import urllib
import re

from .import main

#默认的路由函数
@main.route('/', methods=['GET', 'POST'])
def index():
	url = request.args.get('url', 'http://ehzrb.hz66.com/hzrb/')
	
	return getpage(url)

#得到缩略图的函数	
def getpage(url):
	html = urllib.urlopen(url)
	output = html.read()
	output = output.decode('gbk').encode('utf-8')
	
	restr = re.findall('<div class="left_Img">([\s\S]*)<SPAN id="leveldiv"',output)
	
	strinfo = re.compile('src="../../../../')
	result = strinfo.sub('src="http://ehzrb.hz66.com/',restr[0])
	
	return result