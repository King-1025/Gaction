#!/usr/bin/env python3
# -*- coding: utf-8; -*-

'''
# Desc: 科研在线网盘接口 
# Date: 2020.04.13
# Ver: 0.1.0
# By: king
'''

import os
import re
import sys
import json
import urllib
import requests

import random
import string

from contextlib import closing

from data import DATA
from data import ESC_ZONE as ZONE
from data import ESC_HOST as HOST
from data import ESC_PRID as PRID
from data import ESC_LOCAL_PATH as LPATH


# 科研在线 http://ddl.escience.cn/king1025/list#path=%2F11015861
class Escience:
    def __init__(self, name, password, parentRid=PRID):
        self.name = name
        self.password = password
        self.parentRid = parentRid  

        self.isLogin = False
        self.data=None

        self.header = DATA["header"]
        self.session = requests.Session()

    def auth(self):
        url = DATA["api"]["auth"]["url"]
        data = DATA["api"]["auth"]["data"]
        data["userName"] = self.name
        data["password"] = self.password
        try:
            r = self.session.post(url, headers=self.header, data=data, verify=False, allow_redirects=False)
            r_location = r.headers['Location']
            self.session.post(url=r_location, headers=self.header,verify=False,allow_redirects=False)
            self.isLogin = True
 #           print('redirect url:%s' % r_location)
 #           print("auth success!\n")
        except:
            print("auth failed!\n")
            sys.exit(1)

    def login(self):
        url = DATA["api"]["login"]["url"]
        data = DATA["api"]["login"]["data"]
        r = self.session.get(url, params=data, headers=self.header, verify=True)
        if r.status_code != 200:
            print("login_pages response nO!")
            sys.exit(1)
        else:
    #        print('login_page response oK!')
            self.auth()

    def check_team(self, tid):
        url = DATA["api"]["check_team"]["url"]
        url="%s&teamId=%s" % (url, tid)
        r = self.session.get(url=url, headers=self.header)
        #print(r.text)
        if r.status_code == 200:
           data=str(r.text)
           if data == "true":
              return True
        return False

    def create_team(self, name, tid=None, force=False, max=10):
        rtid, i = tid, 0
        while True:
          if rtid is None:
             rtid = "".join(random.sample(string.ascii_lowercase + string.digits, 8))
             if tid is not None:
                rtid="%s%s" %(tid, rtid)

          print("check rtid: %s..." % rtid)
          if not self.check_team(rtid):
            print("failed!")
            if tid is not None and force is False:
                 sys.exit(1)
            else:
                 print("gen rtid again...\n")
                 rtid=None
          else:
             print("success!\n")
             break
          if i < max:
            i+=1
          else:
            print("beyond max: %d!\n" % max)
            sys.exit(1)

        print("send request...")
        url = DATA["api"]["create_team"]["url"]
        data = DATA["api"]["create_team"]["data"]
        data["teamName"] = name
        data["teamId"] = rtid
        try:
            r = self.session.post(url, headers=self.header, data=data, verify=False, allow_redirects=False)
            r_location = r.headers['Location']
            self.session.post(url=r_location, headers=self.header,verify=False,allow_redirects=False)
            print('redirect url:%s' % r_location)
            print("success!\n")
            return rtid
        except Exception as e:
            print("create team failed!\n")
            print(e)
            sys.exit(1)

    def quit_team(self, zone=None):
        url = DATA["api"]["quit_team"]["url"]
        data = DATA["api"]["quit_team"]["data"]
        if zone:
          data["teamName"] = str(zone)
        else:
          data["teamName"] = str(ZONE)
        r = self.session.post(url=url, headers=self.header, data=data)
        if r.status_code == 200:
           sd=json.loads(r.text)
           print(sd)
           url = DATA["api"]["quit_team"]["url2"]
           r = self.session.post(url=url, headers=self.header, data=data)
           if r.status_code == 200:
              self.data=json.loads(r.text)
        return self

    def mkdir(self, name, prid=None):
        rid=self.parentRid
        if prid:
           rid=str(prid)
        return self.base_mkdir(name, rid)

    def upload(self, path, name, parentRid=None):
        prid=parentRid
        if prid is None:
           prid=self.parentRid
        loca=os.path.join(path, name)
        size=os.path.getsize(loca)
        size=self.bytes2human(size)
        print("prid: %s" % prid)
        print("file：%s" % name)
        print("size：%s" % size)
        print("path：%s" % loca)
        print("upload...")
        return self.base_upload(path, name, prid)

# 批量删除  http://ddl.escience.cn/king1025/list?func=deleteResources&rids%5B%5D=11271884&rids%5B%5D=11271885
    def delete(self, rid):
        url = DATA["api"]["delete"]["url"]
        url = "%s&rid=%s" % (url, str(rid))

        r = self.session.get(url=url, headers=self.header)
        if r.status_code == 200:
           data=json.loads(r.text)
           print(data)

# http://ddl.escience.cn/king1025/list
# post
# fileName=test.sh&rid=11271886&parentRid=11015861&func=editFileName
    def rename(self):
        pass

# http://ddl.escience.cn/king1025/fileManager
# post
# func=moveSelected&originalRids=11271886&targetRid=0
    def move(self, rid):
        pass

    def query(self):
        return self.base_query(self.parentRid)
    
    def download(self, name, rid, path=LPATH, _check=True):
        return self.base_download(name, rid, path, _check)

    def base_mkdir(self, name, prid, zone=None):
        url = DATA["api"]["mkdir"]["url"]
        if zone:
           url = "http://%s/%s/list" % (HOST, str(zone))

        data = DATA["api"]["mkdir"]["data"]
        data["fileName"] = name
        data["parentRid"] = prid
        
        r = self.session.post(url=url, headers=self.header, data=data)
        if r.status_code == 200:
           self.data=json.loads(r.text)
        return self

    #parentRid 上传目录位置 0:根目录
    def base_upload(self, path, name, prid):
        qname = urllib.request.quote(name)

        url = DATA["api"]["upload"]["url"]
        url = "%s&parentRid=%s&qqfile=%s" %(url, prid, qname)
        data = open(os.path.join(path, name),'rb')

        header = self.header
        header["X-File-Name"] = qname
        header["Content-Type"] = "application/octet-stream"
        header["Accept"] = "*/*"

        r = self.session.post(url=url, headers=header, data=data)
        if r.status_code == 200:
            self.data=json.loads(r.text)
            print("upload success!")
        else:
            self.data=None
            print("upload failed!")
        return self

    def base_query(self, path):
        url = DATA["api"]["query"]["url"]
        data = DATA["api"]["query"]["data"]
        data["path"] = path

        r = self.session.post(url=url, headers=self.header, data=data)
        if r.status_code == 200:
           self.data=json.loads(r.text)
        return self

    def base_download(self, name, rid, _dir, _check):
        url = DATA["api"]["download"]["url"]
        url = "%s/%s" % (url, str(rid))

        print("name: %s" %name)
        print("rid: %s\n" %rid)

        path=None
        
        print("fetch %s ..." % url)

        with closing(self.session.get(url,headers=self.header,stream=True)) as response:
             if name is None:
               line=response.headers['Content-Disposition']
               matchObj = re.search( r'.*filename="(.*)"', line, re.M|re.I)
               if matchObj:
                  name=matchObj.group(1)
               else:
                  print("No match!!")
                  sys.exit(0)
             else:
                #path=name
                pass

             chunk_size = 1024  # 单次请求最大值
             content_size = int(response.headers['content-length'])
#             print((response.headers))
             data_count = 0
             path=os.path.join(_dir, name)
             print("name: %s" %name)
             print("path: %s" %path)
             print("")
             if _check is True:
                 if os.path.isfile(path):
                     print("%s exist!" %path)
                     return path
             
             with open(path, "wb") as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    data_count = data_count + len(data)
                    now_jd = (data_count / content_size) * 100
                    #print("\r%s：%d%% (%s/%s) " % (name, now_jd,
                    print("\rstatus: %3d%% (%6s /%6s) " % (now_jd,
                      self.bytes2human(data_count), 
                      self.bytes2human(content_size)), end=" ")

             print("\n\n%s" % path)
             return path

    def bytes2human(self, n):
        symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i + 1) * 10
        for s in reversed(symbols):
            if n >= prefix[s]:
               value = float(n) / prefix[s]
               return '%.1f%s' % (value,s)
        return '%sB' % n

    def format(self):
        data=self.data
        if data is not None:
           i=0
           print("details:\n")
           for ch in data["children"]:
               print("  - id: %d" % i)
               print("    name: %s" % ch["fileName"])
               print("    size: %s" % ch["size"])
               print("    time: %s" % ch["createTime"])
               print("    type: %s" % ch["itemType"])
               print("    rid: %s"  % str(ch["rid"]))
               print("")
               i+=1
           print("total: %d\n" % i)
        else:
           print("data is null!")
