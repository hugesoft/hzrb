#coding:utf-8

#内容的类
class Content():
	title = ''
	stitle = ''
	stitle2 = ''
	content = ''
	auth = ''
	date = ''
	img = ''
	web_title = ''
	def __init__(self, title, content, web_title = '', 
	img='', stitle='', stitle2='', auth='', date=''):
		self.web_title = web_title
		self.title = title
		self.stitle = stitle
		self.stitle2 = stitle2
		self.content = content
		self.auth = auth
		self.date = date
		self.img = img