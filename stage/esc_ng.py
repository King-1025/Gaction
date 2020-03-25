#!/usr/bin/env python3
# -*- coding: utf-8; -*-

import os
import sys
import json
import urllib
import requests

#科研在线 http://ddl.escience.cn/king1025/list#path=%2F11015861
class Escience:
    def __init__(self, name, password,
                 zone="king1025",
                 parentRid="11015861"): #代表目录名: video
        self.name = name
        self.password = password
        self.site="http://ddl.escience.cn"
        self.session = requests.Session()
        self.isLogin = False
        self.zone = zone
        self.parentRid = parentRid  
        self.data=None
        self.header = {
                       'Host': 'ddl.escience.cn',
                       'Connection': 'keep-alive',
                       'Origin': 'http://ddl.escience.cn',
                       'X-Requested-With': 'XMLHttpRequest',
                       'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1; OPPO R7s Build/LMY47I; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 Mobile Safari/537.36',
                       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                       'Accept': 'application/json, text/javascript, */*; q=0.01',
                       'Referer': 'http://ddl.escience.cn/%s/list' % self.zone,
                       'Accept-Encoding': 'gzip, deflate',
                       'Accept-Language': 'zh-CN,zh;q=0.9',
                    }


    def auth(self):
        url = 'https://passport.escience.cn/oauth2/authorize?client_id=87142&redirect_uri=http://ddl.escience.cn/system/login/token&response_type=code&state=http://ddl.escience.cn/pan/list&theme=full'
        data = {'act': 'Validate',
                'pageinfo': 'userinfo',
                'theme': 'full',
                'userName': '%s' % self.name,
                'password': '%s' % self.password,
            }
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
        url = 'https://passport.escience.cn/oauth2/authorize'
        params = {
            "response_type": "code",
            "redirect_uri": "http%3A%2F%2Fddl.escience.cn%2Fsystem%2Flogin%2Ftoken",
            "client_id": "87142",
            "theme": "full",
            "state": "http%3A%2F%2Fddl.escience.cn%2Fpan%2Flist"
        }
        r = self.session.get(url, params=params, headers=self.header, verify=True)
        if r.status_code != 200:
            print("login_pages response nO!")
            sys.exit(1)
        else:
    #        print('login_page response oK!')
            self.auth()

    def base_query(self, path):
        url = "%s/%s/list?func=query" % (self.site, self.zone)
        data = {
               "path" : path,
               "tokenKey" : "1575527996343", # the key can be empty!
            }
        r = self.session.post(url=url, headers=self.header, data=data)
        if r.status_code == 200:
           self.data=json.loads(r.text)
        return self

    def query(self):
        return self.base_query(self.parentRid)

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
               print("    rid: %s"  % str(ch["rid"]))
               print("")
               i+=1
           print("total: %d\n" % i)
        else:
           print("data is null!")

    def download(self, name, rid, _dir="/sdcard/O_o", _check=True):
        path=None
        url = "%s/%s/downloadResource/%s" % (self.site, self.zone, str(rid))
        print("name: %s" %name)
        print("rid: %s\n" %rid)
        from contextlib import closing
        print("fetch %s ..." % url)
        with closing(self.session.get(url,headers=self.header,stream=True)) as response:
             if name is None:
               import re
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

    def rename(self):
        #http://ddl.escience.cn/king1025/list
#        post
#        fileName=test.sh&rid=11271886&parentRid=11015861&func=editFileName
        pass

    def move(self, rid):
#        http://ddl.escience.cn/king1025/fileManager
# post
# func=moveSelected&originalRids=11271886&targetRid=0
        pass

    def mkdir(self):
        pass
# http://ddl.escience.cn/king1025/list
# post
#  fileName=1&rid=0&parentRid=0&func=createFolder

    def delete(self, rid):
        url = "%s/%s/list?func=deleteResource&rid=%s" % (self.site, self.zone, str(rid))
#       批量删除  http://ddl.escience.cn/king1025/list?func=deleteResources&rids%5B%5D=11271884&rids%5B%5D=11271885
        r = self.session.get(url=url, headers=self.header)
        if r.status_code == 200:
           data=json.loads(r.text)
           print(data)

    def upload(self,path,name):
        qname = urllib.request.quote(name)
        #parentRid 上传目录位置 0:根目录
        url = '%s/%s/upload?func=uploadFiles&parentRid=%s&qqfile=%s' %(self.site, self.zone,self.parentRid,qname)
        data = open(os.path.join(path,name),'rb')
        header = {
                       'Host': 'ddl.escience.cn',
                       'Connection': 'keep-alive',
                       'Origin': 'http://ddl.escience.cn',
                       'X-Requested-With': 'XMLHttpRequest',
                       'X-File-Name': qname,
                       'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1; OPPO R7s Build/LMY47I; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 Mobile Safari/537.36',
                       'Content-Type': 'application/octet-stream',
                       'Accept': '*/*',
                       'Referer': 'http://ddl.escience.cn/%s/list' % self.zone,
                       'Accept-Encoding': 'gzip, deflate',
                       'Accept-Language': 'zh-CN,zh;q=0.9',
                       }

        r = self.session.post(url=url, headers=header, data=data)
        if r.status_code == 200:
            print("upload success!")
        else:
            print("upload failed!")
            sys.exit(1)

def exec_view_command(path):
#    print("Call exec_view_command()!")
    if path is not None and os.path.isfile(path):
       comm="android view -f %s" % path
       print(comm)
       os.system(comm)
    else:
       print("%s not exist!" % path)

if __name__ == '__main__':
    argc=len(sys.argv)
    print("argc: %s" %argc)
    if argc <= 3:
       print("it needs 3 arguments at least!")
       sys.exit(1)

    esc = Escience(str(sys.argv[1]),str(sys.argv[2]))
    esc.login()

    if esc.isLogin == True:
       action=str(sys.argv[3])
       if action == "list":
          esc.query().format()
       elif action == "json":
          print(json.dumps(esc.query().data["children"]))
       elif action == "delete" and argc > 4:
          esc.delete(str(sys.argv[4]))
       elif action == "download":
          if argc == 5:
             esc.download(None, str(sys.argv[4]), _check=False)
          elif argc >= 6:
             esc.download(str(sys.argv[5]), str(sys.argv[4]), _check=False)

       elif action == "view":
          path=None
          if argc == 5:
             path=esc.download(None, str(sys.argv[4]))
          elif argc >= 6:
             path=esc.download(str(sys.argv[5]), str(sys.argv[4]))

          print("")
          exec_view_command(path)

       elif action == "upload" and argc > 4: 
          work_dir = str(sys.argv[4])
          for parent, dirnames, filenames in os.walk(work_dir,  followlinks=True):
           for filename in filenames:
             file_path = os.path.join(parent, filename)
             print('file：%s' % filename)
             print('path：%s' % file_path)
             print('upload...')
             esc.upload(parent,filename)
             print('')
