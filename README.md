﻿# 关于 watchwxfiles
用于监测指定文件夹的变化，如果发现新的文件符合特定的规则，则将其拷贝/移动到指定文件夹。
非GUI版本如果需要监测E:\TEST\，则需要将脚本放置到该目录下，使用管理员权限运行。

现在监测对应目录下的办公文档：xls,doc,pdf,ppt,zip,rar等。会将其复制到e:\shuichon目录下。

在GUI文件夹中有GUI版本，并对代码的逻辑进行了优化 （2016-10-04 by shuichon）
修改了几处的逻辑问题
GUI版本和CMD版本现在均无需手工创建目录。(2016-10-06 by shuichon)

#关于 watchdog_of_wxgzh.py
需要的额外模块：urllib,BeautifulSoup
获取指定公众号，指定（关键字）的文章列表及内容
已经完成根据用户指定的关键字，搜索公众号，并采集该公众号最近10篇历史文章。
TODO 1，对文章简要进行展示/分析过滤
TODO 2，增加人性化的参数控制及选择

#关于 wechat-deleted-friends.py
从某个地方获取到的，放着好久了，不确定现在是否还可以用。
等watchdog_of_wxgzh.py完成后，再回头看看。