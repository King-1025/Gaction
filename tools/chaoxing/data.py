#!/usr/bin/env python3
# -*- utf-8; -*-



CXP_HOST="test"
CXP_USER="user"
CXP_PSWD="password"

#CXP_PARENTID="481515948815077376"
#CXP_ENC="a9183addea85e0ab95950a355cdf11d9"
#CXP_PUID="143282464"

#CXP_PARENTID="479730447334428672"
CXP_PARENTID="512044885101957120"
CXP_ENC="3c15cae99038654d85ca48de12b70d3b"
CXP_PUID="142823964"

CXP_PARTID=CXP_PARENTID
CXP_PUID_ROOT="0"
CXP_LPATH="/sdcard/Download/gaction"


CHXPAN_HOST_MAIN="pan-yz.chaoxing.com"
CHXPAN_HOST_TEST="test.pan.chaoxing.com"

CHXPAN_HOST = CHXPAN_HOST_MAIN

if CXP_HOST == "test":
   CHXPAN_HOST = CHXPAN_HOST_TEST

BASE_URL="http://%s" % CHXPAN_HOST
OPT_URL="%s/opt" % BASE_URL
REC_URL="%s/recycle" % BASE_URL
DA_URL="http://d0.ananas.chaoxing.com"

USER_AGENT='Mozilla/5.0 (Linux; Android 5.1; OPPO R7s Build/LMY47I; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 Mobile Safari/537.36'

AUTH_HOST="passport2.chaoxing.com"
AUTH_URL="http://%s" % AUTH_HOST

DEFAULT_COOKIE_PATH="stage/cookie.json"

DATA={
        "cookie" : DEFAULT_COOKIE_PATH,
        "api":{
            "recycle": {
                 "empty":{
                    "url":"%s/empty" % REC_URL
                }
            },
            "download":{
                "url":"%s/download" % DA_URL
            },
            "delete":{
                "url":"%s/delres" % OPT_URL
            },
            "mkdir":{
                "url":"%s/newfolder" % OPT_URL
            },
            "query":{
                "url":"%s/listres" % OPT_URL
            },
            "upload":{
                "url":"%s/upload" % OPT_URL
            },
            "createfile":{
                "url":"%s/createfilenew" % OPT_URL
            },
            "numCode":{
                "url":"%s/num/code" % AUTH_URL
            },
            "auth":{
                "url":"%s/login?refer=%s" % (AUTH_URL, BASE_URL),
                "data":{
                  "refer_0x001": BASE_URL,
                  "pid":"-1",
                  "pidName":"",
                  "fid":"-1",
                  "fidName":"",
                  "allowJoin":"0",
                  "isCheckNumCode":"1",
                  "f":"0",
                  "productid":"",
                  "t":"true",
                  "verCode":""
                 }
             }
        },
        "header" : {
		'User-Agent' : USER_AGENT
        },
        "pan_header":{
                'Host' : CHXPAN_HOST,
                'Connection' : 'keep-alive',
                'Accept' : 'application/json, text/javascript, */*; q=0.01',
                'Origin' : BASE_URL,
                'X-Requested-With' : 'XMLHttpRequest',
                'User-Agent' : USER_AGENT,
                'Referer' : BASE_URL,
                'Accept-Encoding' : 'gzip, deflate',
                'Accept-Language' : 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        },
        "auth_header":{
		'Host' : AUTH_HOST,
		'Connection' : 'keep-alive',
		'Cache-Control' : 'max-age=0',
		'Upgrade-Insecure-Requests' : '1',
		'Origin' : AUTH_URL,
		'Content-Type' : 'application/x-www-form-urlencoded',
		'User-Agent' : USER_AGENT,
		'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'X-Requested-With' : 'mark.via',
		'Referer' : "%s/login?refer=%s" % (AUTH_URL, BASE_URL),
		'Accept-Encoding' : 'gzip, deflate',
		'Accept-Language' : 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            },
        "res":{
                "page":1,
                "size":50,
                "end":"false",
                "action":"normal",
                "current":[],
                "parentId":CXP_PARENTID,
                "choosed":{},
                "choosedlen":0,
                "foldercounter":0,
                "speedclasscon":0,
                "foldernewcounter":0,
                "puid":CXP_PUID_ROOT,
                "isshare":"false",
                "istome":"false",
                "foldertomecounter":0,
                "shareid":0
        },
        "enc" : CXP_ENC
}
