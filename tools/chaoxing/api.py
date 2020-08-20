#!/usr/bin/env python3
# -*- utf-8; -*-


import os
import re
import sys
import json
import time
import base64
import requests
from requests_toolbelt.multipart import encoder
from contextlib import closing

from data import DATA, CXP_USER, CXP_PSWD, CXP_PUID_ROOT, CXP_PUID, CXP_LPATH
from tool import progress, bytes2human, formatSimpleTime, getFileLastGMTime 


class ChaoXingPAN:
    def __init__(self, name=None, password=None, cookie=None):
        self.setName(name)
        self.setPassword(password)

        self.isLogin = False
        self.data = None
        self.disable_progress = False
        self.use_cookie = False
        self.auto_save_cookie = True
        self.quite = False

        self.enc = DATA["enc"]
        self.res = DATA["res"]
        self.header = DATA["header"]

        self.session = requests.Session()

        self.cookie_path = cookie
        if self.cookie_path is None:
           self.cookie_path=DATA["cookie"]
        self.setCookie(self.cookie_path)

    def setQuite(self, v):
        self.quite = v
        return self

    def setName(self, name):
        if name is not None:
           self.name = name
        else:
           self.name = CXP_USER
        return self

    def setPassword(self, password):
        if password is not None:
           self.password = password
        else:
           self.password = CXP_PSWD
        if self.password is not None:
          pswd_bytes = bytes(self.password, encoding='utf-8')
          self.password = str(base64.b64encode(pswd_bytes), encoding='utf-8')
        return self

    def setCookie(self, cookie_path):
        if cookie_path and os.path.exists(cookie_path):
           with open(cookie_path, "r") as f:
               cookie = json.load(f)
               cookie = requests.utils.cookiejar_from_dict(cookie, cookiejar=None, overwrite=True)
               if self.session is not None:
                  self.session.cookies = cookie
                  self.use_cookie = True
               else:
                   print("no session! cann't set cookies.")
        return self

    def login(self):
        if self.use_cookie:
           self.isLogin = True
           if not self.quite:
              print("login use cookie.")           
           return self

        if self.name == "" or self.name is None :
           print("login name is null!")
           sys.exit(1)
        if self.password == "" or self.password is None:
           print("login password is null!")
           sys.exit(1)

        self.header = DATA["auth_header"]
        self.getNumCode()
        code=input("input number code: ")
        if not self.quite:
           print("code: %s" %code)
        self.auth(code)
        return self

    def getNumCode(self, path="/sdcard/Download/numcode.jpg"):
        url = DATA["api"]["numCode"]["url"]
        url="%s?%d" %(url, int(time.time_ns() / (10 ** 6)))
        print("fetch %s..." % url)
        try:
            r=self.session.get(url, headers=self.header)
            with open(path, 'wb') as fp:
               fp.write(r.content)
            print("save numcode: %s" %path)
        except:
            print("getNumCode failed!\n")
            sys.exit(1)

    def auth(self, numcode):
        url = DATA["api"]["auth"]["url"]
        data = DATA["api"]["auth"]["data"]
        data["uname"] = self.name
        data["password"] = self.password
        data["numcode"] = str(numcode)
        try:
            self.session.post(url, headers=self.header, data=data, verify=False, allow_redirects=False)
            cookies=self.getCookies()
            if cookies["xxtenc"] != "":
               self.isLogin = True
               if self.auto_save_cookie:
                  self.saveCookie(self.cookie_path)
               print("auth success!\n")
        except:
            print("auth failed!\n")
            sys.exit(1)

    def getCookies(self):
        return self.session.cookies.get_dict()

    def saveCookie(self, path):
        if path != "" and path is not None:
           with open(path, "w") as f:
                f.write(json.dumps(self.getCookies()))
                if not self.quite:
                   print("save cookie oK! %s" %path)
        else:
           print("cookie save path is null!")
            
    def create_callback(self, progress_label=""):
        def callback(monitor):
            progress(monitor.bytes_read, monitor.len, label = progress_label)
        return callback

    def make_data(self, e, call_back, label, progress=True):
        data = None
        if self.disable_progress or not progress:
           return encoder.MultipartEncoderMonitor(e, None)
        else:
           if call_back is not None:
              data = encoder.MultipartEncoderMonitor(e, call_back)
           else:
              data = encoder.MultipartEncoderMonitor(e, self.create_callback(label))
        return data

    def post(self, url):
        header = DATA["pan_header"]
        data = {}
        return self.base_post(url, header, data)

    def base_post(self, url, header, data=None):
        r = self.session.post(url=url, headers=header, data=data)
        if r.status_code == 200:
           self.data=json.loads(r.text)
        else:
           self.data=None
        return self

    def mkdir(self, name, parentId=None, puid=None):
        if parentId is None:
            return self.base_mkdir(name, self.res["parentId"], puid)
        else:
            return self.base_mkdir(name, parentId, puid)

    def base_mkdir(self, name, parentId, puid=None):
        url = DATA["api"]["mkdir"]["url"]
        header = DATA["pan_header"]
        data = {
                "name" : name,
                "parentId" : parentId,
                "puid" : self.check_puid(parentId, puid)
        }
        return self.base_post(url, header, data)

    def empty_recycle(self):
        url = DATA["api"]["recycle"]["empty"]["url"]
        header = DATA["pan_header"]
        return self.base_post(url, header)

    def delete(self, ids):
        size = len(ids)
        if size <= 0:
           return self
        url = DATA["api"]["delete"]["url"]
        header = DATA["pan_header"]
        resids=""
        resourcetype=""
        puids=""
        for i in ids:
            resids="%s,%s" % (str(i), resids)
            resourcetype="0,%s" % resourcetype
            puids="%s,%s" %(str(CXP_PUID), puids)
        data = {
                "resids" : resids,
                "resourcetype" : resourcetype,
                "puids" : puids
        }
        #print(data)
        return self.base_post(url, header, data)

    def check_puid(self, parentId, puid):
        _puid = puid
        if _puid is None:
           if parentId == self.res["parentId"]:
              _puid = CXP_PUID_ROOT
           else:
              _puid = CXP_PUID
        return _puid

    def query(self, parentId=None, puid=None):
        if parentId is None:
            return self.base_query(self.res["parentId"], puid)
        else:
            return self.base_query(parentId, puid)

    def base_query(self, parentId, puid=None):
        url = DATA["api"]["query"]["url"]
        header = DATA["pan_header"]
        data = {
                "puid" : self.check_puid(parentId, puid),
                "shareid" : self.res["shareid"],
                "parentId" : parentId,
                "page" : self.res["page"],
                "size" : self.res["size"],
                "enc" : self.enc
        }
        return self.base_post(url, header, data)

    def upload(self, path, parentId=None, puid=None, _call_back=None):
        if parentId is None:
           return self.base_upload(path, self.res["parentId"], puid,_call_back)
        else:
           return self.base_upload(path, parentId, puid, _call_back)

    def base_upload(self, path, parentId, puid, _call_back=None):
        crc, ts = None, None
        data = self.createfile(path, parentId, puid).data
        if data is not None:
           if not self.quite:
              print(data)
           result = data["result"]
           if result:
              print("upload success!")
              return self
           else:
              crc = data["crc"]
              ts = data["timemil"]
        else:
           print("file size < 2M")
        filename = os.path.basename(path)
        size = os.path.getsize(path)
        date = getFileLastGMTime(path)
        url = DATA["api"]["upload"]["url"]
        header = DATA["pan_header"]
        header["Accept"] = "*/*"
        header["X-Requested-With"] = "mark.via"
        fields = {
                  "folderId" : parentId,
                  "puid" : self.check_puid(parentId, puid),
                  "id" : "WU_FILE_0",
                  "name" : filename,
                  "type" : "application/octet-stream",
                  "lastModifiedDate" : date,
                  "size": str(size),
                  "file" : (filename, open(path, "rb"), "application/octet-stream")
        }
        if crc is not None:
           fields["crc"] = crc 
        if ts is not None:
           fields["ts"] = ts
        e = encoder.MultipartEncoder(
              fields = fields,
              boundary = "------WebKitFormBoundary" + "kYAh6TNBAQmVa4BH"
        )     
        if not self.quite:
           print(fields)
           print()
        data = self.make_data(e, _call_back, "uploading: ")
        header["Content-Type"] = data.content_type
        r = self.session.post(url=url, headers=header, data=data)
        self.data=json.loads(r.text)
        print()
        if r.status_code == 200 and self.data["success"]:
           print("upload success!")
        else:
           print("upload failed!")
        return self

    def createfile(self, path, parentId, puid, _call_back=None):
        self.data = None
        size = os.path.getsize(path)
        limit = 1024 * 1024
        bytes_per_chunk = 512 * 1024
        if size >= limit + bytes_per_chunk * 2 :
           filename = os.path.basename(path)
           buf0, buf1=None, None
           with open(path, 'rb') as f:
                buf0 = f.read(bytes_per_chunk)
                f.seek(-bytes_per_chunk, 2)
                buf1 = f.read(bytes_per_chunk)
           e = encoder.MultipartEncoder(
               fields = {
                  "size": str(size),
                  "fn" : filename,
                  "file0" : ("blob", buf0, "application/octet-stream"),
                  "file1" : ("blob", buf1, "application/octet-stream"),
                  "fldid" : parentId,
                  "puid" : self.check_puid(parentId, puid),
              },
              boundary = "------WebKitFormBoundary" + "kYAh6TNBAQmVa4BH"
           )
           data = self.make_data(e, _call_back, "create file: ", False)
           url = DATA["api"]["createfile"]["url"]
           header = DATA["pan_header"]
           header["Content-Type"] = data.content_type
           r = self.session.post(url=url, headers=header, data=data)
           if r.status_code == 200:
              self.data=json.loads(r.text)
              #print("createfile success!")
           else:
              print("createfile failed!")
              sys.exit(1)
        return self

    def bytes2human(self, n):
        return bytes2human(n)

    def format(self):
        data=self.data
        if data is not None and "list" in data:
           i=0
           print("details:\n")
           for ch in data["list"]:
               print("  - id: %d" % i)
               print("    name: %s" % ch["name"])
               print("    size: %s" % bytes2human(ch["filesize"]))
               print("    time: %s" % formatSimpleTime(ch["uploadDate"]/1000))
               suffix = ch["suffix"]
               isfile = ch["isfile"]
               if suffix == "" and not isfile:
                  print("    type: dir")
               else:
                  print("    type: file")
                  print("    suffix: %s" % suffix)
               print("    rid: %s"  % str(ch["id"]))
               if "objectId" in ch:
                  print("    objectId: %s"  % str(ch["objectId"]))
               print("")
               i+=1
           print("total: %d\n" % i)
        else:
           print("data is null!")

    def download(self, name, rid, path=None, _check=True):
        if path is None:
           return self.base_download(name, rid, CXP_LPATH, _check)
        else:
           return self.base_download(name, rid, path, _check)

    def base_download(self, name, rid, _dir, _check):
        url = DATA["api"]["download"]["url"]
        url = "%s/%s" % (url, str(rid))

        print("name: %s" %name)
        print("oid: %s\n" %rid)

        path=None
        
        print("fetch %s ..." % url)

        with closing(self.session.get(url,headers=self.header,stream=True)) as response:
             if name is None:
               line=response.headers['Content-Disposition']
               matchObj = re.search( r'.*filename=(.*);.*', line, re.M|re.I)
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
