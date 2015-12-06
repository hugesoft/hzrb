#coding:utf-8
from datetime import datetime
from flask import render_template, session, redirect, url_for, request
import urllib2
import urllib
import  json
import re
import time
from datetime import datetime, timedelta
from array import *

from .import main
from content import HzlvPage
from content import Content
from content import Menu
from content import ItemList
from content import PageType
from HTMLParser import HTMLParser
import MySQLdb

####################################
#默认的路由函数
@main.route('/', methods=['GET', 'POST'])
@main.route('/main/', methods=['GET', 'POST'])
def index():
	return redirect('/hzrb/')
	
####################################
#main路由函数
@main.route('/hzrb/', methods=['GET', 'POST'])
@main.route('/hzwb/', methods=['GET', 'POST'])
def indexlist():
	import sys
	reload(sys)
	sys.setdefaultencoding('utf8')
	
	#当前当前的路由（比如/hzrb/或是/hzwb/
	cur_url = request.path 
	#得到当前的分类（日报还是晚报）	
	pagetype = PageType(cur_url)
	
	curr_time = time.strftime('%Y-%m/%d')
	url = request.args.get('url', 'http://ehzrb.hz66.com/' + pagetype.url + '/html/'+ curr_time + '/node_2.htm')

	#得到当前的列表
	data = getPageList(url)

	array_data = []
	arr = []	
	i = 0
	#得到内容页的url，用正则去改
	newurl =  url[:url.rindex('/')]
	for x in data:
		arr.append(newurl + '/node_' + str(i+2) + '.htm')
		#得到页面内容
		array_data.append(getpage(arr[i],i+1))
		i=i+1
		
	#得到往期的时间
	menu_data = getpagetime(365,cur_url)
	
	return render_template('main.html', page_data = array_data, menu_data = menu_data, 
	curr_page= url,curr_hzrb=cur_url,web_title=getWebTitle(cur_url))

####################################
#旅游版的路由
@main.route('/hzlv/', methods=['GET', 'POST'])
def indexhzlv():
	import sys
	reload(sys)
	sys.setdefaultencoding('utf8')

	#当前当前的路由（比如/hzrb/或是/hzwb/
	cur_url = request.path

	type = request.args.get('type', 1)
	curr_url = getHistryList(int(type))
	curr_time = time.strftime('%Y-%m/%d')
	#最近一版旅游或是度假区
	url = request.args.get('url', curr_url[0][0])

	#得到当前的列表
	data = getHzlvPageList(url,int(type))

	array_data = []
	arr = []
	i = 0

	j = int(data[2]) - 1
	#得到内容页的url，用正则去改
	newurl =  url[:url.rindex('/')]
	while(i < int(data[3])):
		arr.append(newurl + '/node_' + str(j+2) + '.htm')
		#得到页面内容
		array_data.append(getpage(arr[i],i+1))
		i=i+1
		j += 1

	#得到往期的时间
	menu_data = getpageHistry(curr_url)

	return render_template('hzlv.html', page_data = array_data, menu_data = menu_data,
	curr_page= url,curr_hzrb=cur_url,web_title=getWebTitle(cur_url),type=str(type))

###################################
#得到旅游版的第一版与版数
#得到目录列表的函数
def getHzlvPageList(url,type=1):
	html = urllib.urlopen(url)
	output = html.read()
	output = output.decode('gbk').encode('utf-8')

	#改内容(初次)
	restr = re.findall('<!--Right-->([\s\S]*)<!--Right End-->',output)
	if restr:
		restr2 = re.findall('title=\'(.*?)\'>[A-Z]\d\d',restr[0])

	arr_title = []
	i = 0
	j = 0
	index = 0
	hzlv_flag = None
	for x in restr2:
		j += 1
		if type == 1:
			hzlv_NO = re.findall('[A-Z]\d\d版：湖州旅游',x)
		else:
			hzlv_NO = re.findall('[A-Z]\d\d版：度假区时报',x)
		if hzlv_NO and hzlv_flag == None:
			hzlv_flag = hzlv_NO[0][0]
			index = j
		if hzlv_flag == x[0][0]:
			arr_title.append(x)
			i += 1

	return restr2,arr_title,index,i

####################################
#得到往期的时间（旅游）
def getpageHistry(data):
	menudata = []
	now = datetime.now()
	i = 0

	for x in data:
		menudata.append(Menu(x[2].strftime(getWeek(x[2].weekday())+' %Y年%m月%d日'),'/hzlv/?url='+x[0]))

	return menudata


##################################
#得到旅游版的数据库列表
def getHistryList(type = 1):
	import sys
	reload(sys)
	sys.setdefaultencoding('utf8')

	#数据库的打开
	db = MySQLdb.connect(db='mysql',host='127.0.0.1',user='root',passwd='enter0087!')
	db.autocommit(1)
	cur = db.cursor()
	cur.execute('show databases;')

	#使用数据库
	cur.execute('use mhzrb;')

	strSQL = ''
	print 'type' + str(type)
	#旅游
	if type == 1:
		strSQL = 'SELECT * FROM hzlv where type = 1 or type = 3 order by time desc limit 100;'
	else: #度假区
		strSQL = 'SELECT * FROM hzlv where type = 2 order by time desc limit 100;'
	cur.execute(strSQL)
	data = cur.fetchall()
	#关闭数据库
	cur.close()
	db.commit()
	db.close()

	return data


####################################
#版面的路由（旅游）
@main.route('/hzlvlist/', methods=['GET', 'POST'])
def hzlvlist():
	import sys
	reload(sys)
	sys.setdefaultencoding('utf8')
	cur_url = request.path

	type = request.args.get('type', 1)
	curr_url = getHistryList(int(type))
	curr_time = time.strftime('%Y-%m/%d')
	#最近一版旅游或是度假区
	url = request.args.get('url', curr_url[0][0])
	#得到当前的列表
	data = getHzlvPageList(url,int(type))

	arr = []
	i = 2
	j = int(data[2]) - 1
	#得到内容页的url，用正则去改
	spliurl =  url[:url.rindex('/')]
	for x in data[1]:
		newurl = spliurl + '/node_' + str(j+2) + '.htm'
		arr.append(ItemList(1,x,'/hzlv/?url='+newurl+'&type='+str(type)+'#PagePicMap'+str(i-1)))
		item = getItemList(newurl)
		for y in range(0, len(item[0])):
			arr.append(ItemList(0,item[0][y],'/content/?url=http://ehzrb.hz66.com/hzrb/'+item[1][y]))
		i = i+1
		j += 1

	#得到往期的时间
	menu_data = getpageHistry(curr_url)

	return render_template('pagelist.html', page_data = arr, menu_data = menu_data, curr_page = url,
	curr_hzrb=cur_url,web_title=getWebTitle('/hzrb/'),type=type)



####################################
#内容页的路由
@main.route('/content/', methods=['GET', 'POST'])
def content():
	import sys
	reload(sys)
	sys.setdefaultencoding('utf8')
	
	#当前当前的路由（比如/hzrb/或是/hzwb/
	cur_url = request.path 
	#得到当前的分类（日报还是晚报）	
	pagetype = PageType(cur_url)
		
	url = request.args.get('url', 'http://ehzrb.hz66.com/'+pagetype.url+'/html/2015-10/20/content_254527.htm')
	data = getcontent(url)
	
	return  render_template('content.html', page_data = data)

####################################
#内容页的路由
@main.route('/content2/', methods=['GET', 'POST'])
def content_TTS():
	import sys
	reload(sys)
	sys.setdefaultencoding('utf8')
	
	#当前当前的路由（比如/hzrb/或是/hzwb/
	cur_url = request.path 
	#得到当前的分类（日报还是晚报）	
	pagetype = PageType(cur_url)
		
	url = request.args.get('url', 'http://ehzrb.hz66.com/'+pagetype.url+'/html/2015-10/20/content_254527.htm')
	data = getcontent(url)
	
	tts_data = getTTS(data.content)
	
	return  render_template('content_TTS.html', page_data = data,tts_data=tts_data)


####################################	
#版面的路由	
@main.route('/page/', methods=['GET', 'POST'])
def pagelist():
	import sys
	reload(sys)
	sys.setdefaultencoding('utf8')
	
	#当前当前的路由（比如/hzrb/或是/hzwb/
	cur_url = request.path 
	#得到当前的分类（日报还是晚报）	
	pagetype = PageType(cur_url)
	
	url = request.args.get('url', 'http://ehzrb.hz66.com/'+pagetype.url+'/html/'+ time.strftime('%Y-%m/%d') + '/node_2.htm')
	data = getPageList(url)
	
	arr = []	
	i = 2
	#得到内容页的url，用正则去改
	newurl =  url[:url.rindex('/')]
	for x in data:
		arr.append('<a href=..?url=' + newurl + '/node_' + str(i) + '.htm>' + x + '</a>')
		i = i+1

	return render_template('pagelist.html', page_data = arr,web_title=getWebTitle(cur_url))

####################################	
#版面的路由	
@main.route('/list/', methods=['GET', 'POST'])
def itemslist():
	import sys
	reload(sys)
	sys.setdefaultencoding('utf8')
	
	cur_url = ''
	str_url = request.args.get('url')
	if str_url.find('ehzrb.hz66.com/hzrb/')>0:
		cur_url = 'hzrb'
	elif str_url.find('ehzrb.hz66.com/hzwb/')>0:
		cur_url = 'hzwb'
		
	url = request.args.get('url', 'http://ehzrb.hz66.com/'+cur_url+'/html/'+ time.strftime('%Y-%m/%d') + '/node_2.htm')
	data = getPageList(url)
	
	arr = []
	i = 2
	#得到内容页的url，用正则去改
	spliurl =  url[:url.rindex('/')]
	for x in data:
		newurl = spliurl + '/node_' + str(i) + '.htm'
		arr.append(ItemList(1,x,'/'+cur_url +'/?url='+newurl+'#PagePicMap'+str(i-1)))
		item = getItemList(newurl)	
		for y in range(0, len(item[0])):
			arr.append(ItemList(0,item[0][y],
			'/content/?url=http://ehzrb.hz66.com/'+cur_url+'/'+item[1][y]))	
		i = i+1
		
	#得到往期的时间
	menu_data = getpagetime(365,'/'+cur_url+'/')
	
	return render_template('pagelist.html', page_data = arr, menu_data = menu_data, curr_page = url,
	curr_hzrb='/'+cur_url+'/',web_title=getWebTitle('/'+cur_url+'/'))
	

####################################
#
#以下为功能函数
#
####################################
    
def my_urlencode(str1):
	reprStr = repr(str1).replace(r'\x', '%')
	return reprStr[1:-1]
	
def clearWord(str1):
	d = re.sub('[&nbsp;]+','',str1)
	d = re.sub('<[^>]+>','',d)	
	d = re.sub('▲▲+','',d)	
	
	p=re.compile('\s+')
	str_var=re.sub(p,'',d) 

	return str_var
	
####################################
#为逼格
#TTS 
def getTTS(txt):	
	char_len = 9
	max_len = char_len * 800
	
	clearTxt = clearWord(txt)
	str_total= my_urlencode(clearTxt )

	cur_len = len(str_total)
	str_value = ''

	url = 'http://apis.baidu.com/apistore/baidutts/tts?text='+str_total[0:max_len]+'&ctp=1&per=0'
	req = urllib2.Request(url)
	req.add_header("apikey", "a72db0e04b98e6e86481fc5424f85078")
	resp = urllib2.urlopen(req)
	content = resp.read()
	if(content):
		s = json.loads(content)
		str_value  += str(s['retData'])
		
		return str_value
		
####################################
#得是否日报
def getWebTitle(cur_url):	
	if cur_url == '/hzwb/':
		web_title = '湖州晚报手机版'
	else:
		web_title = '湖州日报手机版'
	return web_title
	
####################################
#得到往期的时间
def getpagetime(days,url):
	menudata = []
	now = datetime.now()
	i = 0
					
	while(i < days):
		delta = timedelta(days=i)
		n_days = now - delta
		i +=1
		
		menudata.append(Menu(n_days.strftime(getWeek(n_days.weekday()) + ' %Y年%m月%d日'),
		url + '?url=http://ehzrb.hz66.com' + url+ 'html/'+ n_days.strftime('%Y-%m/%d') + '/node_2.htm'))
	
	return menudata

####################################
#得到目录列表的函数
def getPageList(url):
	html = urllib.urlopen(url)
	output = html.read()
	output = output.decode('gbk').encode('utf-8')

	#改内容(初次)
	restr = re.findall('<!--Right-->([\s\S]*)<!--Right End-->',output)
	if restr:
		restr = re.findall('title=\'(.*?)\'>[A-Z]\d\d',restr[0])
		
	return restr

####################################
#得到版面列表的函数
def getItemList(url):
	html = urllib.urlopen(url)
	output = html.read()
	output = output.decode('gbk').encode('utf-8')

	#得到url
	restr = re.findall('<td valign="top" class="right_bg02"><div class="list">([\s\S]*) <!--Left End-->',output)
	if restr:
		outurl = re.findall('<a href=\'../../../(.*?)\'>',restr[0])
		outtitle = re.findall('.htm\'>(.*?)</a>',restr[0])
			
	return outtitle,outurl
			
####################################
#得到内容的函数	
def getcontent(url):
	html = urllib.urlopen(url)
	output = html.read()
	output = output.decode('gbk').encode('utf-8')

	#得网页大标标题	
	web_title = re.findall('<title>([\s\S]*)</title>',output)
	
	#改内容(初次)
	restr = re.findall('<div align="center" class="title">([\s\S]*)<div class="right_5">',output)
	strinfo = re.compile('src="../../../../')
	result = strinfo.sub('src="http://ehzrb.hz66.com/',restr[0])
	
	str_img = ''
	img_url = request.args.get('url')
	if img_url.find('ehzrb.hz66.com/hzrb/')>0:
		str_img = 'hzrb'
	elif img_url.find('ehzrb.hz66.com/hzwb/')>0:
		str_img = 'hzwb'
		
	#改内容(第二次，得图)
	pageimage = re.findall(str_img+'([\s\S]*) border=0><table><tr>',result)
	if pageimage:
		image= '<img src="http://ehzrb.hz66.com/'+str_img+'/'+ pageimage[0] + '"width = 100% border=0>'
	else:
		image = None
	
	#改内容(二次得title）
	restr = re.findall('<h1>([\s\S]*)<\/h1>',result)
	title = restr[0]
	
	#改内容(二次得stitle）
	restr = re.findall('<h3>([\s\S]*)<\/h3>',result)
	stitle = restr[0]
	
	#改内容(二次得内容）
	restr = re.findall('<div class="content">([\s\S]*)<\/div>',result)
	content = restr[0]
	
	contentObj=Content(title,content,'',image,stitle)
	
	return contentObj
	
####################################	
#得到缩略图的函数	 #PagePicMap1
def getpage(url,Map_id=1):
	html = urllib.urlopen(url)
	output = html.read()
	output = output.decode('gbk').encode('utf-8')
	
	#用正则得到得页面（报纸的图）
	restr = re.findall('<div class="left_Img">([\s\S]*)<SPAN id="leveldiv"',output)
	strinfo = re.compile('src="../../../../')
	result = None
	if restr:
		result = strinfo.sub('src="http://ehzrb.hz66.com/',restr[0])
	
	#得到内容页的url，用正则去改
	newurl =  url[:url.rindex('/')]
	strinfo = re.compile('href=\'content_')
	###########################
	#这里content的路径可能还需要改
	###########################
	if result:
		result = strinfo.sub('href=\'../content?url=' + newurl + '/content_',result)

	#改图大小
	strinfo = re.compile('width=330px height=530px')
	if result:
		result = strinfo.sub('width=330px height=506px',result)
	
	#改map1
	strinfo = re.compile('PagePicMap1')
	if result:
		result = strinfo.sub('PagePicMap'+str(Map_id),result)
	
	#改PagePicMap的
	strinfo = re.compile('<img useMap=')
	if result:
		result = strinfo.sub('<img id=PagePicMap'+str(Map_id) +' useMap=',result)
	
	class count_add:
		s = 0
		def __init__(self,s):
			self.s = s
	
	a = count_add(0)

#用于计算number,的数字			
	def _add1(matched):
 		intStr = matched.group("number");
 		
 		if intStr:
			intValue = int(intStr);
			#第9位时，计数清0
			if a.s == 9:
				a.s = 0
			if a.s % 2 == 0:
				addedValue = int(round(intValue/1.17575758));		
			else:
			 	addedValue = int(round(intValue/1));
	
			a.s = a.s+1	
			addedValueStr = str(addedValue)+',';
		
		return addedValueStr;
	
	#用于计算number’的数字	（最后一位）	
	def _add2(matched):
		intStr = matched.group("number");
		
		if intStr:
			intValue = int(intStr);

			addedValue = int(round(intValue/1));

			a.s = 0
			addedValueStr = str(addedValue)+'\'';
		 
		return addedValueStr; 	 

	if result:
		result = re.sub('(?P<number>\d+)[,]',_add1,result)
		result = re.sub('(?P<number>\d+)[\']',_add2,result)
		
	return result

#用于计算周几
def getWeek(week):
	strValue=''
	
	if 6 == week:
		strValue = "星期日"
	elif 0 == week:
		strValue = "星期一"
	elif 1 == week:
		strValue = "星期二"
	elif 2 == week:
		strValue = "星期三"
	elif 3 == week:
		strValue = "星期四"		
	elif 4 == week:
		strValue = "星期五"
	elif 5 == week:
		strValue = "星期六"			
								
	return strValue
    
    