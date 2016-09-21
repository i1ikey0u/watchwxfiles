#!/usr/bin/env python
# -*- coding: GBK -*-
'''
Create on 2016年9月19日
FileNme ：watchfiles
@author:Shuichon
doc docx pdf xls ppt 等文档格式化，监控制定文件夹，将符合制定格式的新文档复制到e:\wx目录
创建一个SqlLite3的数据库文件索引,用于存储文件MD5值，实现快速搜索及对比文件
'''
import sqlite3,os,hashlib,shutil,sys,time

def u(s, encoding):
    if not s:
        return s
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, encoding)

def scanFile(dir,dbname,shijian):
    conn=sqlite3.connect(dbname)
    cu=conn.cursor()
    dpth="e:\wx"
    for f in os.listdir(dir):
        print (f)
        if os.path.isfile(f):
            if os.path.getmtime(f)<shijian:
                print ("符合时间")
                if os.path.splitext(f)[1].lower() in ('.doc','.docx','.pdf','.pdfx','.ppt','.pptx','.zip','.rar','.xls','.xlsx'):
                    print ("符合后缀")
                    md5s=GetFileMd5(f)
                    print (md5s)
                    cu.execute("select count() from files where filemd5=?;",(md5s,))
                    isnot =cu.fetchone()
                    print (isnot[0])
                    if isnot[0] ==0:
                        print ("新文件")
                        shutil.copy(f,dpth)
                        cu.execute("insert into files(filepath,filename,filemd5,filesize) values(?,?,?,?);",(dir, f, md5s,os.path.getsize(f)))
                        conn.commit()


def GetFileMd5(filename):
    myhash = hashlib.md5()
    f = open(filename,'rb')
    while True:
        b = f.read(8096)
        if not b :
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

    sql= "create index IF NOT EXISTS files_filepath  on  files(filepath);"
    cu.execute(sql)

    sql= "create index IF NOT EXISTS files_filename  on  files(filename);"
    cu.execute(sql)

    sql = "delete from files;"
    cu.execute(sql)
    conn.commit()
        
if __name__ == "__main__":
    work_dir=os.getcwd()
    sqliteName=os.path.join(work_dir,"files.db")
    print ("YOUR DB IS @ "+sqliteName)
    CreateDB(sqliteName)
    while True:
        shijian = time.time()
        time.sleep(300)
        print (shijian)
        scanFile(work_dir,sqliteName,shijian)
