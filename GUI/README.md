# watchwxfiles
用于监测指定文件夹的变化，如果发现新的文件符合特定的规则，则将其拷贝/移动到指定文件夹
。本版本监测对应目录下的办公文档：xls,doc,pdf,ppt,zip,rar等。会将其复制到e:\shuichon 目录下。

使用管理员权限运行，选择要检测到用文件夹，点击“开始”按钮，最小化程序即可。

请注意，GUI版本适用了python内置的tkinter。所以你需要使用python3 版本，因为python2.7中的tkinter升级到pytnon3.5后，变化比较大，无法兼容。