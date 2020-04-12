#!/usr/bin/env python3
# -*- coding: utf-8; -*-

import os
import sys
import json
import shutil
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
               print("    type: %s" % ch["itemType"])
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

    def mkdir(self, name):
        return self.base_mkdir(name, self.parentRid)

    def base_mkdir(self, name, prid):
        url = "%s/%s/list" % (self.site, self.zone)
        data = {
               "fileName" : name,
               "rid" : "0",
               "parentRid" : prid,
               "func" : "createFolder"
            }
        r = self.session.post(url=url, headers=self.header, data=data)
        if r.status_code == 200:
           self.data=json.loads(r.text)
        return self

    def delete(self, rid):
        url = "%s/%s/list?func=deleteResource&rid=%s" % (self.site, self.zone, str(rid))
#       批量删除  http://ddl.escience.cn/king1025/list?func=deleteResources&rids%5B%5D=11271884&rids%5B%5D=11271885
        r = self.session.get(url=url, headers=self.header)
        if r.status_code == 200:
           data=json.loads(r.text)
           print(data)

    def upload(self, path, name, parentRid=None):
        prid=parentRid
        if prid is None:
           prid=self.parentRid
        print("prid: %s" % prid)
        print('file：%s' % name)
        print('path：%s' % os.path.join(path, name))
        print('upload...')
        return self.base_upload(path, name, prid)

    def base_upload(self, path, name, prid):
        qname = urllib.request.quote(name)
        #parentRid 上传目录位置 0:根目录
        url = '%s/%s/upload?func=uploadFiles&parentRid=%s&qqfile=%s' %(self.site, self.zone, prid, qname)
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
            self.data=json.loads(r.text)
            print("upload success!")
        else:
            self.data=None
            print("upload failed!")
        return self

def exec_view_command(path):
#    print("Call exec_view_command()!")
    if path is not None and os.path.isfile(path):
       comm="android view -f %s" % path
       print(comm)
       os.system(comm)
    else:
       print("%s not exist!" % path)

def exec_fusion_command(parts, path):
    if path is not None and os.path.exists(path) is False:
       comm="cat %s/* > %s" % (parts, path)
       print(comm)
       os.system(comm)
    else:
       print("%s exist! skip fusion" % path)

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
          if argc > 4:
            prid=str(sys.argv[4])
            esc.base_query(prid).format()
          else:
            esc.query().format()
       elif action == "json":
          print(json.dumps(esc.query().data["children"]))
       elif action == "query" and argc > 4:
          print(json.dumps(esc.base_query(str(sys.argv[4])).data))
       elif action == "delete" and argc > 4:
          esc.delete(str(sys.argv[4]))
       elif action == "delete_record" and argc > 4:
          rec=str(sys.argv[4])
          path=esc.download(None, rec)
          data=None
          with open(path, "r") as jf:
               data=json.loads(jf.read())
          os.remove(path)
          esc.delete(rec)
          esc.delete(data["id"])
       elif action == "mkdir" and argc > 4:
          print(json.dumps(esc.mkdir(str(sys.argv[4])).data))
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
          if path.endswith(".record"):
             data=None
             with open(path, "r") as jf:
                data=json.loads(jf.read())
             os.remove(path)
             if data is not None:
                bsdir=os.path.dirname(path)
                parts=os.path.join(bsdir, "%s_parts" % data["name"])
                shutil.rmtree(parts, ignore_errors=True)
                os.makedirs(parts)
                for r in data["record"]:
                    esc.download(r["part"], r["id"], parts)
                    print("")
                path=os.path.join(bsdir, data["name"])
                exec_fusion_command(parts, path)
                shutil.rmtree(parts, ignore_errors=True)
                print("")

          exec_view_command(path)

       elif action == "upload" and argc > 4: 
          work_dir = str(sys.argv[4])
          for ff in os.listdir(work_dir):
             pp = os.path.join(work_dir, ff)
             if os.path.isdir(pp):
                print("> upload dir: %s" % ff)
                # 11327572 part
                part="11327572"
                ch_list=esc.base_query(part).data["children"]
                prid=None
                for ch in ch_list:
                  if ff == ch["fileName"]:
                    if "Folder" == ch["itemType"]:
                        prid=ch["rid"]
                        break
                if prid is None:
                   prid=esc.base_mkdir(ff, part).data["resource"]["rid"]
                record=[]
                count=0
                for parent, _, files in os.walk(pp, followlinks=True):
                  for ch_ff in files:
                     data=esc.upload(parent,ch_ff,prid).data["resource"]
                     if data is not None:
                        item={}
                        item["id"]=str(data["rid"])
                        item["part"]=data["fileName"]
                        record.append(item)
                        count+=1
                     print('')
                data=json.dumps({"id":str(prid), "name":ff, "total":count, "record":record})
                rf="%s.record" % ff
                with open(os.path.join(pp, rf), "w") as f:
                     f.write(data)
                print("> upload record: %s" % rf)
                esc.upload(pp, rf)
             else:
                print("> upload file: %s" % ff)
                esc.upload(work_dir, ff)
             print('')
