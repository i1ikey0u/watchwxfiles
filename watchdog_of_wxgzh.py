#!/usr/bin/env python
# coding:utf-8
# environ: python3.6 32bit
# code by shuichon

'''
V3.0，获取指定公众号，指定（关键字）的文章列表
根据指定的关键字，搜索公众号，并采集该公众号最近10篇历史文章访问URL
根据指定的关键字，搜索公众号，并返回指定数量的公众号的访问URL
根据指定的关键字，搜索公众号，并返回搜索结果第1个公众号中，前10篇文章包含指定关键字的文章URL
根据指定的关键字，搜索公众号，并返回访问URL
TODO 优化执行流程，和丰富不同的参数组合的选择
'''

from urllib import request, parse
from bs4 import BeautifulSoup
import re, json, sys

# keyws = '测试' #调试参数
# nrurl = "http://weixin.sogou.com/weixin?type=2&query=" + parse.quote(keyws)
# gzhurl = "http://weixin.sogou.com/weixin?type=1&query=" + parse.quote(keyws)
# print(gzhurl)
# cont_pref = 'http://mp.weixin.qq.com/'

# 该参数似乎未使用
# headers = {
# 	'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
# 	              r'Chrome/44.0.2454.85 Safari/537.36 115Browser/6.0.3',
# 	'Connection': 'keep-alive'
# }


def get_gzh_url(soup):
	'''
	该函数暂未使用
	type2 通过搜狗主页“搜文章”搜索结果页面“相关公众号”，获取公众号地址URL
	'''
	# print(soup.prettify())
	# 获取公众号信息所在box
	gzhbox = soup.find_all('div', class_='gzh-box')
	gzhnum = len(gzhbox)
	print("获取到%i个box" % gzhnum)
	for i in range(gzhnum):
		gzhadr = gzhbox[i].find('a').attrs['href']
		print(gzhadr)
		#todo 需要设计一个返回值，返回公众号URL



def get_gzh_list(soup, gzh_num=1):
	'''
	该函数暂时被废弃了。
	type1 通过搜狗“搜公众号”，获取公众号地址，传入参数soup对象；
	gzh_num=：公众号数量；
	默认获取一个公众号，结果返回为数组gzh_list
	'''
	gzh_list = []
	# 当前页存在多少公众号
	gzhbox2 = soup.find_all('div', class_="gzh-box2")
	# 暂无实现，判断参数值，抓取几页公众号，默认抓取第一页的
	# todo 添加可选参数的判断功能
	if gzh_num >= len(gzhbox2):
		gzh_num = len(gzhbox2)
	print("从当前页获取 %i 个公众号。" % gzh_num)
	# 获取公众号访问地址
	for n in range(0, gzh_num):
		print(gzhbox2[0].find('a').attrs['href'])
		uni_gzh = gzhbox2[n].find('a').attrs['href']
		gzh_list.append(uni_gzh)
	return gzh_list


def get_warn(soup):
	'''频繁访问时，搜狗会需要二次验证，判断是否需要二次验证'''
	warn = soup.find_all('p', class_='ip-time-p')
	return len(warn)


def get_gzh_lists(keys, gzh_num=1):
	"""
	根据关键字keys，搜索公众号，未登录搜狗情况下，最多搜索10页，共计100个公众号。
	gzh_num为从搜索结果中提取多少个公众号，数组gzh_list，内容为公众号列表
	"""

	gzh_lists = []
	# 取整数页,+2中，1是列表下标+1问题，1是页码+1问题
	# TODO 存在一个问题，搜索结果首页公众号数量会在8 -10个浮动
	# 首先按照指定的关键字搜索第一页，并获取第一个公众号数量，和gzh_num对比，
	# 如果小于gzh_num。则直接返回gzh_num个公众号连接。如果大于gzh_num，则
	# 将搜索下一页，如果结果大于 gzh_num减去上一页的数量，则停止遍历下一页。
	# 否则继续遍历下一页搜索结果，并每次都gzh_num减去以及搜索的数量
	m = 1
	while gzh_num > 0:
		pages_url = "http://weixin.sogou.com/weixin?query=" + parse.quote(keys) + "&type=1&page=%s" % m
		print("当前搜索URL为：", pages_url)
		cots = request.urlopen(pages_url).read().decode('utf-8')
		gzhlist_soup = BeautifulSoup(cots, "html.parser")
		if get_warn(gzhlist_soup) > 0:
			print('发送请求过于频繁，存在二次验证，请手工打开搜狗微信搜索通过验证！')
			break
		else:
			gzhbox2 = gzhlist_soup.find_all('div', class_="gzh-box2")
			if len(gzhbox2) < gzh_num:
				num = len(gzhbox2)
				# gzh_num = gzh_num - num
			# 如果当前页匹配的公众号数目比gzh_num大，则直接返回gzh_num个公众号
			elif len(gzhbox2) > gzh_num:
				num = gzh_num
			print("从当前页获取 %i 个公众号。" % num)
			# 获取公众号访问地址
			for n in range(0, num):
				uni_gzh = gzhbox2[n].find('a').attrs['href']
				gzh_lists.append(uni_gzh)
			# 统一减去，从而跳出while循环
			gzh_num = gzh_num - num
			m += 1
	return gzh_lists

#TODO 获取到的文章列表是乱序的，文章顺序不对。
def get_gzh_content_top10(gzh_url, key='关键字'):
	"""
	传入公众号地址gzh_url，获取某个公众号最近的10篇链接，同时会调用grep_gzh函数，
	查看是否有关键字匹配结果
	"""

	infos = request.urlopen(gzh_url).read().decode('utf-8')
	# print(infos)
	# 返回的公众号文章列表为JS控制的JSON数据。所以需要获取json数据。
	# 获取json数据，该数据存有历史文章数据信息
	infos_soup = BeautifulSoup(infos, "html.parser")
	if get_warn(infos_soup) > 0:
		print('发送请求过于频繁，存在二次验证，请手工打开搜狗微信搜索通过验证！')
	else:
		json2 = infos_soup.find('script', type="text/javascript", text=re.compile("var msgList*"))
		print(len(json2))
		splitjson = json2.text.split('\r\n')
		# print(splitjson[8])
		jsoninfo = splitjson[8].replace("        var msgList = ", '')
		# print("jsoninfo: ", jsoninfo)
		#去除行末不可见的垃圾字符，防止出错
		jsonData = json.loads(jsoninfo[0:-1])
		# print("jsonData:", jsonData)
		#len(jsonData['list'])为10,即近期的10条内容
		print(len(jsonData['list'][0]))

		for l in range(len(jsonData['list'])):
			inf_u = jsonData['list'][l]['app_msg_ext_info']['content_url']
			# 字符串内有异常字符，需要将&amp; 替换为&
			inf_u = inf_u.replace("&amp;", "&")
			inf_u = "http://mp.weixin.qq.com" + inf_u
			# 调试参数，关闭显示
			# print('第 %d 篇的访问连接为：%s' % (l+1, inf_u))
			# 调用函数，查看是否存在指定的关键字
			grep_gzh(inf_u, key)


def grep_gzh(url, key):
	'''对文章中的关键字进行过滤，输出含有指定关键字的文章链接'''
	contents = request.urlopen(url).read().decode('utf-8')
	# print(contents)
	pat = re.compile(key)
	res = len(pat.findall(contents))
	if res > 0:
		print("发现 %i 处匹配的关键字" % res + '\n')
		print("公众号文章临时访问地址为：" + url + '\n')
	else:
		print("未发现存在匹配的关键字")

if __name__ == "__main__":
	print("f*ck wechat !")
	version = "version v3.0 by shuichon @ 2017年8月28日"
	# 参数判断函数
	if len(sys.argv) > 1:
		# 判断参数是否以‘-’开始，并且判断参数是否合法，然后继续操作
		if sys.argv[1].startswith('-'):
			option = sys.argv[1][1:]
			if option == 'v':
				print(version)
			elif option == 'h':
				print('''
	=================================================================
	|使用说明                                                        |
	|                                                               |
	| Options include:                                              |
	| -v         : The version number of the pychon script          |
	| -h         : Display this help                                |
	| -gzh       : 查找指定关键字的公众号,默认返回第一个                  |
	|   -gnum  : 可选参数,从结果中取gnum个公众号,进行内容识别,默认1        |
	|   -key   : 可选参数,搜索1个公众号,返回近10篇文章中,包含key的文章URL  |
	| -kws       : 内容识别关键字,查找包含kws的公众号文章                 |
	=================================================================
					''')
			elif option == 'v':
				print(version)
			elif option == 'gzh':
				print('当前参数数量为：', len(sys.argv[:]), sys.argv[:])
				print('搜索和"%s"相关的公众号' % sys.argv[2])
				# print ('当前参数为：' + sys.argv[2])
				if (len(sys.argv[:]) > 3) and (sys.argv[3][1:] == 'gnum'):
					option2 = sys.argv[3][1:]
					print('获取%i个微信公众号进行内容识别' % int(sys.argv[4]))
					# 按照设定参数，获取到公众号结果列表
					gzh_url_l = get_gzh_lists(keys=sys.argv[2], gzh_num=int(sys.argv[4]))
					# print(gzh_url_l)
					for l in gzh_url_l:
						print(l)
						# TODO ,暂时没有指定关键字功能
						# 输出当前公众号最近10篇公众号文章中含有“测试”关键字的文章URL。
						get_gzh_content_top10(l, key="测试")
				# 搜索1个公众号，并过滤其前10篇文章中是否有包含指定的关键字，并返回包含关键字的访问URL
				if (len(sys.argv[:]) > 3) and (sys.argv[3][1:] == 'key'):
					option2 = sys.argv[3][1:]
					print('使用 "%s" 关键字对搜索的微信公众号进行文章内容识别过滤' % sys.argv[4])
					gzh_url_l = get_gzh_lists(keys=sys.argv[2])
					for l in gzh_url_l:
						print(l)
						get_gzh_content_top10(l, key=sys.argv[4])
				else:
					print(get_gzh_lists(keys=sys.argv[2]))
			elif option == 'kws':
				option2 = sys.argv[2][1:]
				print('公众号内容识别关键字为：' + option2)
				gzh_url_l = get_gzh_lists(keys=sys.argv[2])
				print(gzh_url_l)
			else:
				print('''Unknown option !
	please input '-h' behind the script.''')
		else:
			print('''Unknown option !
	please input '-h' behind the script.''')
	else:
		print('Nothing done!')
