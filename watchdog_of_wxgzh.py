#!/usr/bin/env python
# coding:utf-8
# environ: python3.6 32bit
# code by shuichon

'''
V1.0，获取指定公众号，指定（关键字）的文章列表及内容
已经完成根据用户指定的关键字，搜索公众号，并采集该公众号最近10篇历史文章。
TODO 1，对文章简要进行展示/分析过滤
TODO 2，增加人性化的参数控制及选择
'''

from urllib import request, parse
from bs4 import BeautifulSoup
import re, json

keyws = '胡说八道'
nrurl = "http://weixin.sogou.com/weixin?type=2&query=" + parse.quote(keyws)
gzhurl = "http://weixin.sogou.com/weixin?type=1&query=" + parse.quote(keyws)
# print(gzhurl)
cont_pref = 'http://mp.weixin.qq.com/'

headers = {
	'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
	              r'Chrome/44.0.2454.85 Safari/537.36 115Browser/6.0.3',
	'Connection': 'keep-alive'
}


'''type2 通过搜狗主页“搜文章”搜索结果页面“相关公众号”，获取公众号地址URL'''


def get_gzh_url(soup):
	# print(soup.prettify())
	# 获取公众号信息所在box
	gzhbox = soup.find_all('div', class_='gzh-box')
	gzhnum = len(gzhbox)
	print("获取到%i个box" % gzhnum)
	for i in range(gzhnum):
		gzhadr = gzhbox[i].find('a').attrs['href']
		print(gzhadr)
		#todo 需要设计一个返回值，返回公众号URL


'''type1 通过“搜公众号”，获取公众号地址，默认获取一个公众号，结果返回为数组'''


def get_gzh_list(soup, page_num2=1, gzh_num=2):
	# 获取公众号信息所在box
	gzh_list = []
	# 当前页存在多少公众号
	gzhbox2 = soup.find_all('div', class_="gzh-box2")
	# 暂无实现，判断参数值，抓取几页公众号，默认抓取第一页的
	# todo 添加可选参数的判断功能
	if gzh_num >= len(gzhbox2):
		gzh_num = len(gzhbox2)
	print("从当前页获取 %i 个公众号。" % gzh_num-1)
	# 获取公众号访问地址
	for n in range(1, gzh_num):
		uni_gzh = gzhbox2[n].find('a').attrs['href']
		gzh_list.append(uni_gzh)
	return gzh_list



'''频繁访问时，搜狗会需要二次验证，判断是否需要二次验证'''


def get_warn(soup):
	warn = soup.find_all('p', class_='ip-time-p')
	return len(warn)


'''根据关键字，搜索公众号，搜狗未登录情况下，最多搜索10页，共计100个公众号'''


def get_gzh_lists(keys, page_num=1):
	gzh_list = []
	for m in range(1, page_num):
		print('第 %i 页公众号列表：' % m)
		# pages_url='http://weixin.sogou.com/weixin?query=%E8%83%A1%E8%AF%B4%E5%85%AB%E9%81%93&_sug_type_=&sut=6832&lkt=1%2C1493816955341%2C1493816955341&s_from=input&_sug_=y&type=1&sst0=1493816955443&page='+str(i)+'&ie=utf8&w=01019900&dr=1'
		pages_url = "http://weixin.sogou.com/weixin?query=" + parse.quote(keys) + "&type=1&page=%s" % m
		print("搜索URL为：", pages_url)
		# list_page = request.Request(pages_url, headers)
		cots = request.urlopen(pages_url).read().decode('utf-8')
		print('当前结果页内容长度为：', len(cots))
		# print(cots)
		gzhlist_soup = BeautifulSoup(cots, "html.parser")
		# 判断是否存在二次验证
		if get_warn(gzhlist_soup) > 0:
			print('发送请求过于频繁，存在二次验证，请手工打开搜狗微信搜索通过验证！')
			break
		else:
			# get_gzh_list的返回值也是一个列表，该处存在一个可选参数gzhnum2，可以选择返回公众号数量
			gzh_list = get_gzh_list(gzhlist_soup)
			print(gzh_list)
	return gzh_list


'''获取某个公众号最近的10篇链接'''


def get_gzh_content_top10(gzh_url):
	# 新材料在线 测试内容
	# url = '''http://mp.weixin.qq.com/profile?src=3&timestamp=1494742376&ver=1&signature=Tlgr--ZADlvcXc9zsJyf56xe932gmB*ecH8O1gg9o5xO4cjSYXEQUZ7oKRaWbYJbGyRf8a*nbwpjH4OE0Y7*sA=='''
	infos = request.urlopen(gzh_url).read().decode('utf-8')
	# print(infos)
	# 返回的公众号文章列表为JS控制的JSON数据。所以需要获取json数据。
	# 获取json数据，该数据存有历史文章数据信息
	infos_soup = BeautifulSoup(infos, "html.parser")
	# json1 = infos_soup.find_all(text=re.compile("var msgList*"))
	json2 = infos_soup.find('script', type="text/javascript", text=re.compile("var msgList*"))
	print(len(json2))
	# print("json2: ", json2.text)
	#json内容在获取到内容中的第9号，即第8位
	# splitjson = str(json2.text).split('\r\n')
	splitjson = json2.text.split('\r\n')
	# print(splitjson[8])
	jsoninfo = splitjson[8].replace("        var msgList = ", '')
	# print("jsoninfo: ", jsoninfo)
	#去除行末不可见的垃圾字符，防止出错
	jsonData = json.loads(jsoninfo[0:-1])
	# print("jsonData:", jsonData)
	#len(jsonData['list'])为10,即近期的10条内容
	print(len(jsonData['list'][0]))

	for i in range(len(jsonData['list'])):
		inf_u = jsonData['list'][i]['app_msg_ext_info']['content_url']
		#字符串内有异常字符，需要将&amp; 替换为&
		inf_u = inf_u.replace("&amp;", "&")
		print('第 %d 篇的访问连接为：%s' % (i+1, inf_u))

if __name__ == "__main__":
	print("f*ck wechat !")
	# 搜索关键字，只返回2-1 页的公众号
	gzh_url_l = get_gzh_lists("胡说八道", page_num=2)
	print("共发现 %i 个文章访问地址", len(gzh_url_l))
	for i in gzh_url_l:
		get_gzh_content_top10(i)
