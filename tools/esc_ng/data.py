#!/usr/bin/env python3
# -*- coding: utf-8; -*-

import os
import sys

ESC_HOST="ddl.escience.cn"
ESC_ZONE=os.getenv("ESC_ZONE")
ESC_PRID=os.getenv("ESC_PRID")  #代表目录名: video
ESC_PARTID=os.getenv("ESC_PARTID") #代表目录名: part
ESC_LOCAL_PATH=os.getenv("ESC_LOCAL_PATH")
ESC_CONFIG=os.getenv("ESC_CONFIG")
ESC_HOME=os.getenv("ESC_HOME")

if not ESC_HOME:
  ESC_HOME=os.path.join(str(os.getenv("HOME")), ".gaction", "Gaction", "stage")

if not ESC_CONFIG:
  ESC_CONFIG=os.path.join(ESC_HOME, "esc_config.json")

if not (ESC_ZONE and ESC_PRID and ESC_PARTID and ESC_LOCAL_PATH):
   config=ESC_CONFIG
   if os.path.exists(config):
    try:
      import json
      with open(config, "r") as jf:
         data=json.loads(jf.read())
         if not ESC_ZONE and data["zone"]:
            ESC_ZONE=data["zone"]
         if not ESC_PRID and data["prid"]:
            ESC_PRID=data["prid"]
         if not ESC_PARTID and data["part_id"]:
            ESC_PARTID=data["part_id"]
         if not ESC_LOCAL_PATH and data["local_path"]:
            ESC_LOCAL_PATH=data["local_path"]
    except Exception as e:
       print("config file invalid! %s" % config)     
       print(e)
       sys.exit(1)
#   else: 
#      print("warning: %s not exist!" % config)

if not ESC_LOCAL_PATH:
   ESC_LOCAL_PATH=os.path.join(str(os.getenv("HOME")), "storage", "downloads", "gaction")

#print(ESC_ZONE)
#print(ESC_PRID)
#print(ESC_PARTID)
#print(ESC_LOCAL_PATH)

BASE_URL="http://%s/%s" % (ESC_HOST, ESC_ZONE)

DATA={
  "api" : {
      "quit_team" : {
          "url" : "http://%s/system/quitTeam?func=quitTeamValidate" % ESC_HOST,
          "url2" : "http://%s/system/quitTeam" % ESC_HOST,
          "data" : {
              "teamName" : ""
          }
      },
      "check_team" : {
          "url" : "http://%s/system/createTeam?func=validateTeamId" % ESC_HOST
       },
      "create_team" : {
           "url" : "http://%s/system/createTeam" % ESC_HOST,
           "data" : {
               "func" : "createTeam",
               "defaultMemberAuth" : "edit",
               "teamName" : "",
               "teamId" : "",
               "accessType" : "private",
               "auth" : "view",
               "teamInfo" : "docManager",
               "teamDescription" : ""
           }
      },
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
