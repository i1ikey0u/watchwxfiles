#!/usr/bin/env python
# coding=utf-8

'''
使用添加群组的方法，查看是否是好友
有github仓库反馈即使你已被对方删除好友，依然可以拉对方入群
经过我2017-05-15的测试，使用手机微信，如果对方未添加你为好友，现在还是可以使用的。
'''

from urllib import request, parse
import os
# import urllib, urllib2
import re
# import cookielib
import time
import xml.dom.minidom
import json
import sys
import math

DEBUG = False

MAX_GROUP_NUM = 35  # 每个组人数

QRImagePath = os.getcwd() + '/qrcode.jpg'

tip = 0
uuid = ''

base_uri = ''
redirect_uri = ''

skey = ''
wxsid = ''
wxuin = ''
pass_ticket = ''
deviceId = 'e000000000000000'

BaseRequest = {}

ContactList = []
My = []

def getUUID():
	global uuid

	url = 'https://login.weixin.qq.com/jslogin'
	params = {
		'appid': 'wx782c26e4c19acffb',
		'fun': 'new',
		'lang': 'zh_CN',
		'_': int(time.time()),
	}

	req = request.urlopen(url = url, data = params)
	resp= req.read().decode('utf-8')

	# print resp

	# window.QRLogin.code = 200; window.QRLogin.uuid = "oZwt_bFfRg==";
	regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
	pm = re.search(regx, resp)

	code = pm.group(1)
	uuid = pm.group(2)

	if code == '200':
		return True

	return False

def showQRImage():
	global tip

	url = 'https://login.weixin.qq.com/qrcode/' + uuid
	params = {
		't': 'webwx',
		'_': int(time.time()),
	}

	req = request.urlopen(url = url, data = params)
	resp = req.read().decode('utf-8')

	tip = 1

	f = open(QRImagePath, 'wb')
	f.write(resp)
	f.close()

	if sys.platform.find('darwin') >= 0:
		os.system('open %s' % QRImagePath)
	elif sys.platform.find('linux') >= 0:
		os.system('xdg-open %s' % QRImagePath)
	else:
		os.system('call %s' % QRImagePath)

	print('请使用手机微信扫描二维码进行登录：')

def waitForLogin():
	global tip, base_uri, redirect_uri

	url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % (tip, uuid, int(time.time()))

	req = request.urlopen(url = url)
	resp = req.read().decode('utf-8')

	# window.code=500;
	regx = r'window.code=(\d+);'
	pm = re.search(regx, resp)

	code = pm.group(1)

	if code == '201':
		print('状态201，成功扫描,请在手机上点击确认以登录。')
		tip = 0
	elif code == '200':
		print('状态200，正在登录..')
		regx = r'window.redirect_uri="(\S+?)";'
		pm = re.search(regx, resp)
		redirect_uri = pm.group(1) + '&fun=new'
		base_uri = redirect_uri[:redirect_uri.rfind('/')]
	elif code == '408':
		pass
	# elif code == '400' or code == '500':

	return code

def login():
	global skey, wxsid, wxuin, pass_ticket, BaseRequest

	req = request.urlopen(url = redirect_uri)
	resp = req.read().decode('utf-8')

	'''
		<error>
			<ret>0</ret>
			<message>OK</message>
			<skey>xxx</skey>
			<wxsid>xxx</wxsid>
			<wxuin>xxx</wxuin>
			<pass_ticket>xxx</pass_ticket>
			<isgrayscale>1</isgrayscale>
		</error>
	'''

	doc = xml.dom.minidom.parseString(resp)
	root = doc.documentElement

	for node in root.childNodes:
		if node.nodeName == 'skey':
			skey = node.childNodes[0].data
		elif node.nodeName == 'wxsid':
			wxsid = node.childNodes[0].data
		elif node.nodeName == 'wxuin':
			wxuin = node.childNodes[0].data
		elif node.nodeName == 'pass_ticket':
			pass_ticket = node.childNodes[0].data

	# print 'skey: %s, wxsid: %s, wxuin: %s, pass_ticket: %s' % (skey, wxsid, wxuin, pass_ticket)

	if skey == '' or wxsid == '' or wxuin == '' or pass_ticket == '':
		return False

	BaseRequest = {
		'Uin': int(wxuin),
		'Sid': wxsid,
		'Skey': skey,
		'DeviceID': deviceId,
	}

	return True

def webwxinit():

	url = base_uri + '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (pass_ticket, skey, int(time.time()))
	params = {
		'BaseRequest': BaseRequest
	}

	req = request.urlopen(url = url, data = json.dumps(params))
	request.add_header('ContentType', 'application/json; charset=UTF-8')
	resp = req.read().decode('utf-8')

	if DEBUG == True:
		f = open(os.getcwd() + '/webwxinit.json', 'wb')
		f.write(resp)
		f.close()

	# print data

	global ContactList, My
	dic = json.loads(data)
	ContactList = dic['ContactList']
	My = dic['User']

	ErrMsg = dic['BaseResponse']['ErrMsg']
	if len(ErrMsg) > 0:
		print(ErrMsg)

	Ret = dic['BaseResponse']['Ret']
	if Ret != 0:
		return False
		
	return True

def webwxgetcontact():
	
	url = base_uri + '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (pass_ticket, skey, int(time.time()))

	req = request.urlopen(url = url)
	req.add_header('ContentType', 'application/json; charset=UTF-8')
	resp = req.read().decode('utf-8')

	if DEBUG == True:
		f = open(os.getcwd() + '/webwxgetcontact.json', 'wb')
		f.write(resp)
		f.close()

	# print data

	dic = json.loads(data)
	MemberList = dic['MemberList']

	# 倒序遍历..
	SpecialUsers = ['newsapp', 'fmessage', 'filehelper', 'weibo', 'qqmail', 'fmessage', 'tmessage', 'qmessage', 'qqsync', 'floatbottle', 'lbsapp', 'shakeapp', 'medianote', 'qqfriend', 'readerapp', 'blogapp', 'facebookapp', 'masssendapp', 'meishiapp', 'feedsapp', 'voip', 'blogappweixin', 'weixin', 'brandsessionholder', 'weixinreminder', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'officialaccounts', 'notification_messages', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'wxitil', 'userexperience_alarm', 'notification_messages']
	for i in range(len(MemberList) - 1, -1, -1):
		Member = MemberList[i]
		if Member['VerifyFlag'] & 8 != 0: # ���ں�/�����
			MemberList.remove(Member)
		elif Member['UserName'] in SpecialUsers: # �����˺�
			MemberList.remove(Member)
		elif Member['UserName'].find('@@') != -1: # Ⱥ��
			MemberList.remove(Member)
		elif Member['UserName'] == My['UserName']: # �Լ�
			MemberList.remove(Member)

	return MemberList

def createChatroom(UserNames):
	MemberList = []
	for UserName in UserNames:
		MemberList.append({'UserName': UserName})


	url = base_uri + '/webwxcreatechatroom?pass_ticket=%s&r=%s' % (pass_ticket, int(time.time()))
	params = {
		'BaseRequest': BaseRequest,
		'MemberCount': len(MemberList),
		'MemberList': MemberList,
		'Topic': '',
	}

	req = request.urlopen(url=url)
	req.add_header('ContentType', 'application/json; charset=UTF-8')
	resp = req.read().decode('utf-8')

	# print data

	dic = json.loads(resp)
	ChatRoomName = dic['ChatRoomName']
	MemberList = dic['MemberList']
	DeletedList = []
	for Member in MemberList:
		if Member['MemberStatus'] == 4: #���Է�ɾ����
			DeletedList.append(Member['UserName'])

	ErrMsg = dic['BaseResponse']['ErrMsg']
	if len(ErrMsg) > 0:
		print(ErrMsg)

	return (ChatRoomName, DeletedList)

def deleteMember(ChatRoomName, UserNames):
	url = base_uri + '/webwxupdatechatroom?fun=delmember&pass_ticket=%s' % (pass_ticket)
	params = {
		'BaseRequest': BaseRequest,
		'ChatRoomName': ChatRoomName,
		'DelMemberList': ','.join(UserNames),
	}

	req = request.urlopen(url=url)
	req.add_header('ContentType', 'application/json; charset=UTF-8')
	resp = req.read().decode('utf-8')

	dic = json.loads(resp)
	ErrMsg = dic['BaseResponse']['ErrMsg']
	if len(ErrMsg) > 0:
		print(ErrMsg)

	Ret = dic['BaseResponse']['Ret']
	if Ret != 0:
		return False
		
	return True

def addMember(ChatRoomName, UserNames):
	url = base_uri + '/webwxupdatechatroom?fun=addmember&pass_ticket=%s' % (pass_ticket)
	params = {
		'BaseRequest': BaseRequest,
		'ChatRoomName': ChatRoomName,
		'AddMemberList': ','.join(UserNames),
	}

	req = request.urlopen(url = url, data = json.dumps(params))
	req.add_header('ContentType', 'application/json; charset=UTF-8')
	resp = req.read().decode('utf-8')


	# print data

	dic = json.loads(resp)
	MemberList = dic['MemberList']
	DeletedList = []
	for Member in MemberList:
		if Member['MemberStatus'] == 4: #���Է�ɾ����
			DeletedList.append(Member['UserName'])

	ErrMsg = dic['BaseResponse']['ErrMsg']
	if len(ErrMsg) > 0:
		print(ErrMsg)

	return DeletedList

def main():

	# opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
	# urllib2.install_opener(opener)

	if getUUID() == False:
		print('uuid error')
		return

	showQRImage()
	time.sleep(1)

	while waitForLogin() != '200':
		pass

	os.remove(QRImagePath)

	if login() == False:
		print('login fail')
		return

	if webwxinit() == False:
		print('webwxinit fail')
		return

	MemberList = webwxgetcontact()

	MemberCount = len(MemberList)
	print('membercount' % MemberCount)

	ChatRoomName = ''
	result = []
	for i in range(0, int(math.ceil(MemberCount / float(MAX_GROUP_NUM)))):
		UserNames = []
		NickNames = []
		DeletedList = ''
		for j in range(0, MAX_GROUP_NUM):
			if i * MAX_GROUP_NUM + j >= MemberCount:
				break

			Member = MemberList[i * MAX_GROUP_NUM + j]
			UserNames.append(Member['UserName'])
			NickNames.append(Member['NickName'].encode('utf-8'))
                        
		print('��%s��...' % (i + 1))
		print(', '.join(NickNames))
		print('�س�������...')
		input()

		if ChatRoomName == '':
			(ChatRoomName, DeletedList) = createChatroom(UserNames)
		else:
			DeletedList = addMember(ChatRoomName, UserNames)

		DeletedCount = len(DeletedList)
		if DeletedCount > 0:
			result += DeletedList

		print('test' % DeletedCount)

		deleteMember(ChatRoomName, UserNames)

	# todo


	resultNames = []
	for Member in MemberList:
		if Member['UserName'] in result:
			NickName = Member['NickName']
			if Member['RemarkName'] != '':
				NickName += '(%s)' % Member['RemarkName']
			resultNames.append(NickName.encode('utf-8'))

	print('---------- ��ɾ���ĺ����б� ----------')
	print('\n'.join(resultNames))
	print('-----------------------------------')

# windows�±��������޸�
# http://blog.csdn.net/heyuxuanzee/article/details/8442718
class UnicodeStreamFilter:  
	def __init__(self, target):  
		self.target = target  
		self.encoding = 'utf-8'  
		self.errors = 'replace'  
		self.encode_to = self.target.encoding  
	def write(self, s):  
		if type(s) == str:  
			s = s.decode('utf-8')  
		s = s.encode(self.encode_to, self.errors).decode(self.encode_to)  
		self.target.write(s)  
		  
if sys.stdout.encoding == 'cp936':  
	sys.stdout = UnicodeStreamFilter(sys.stdout)

if __name__ == '__main__' :

	print('00')
	print('01')
	input()

	main()

	print('02')
	input()
