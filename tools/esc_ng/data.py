#!/usr/bin/env python3
# -*- coding: utf-8; -*-

ESC_HOST="ddl.escience.cn"
ESC_ZONE="king1025"
ESC_PRID="11015861" #代表目录名: video
ESC_PARTID="11327572" #代表目录名: part

BASE_URL="http://%s/%s" % (ESC_HOST, ESC_ZONE)

DATA={
  "api" : {
      "upload" : {
           "url" : "%s/upload?func=uploadFiles" % BASE_URL
      },
      "mkdir" : { 
           "url" : "%s/list" % BASE_URL,
           "data" : {
                  "rid" : "0",
                  "func" : "createFolder"
            }
      },
      "delete" : {
          "url" : "%s/list?func=deleteResource" % BASE_URL
      },
      "download" : {
          "url" : "%s/downloadResource" % BASE_URL
      },
      "query" : {
          "url" : "%s/list?func=query" % BASE_URL,
          "data" : {
                 "tokenKey" : "1575527996343", # the key can be empty!
           }
      },
      "login" : {
          "url" : "https://passport.escience.cn/oauth2/authorize",
          "data" : {
                 "response_type": "code",
                 "redirect_uri": "http%3A%2F%2Fddl.escience.cn%2Fsystem%2Flogin%2Ftoken",
                 "client_id": "87142",
                 "theme": "full",
                 "state": "http%3A%2F%2Fddl.escience.cn%2Fpan%2Flist"
          }
      },
      "auth" : {
          "url" : "https://passport.escience.cn/oauth2/authorize?client_id=87142&redirect_uri=http://ddl.escience.cn/system/login/token&response_type=code&state=http://ddl.escience.cn/pan/list&theme=full",
          "data" : {
                 'act': 'Validate',
                 'pageinfo': 'userinfo',
                 'theme': 'full'
          }
      }
  },
  "header" : {
             'Connection': 'keep-alive',
             'X-Requested-With': 'XMLHttpRequest',
             'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1; OPPO R7s Build/LMY47I; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 Mobile Safari/537.36',
             'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
             'Accept': 'application/json, text/javascript, */*; q=0.01',
             'Accept-Encoding': 'gzip, deflate',
             'Accept-Language': 'zh-CN,zh;q=0.9',
             'Host': "%s" % ESC_HOST,
             'Origin' : "%s" % BASE_URL,
             'Referer' : "%s/list" % BASE_URL
  }
}
