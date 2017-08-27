# 关于 WATCHWXFILES
用于监测指定文件夹的变化，如果发现新的文件符合特定的规则，则将其拷贝/移动到指定文件夹。
非GUI版本如果需要监测E:\TEST\，则需要将脚本放置到该目录下，使用管理员权限运行。

现在监测对应目录下的办公文档：xls,doc,pdf,ppt,zip,rar等。会将其复制到e:\shuichon目录下。

在GUI文件夹中有GUI版本，并对代码的逻辑进行了优化 （2016-10-04 by shuichon）
修改了几处的逻辑问题
GUI版本和CMD版本现在均无需手工创建目录。(2016-10-06 by shuichon)

#关于 WATCHDOG_OF_WXGZH.PY

#TIPS:
需要安装的额外模块：urllib,BeautifulSoup

V3.0，获取指定公众号，指定（关键字）的文章列表
根据指定的关键字，搜索公众号，并采集该公众号最近10篇历史文章。
根据指定的关键字，搜索公众号，并返回指定数量的公众号的访问URL
根据指定的关键字，搜索公众号，并返回搜索结果第1个公众号中，前10篇文章包含指定关键字的文章URL
根据指定的关键字，搜索公众号并返回访问URL
TODO 优化执行流程，和丰富不同的参数组合的选择

##使用说明：
显示当前版本信息:
	python.exe ./watchdog_of_wxgzh.py -v

显示帮助信息:
	python.exe ./watchdog_of_wxgzh.py -h

以“测试”为关键字，搜索公众号，并返回搜索结果中的前5个公众号访问URL:
	python.exe ./watchdog_of_wxgzh.py -gzh 测试 -gnum 5

以“测试”为关键字，搜索公众号，并返回第1个公众号的访问URL，以及该公众号前10篇文章中，包含“内容关键字”的文章访问URL:
	python.exe ./watchdog_of_wxgzh.py -gzh 测试 -key 内容关键字

搜索包含“内容关键字”的公众号，并返回结果中第1个公众号的访问URL
	python.exe ./watchdog_of_wxgzh.py -kws 内容关键字

#2017年8月28日，情人节当然要“啪啪啪”敲代码了。

#关于 WECHAT-DELETED-FRIENDS.PY
从某个地方获取到的，放着好久了，不确定现在是否还可以用。
等watchdog_of_wxgzh.py完成后，再回头看看。