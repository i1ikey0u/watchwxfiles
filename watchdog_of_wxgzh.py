#!/usr/bin/env python
# coding:utf-8
# environ: python3.6 32bit
# code by shuichon
'''
V3.2，优化了执行流程和操作的简易性，修补了几个bug
'''

from urllib import request, parse
from bs4 import BeautifulSoup
import re, json, sys


def get_warn(soup):
	'''
	频繁访问时，搜狗会需要二次验证，判断是否需要二次验证
	'''
	warn = soup.find_all('p', class_='ip-time-p')
	return len(warn)


def get_gzh_lists(keys, gzh_num=1):
	"""
	根据关键字keys，搜索公众号，未登录搜狗情况下，最多搜索10页，共计100个公众号。
	gzh_num为从搜索结果中提取多少个公众号，数组gzh_list，内容为公众号列表
	"""

	gzh_lists = []
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
			elif len(gzhbox2) > gzh_num:
				num = gzh_num
			print("从当前页获取 %i 个公众号。" % num)
			for n in range(0, num):
				uni_gzh = gzhbox2[n].find('a').attrs['href']
				gzh_lists.append(uni_gzh)
			gzh_num = gzh_num - num
			m += 1
	return gzh_lists



def get_gzh_content_top10(gzh_url):
	"""
	传入公众号地址gzh_url，获取某个公众号最近的10篇链接
	以列表方式，返回该公众号最近10篇的文章访问地址
	该函数不再用于文章内容的过滤，转由grep_gzh()落实
	"""

	gzh_wz_l = []

	infos = request.urlopen(gzh_url).read().decode('utf-8')
	infos_soup = BeautifulSoup(infos, "html.parser")
	if get_warn(infos_soup) > 0:
		print('发送请求过于频繁，存在二次验证，请手工打开搜狗微信搜索通过验证！')
	else:
		json2 = infos_soup.find('script', type="text/javascript", text=re.compile("var msgList*"))
		splitjson = json2.text.split('\r\n')
		jsoninfo = splitjson[8].replace("        var msgList = ", '')
		jsonData = json.loads(jsoninfo[0:-1])

		for l in range(len(jsonData['list'])):
			inf_u = jsonData['list'][l]['app_msg_ext_info']['content_url']
			inf_u = inf_u.replace("&amp;", "&")
			inf_u = "http://mp.weixin.qq.com" + inf_u
			gzh_wz_l.append(inf_u)
	return gzh_wz_l


def grep_gzh(url, key):
	'''
	对给定文章中的关键字进行过滤，输出含有指定关键字的文章链接
	'''
	contents = request.urlopen(url).read().decode('utf-8')
	pat = re.compile(key)
	res = len(pat.findall(contents))
	if res > 0:
		print("发现 %i 处匹配的关键字" % res + '\n')
		print("公众号文章临时访问地址为：" + url + '\n')
	else:
		print("未发现存在匹配的关键字")

if __name__ == "__main__":
	print("f*ck wechat !")
	version = "version v3.2 by shuichon @ 2017年8月28日"
	if len(sys.argv) > 1:
		if sys.argv[1].startswith('-'):
			option = sys.argv[1][1:]
			if option == 'v':
				print(version)
			elif option == 'h':
				print('''
	=================================================================
	|                  使用说明:                                     |
	| 参数说明:                                                      |
	| -v         : 当前版本                                          |
	| -h         : 显示本帮助说明                                     |
	| -gzh       : 查找指定关键字的公众号,默认返回第一个                  |
	|   -gnum  : 可选参数,从结果中取gnum个公众号,默认1                   |
	|   -key   : 可选参数,搜索1个公众号,返回近10篇文章中,包含key的文章URL  |
	| -kws       : 内容识别关键字,查找包含kws的公众号文章，               |
	|   -gnum  : 可选参数,在结果中取gnum个公众号,默认1                   |
	=================================================================
					''')
			elif option == 'v':
				print(version)
			elif option == 'gzh':
				print('当前参数数量为：', len(sys.argv[:]), sys.argv[:])
				print('搜索和"%s"相关的公众号' % sys.argv[2])
				if (len(sys.argv[:]) > 3) and (sys.argv[3][1:] == 'gnum'):
					option2 = sys.argv[3][1:]
					print('获取%i个微信公众号进行内容识别' % int(sys.argv[4]))
					gzh_url_l = get_gzh_lists(keys=sys.argv[2], gzh_num=int(sys.argv[4]))
					for l in gzh_url_l:
						print("当前公众号访问URL:")
						print(l)
						print("当前公众号最近10篇公众号文章URL:")
						for wz in get_gzh_content_top10(l):
							print(wz)
				elif (len(sys.argv[:]) > 3) and (sys.argv[3][1:] == 'key'):
					option2 = sys.argv[3][1:]
					print('使用 "%s" 关键字搜索微信公众号' % sys.argv[2])
					gzh_url_l = get_gzh_lists(keys=sys.argv[2])
					for l in gzh_url_l:
						print(l)
						for wz in get_gzh_content_top10(l):
							grep_gzh(wz, key=sys.argv[4])
				else:
					print(get_gzh_lists(keys=sys.argv[2]))
			elif option == 'kws':
				option2 = sys.argv[2]
				print('公众号内容识别关键字为：' + option2)
				if len(sys.argv[:]) == 3:
					print('默认获取1个微信公众号')
					gzh_url_l = get_gzh_lists(keys=sys.argv[2])
					print(gzh_url_l)
				elif (len(sys.argv[:]) > 3) and (sys.argv[3][1:] == 'gnum') :
					option3 = sys.argv[3]
					print('获取%i个微信公众号' % int(sys.argv[4]))
					gzh_url_l = get_gzh_lists(keys=sys.argv[2], gzh_num=int(sys.argv[4]))
					print(gzh_url_l)
				for l in gzh_url_l:
					print("当前公众号最近10篇公众号文章URL:")
					for wz in get_gzh_content_top10(l):
						print(wz)
			else:
				print('''Unknown option !
	please input '-h' behind the script.''')
		else:
			print('''Unknown option !
	please input '-h' behind the script.''')
	else:
		print('Nothing done!')
