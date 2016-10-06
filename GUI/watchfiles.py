#!/usr/bin/env python
# -*- coding: GBK -*-
'''
Create on 2016年9月19日
FileNme ：watchfiles
@author:Shuichon
doc docx pdf xls ppt 等文档格式化，监控制定文件夹，将符合制定格式的新文档复制到e:\wx目录
创建一个SqlLite3的数据库文件索引,用于存储文件MD5值，实现快速搜索及对比文件
'''
import sqlite3, os, hashlib, shutil, sys, time
import tkinter as tk
from tkinter import *
from tkinter.filedialog import *
from tkinter import messagebox

def u(s, encoding):
	if not s:
		return s
	if isinstance(s, unicode):
		return s
	else:
		return unicode(s, encoding)


def scanFile(dir, dbname, shijian ,respth):
	conn = sqlite3.connect(dbname)
	cu = conn.cursor()
	dpth=respth

	for f in os.listdir(dir):
		print (f)
		if os.path.isfile(f):
			if os.path.getmtime(f) < shijian:
				print ("符合时间")
				if os.path.splitext(f)[1].lower() in (
				'.doc', '.docx', '.pdf', '.pdfx', '.ppt', '.pptx', '.zip', '.rar', '.xls', '.xlsx'):
					print ("符合后缀")
					md5s = GetFileMd5(f)
					print (md5s)
					cu.execute("select count() from files where filemd5=?;", (md5s,))
					isnot = cu.fetchone()
					print (isnot[0])
					if isnot[0] == 0:
						print ("新文件")
						shutil.copy(f, dpth)
						cu.execute("insert into files(filepath,filename,filemd5,filesize) values(?,?,?,?);",
						           (dir, f, md5s, os.path.getsize(f)))
						conn.commit()


def GetFileMd5(filename):
	myhash = hashlib.md5()
	f = open(filename, 'rb')
	while True:
		b = f.read(8096)
		if not b:
			break
		myhash.update(b)
	f.close()
	return myhash.hexdigest()


def CreateDB(sqliteName):
	conn = sqlite3.connect(sqliteName)

	conn.text_factory = str

	cu = conn.cursor()

	sql = "create table IF NOT EXISTS files(filepath varchar(400),filename varchar(200),filemd5 varchar(40),filesize varchar(100));"
	cu.execute(sql)

	sql = "create index IF NOT EXISTS files_filepath  on  files(filepath);"
	cu.execute(sql)

	sql = "create index IF NOT EXISTS files_filename  on  files(filename);"
	cu.execute(sql)

	sql = "delete from files;"
	cu.execute(sql)
	conn.commit()

def start():
	work_dir = os.getcwd()
	sqliteName = os.path.join(work_dir, "files.db")
	print("YOUR DB IS @ " + sqliteName)
	CreateDB(sqliteName)
	path = askdirectory(parent=root, initialdir="/", title="请选择需要监控的文件夹!")
	print("监控的目录为：", path)
	respth = "e:\shuichon"
	if os.path.isdir(respth):
		print("符合特征的文件将保存于：", respth)
	else:
		os.mkdir(respth)
		print("符合特征的文件将保存于：", respth)
	while True:
		shijian = time.ctime()
		#设定循环时间，默认5min，300s
		time.sleep(300)
		print (shijian)
		scanFile(path, sqliteName, shijian, respth)

if __name__ == "__main__":
	root = tk.Tk()
	# withdraw()可以让多余的窗口消失。隐藏是:withdraw()函数。重新显示是：update()和deiconify()函数。
	# root.withdraw()
	bt_start = tk.Button(root, text="开始", command=start).pack()
	root.mainloop()