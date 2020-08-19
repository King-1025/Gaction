#!/usr/bin/env python3
# -*- utf-8; -*-

import os
import sys
import json
import time
from api import ChaoXingPAN
from data import CXP_PARTID as PART_ID
from tool import may_download_record


if __name__ == "__main__":
    argc=len(sys.argv)
#   print("argc: %s" %argc)
    if argc < 2:
       print("it needs 2 arguments at least!")
       sys.exit(1)
    cxp = ChaoXingPAN().setQuite(True).login()
    if cxp.isLogin:
       action = str(sys.argv[1])
       if action == "list":
          if argc > 2:
            prid=str(sys.argv[2])
            cxp.base_query(prid).format()
          else:
            cxp.query().format()
       elif action == "empty_rec":
            print(json.dumps(cxp.empty_recycle().data))
       elif action == "delete":
          if argc > 2:
             ids = sys.argv[2:]
             print(json.dumps(cxp.delete(ids).data))
       elif action == "mkdir":
          if argc > 3:
             print(json.dumps(cxp.mkdir(str(sys.argv[2]), str(sys.argv[3])).data))
          elif argc > 2:
             print(json.dumps(cxp.mkdir(str(sys.argv[2])).data))
       elif action == "query":
          if argc > 2:
             print(json.dumps(cxp.query(str(sys.argv[2])).data))
          else:
             print(json.dumps(cxp.query().data))
       elif action == "pure_download":
          if argc == 3:
             path=cxp.download(None, str(sys.argv[2]), _check=False)
          elif argc >= 4:
             path=cxp.download(str(sys.argv[3]), str(sys.argv[2]), _check=False)
       elif action == "download":
          path = None
          if argc == 3:
             path=cxp.download(None, str(sys.argv[2]), _check=False)
          elif argc >= 4:
             path=cxp.download(str(sys.argv[3]), str(sys.argv[2]), _check=False)
          if path is not None:
             may_download_record(cxp, path)
       elif action == "upload" and argc > 2: 
          path = str(sys.argv[2])
          if os.path.exists(path) is False:
             print("%s not exists!" %path)
             sys.exit(1)
          part=PART_ID
          if os.path.isfile(path):
             print("> upload file: %s" % path)
             cxp.upload(path, parentId=part)
             print(cxp.data)
          elif os.path.isdir(path):
            work_dir = path
            print("work_dir: %s\n" % work_dir)
            for ff in os.listdir(work_dir):
              pp = os.path.join(work_dir, ff)
              if os.path.isdir(pp):
                print("> upload_dir: %s" % ff)
                #print("\033[1;6;37m> upload_dir: %s\033[m" % ff)
                ch_list = []
                if "list" in cxp.base_query(part).data:
                   ch_list=cxp.data["list"]
                prid=None
                for ch in ch_list:
                  if ff == ch["name"]:
                    if not ch["isfile"]:
                        prid=ch["id"]
                        break
                if prid is None:
                   prid = part
                   if "data" in cxp.base_mkdir(ff, part).data:
                       prid = cxp.data["data"]["id"]
                else:
                   print("skip prid: %s" % prid)
                record=[]
                count, p_c=0, 0
                total_size=0
                for parent, _, files in os.walk(pp, followlinks=True):
                  p_c+=1
                  f_l, f_c=len(files), 1
                  for ch_ff in files:
                     print("\033[1;6;32m> upload part %s... (%d/%d %d:%d)\033[m" % (ch_ff, f_l, f_c, p_c, count))
                     ch_path = os.path.join(parent, ch_ff)
                     size = os.path.getsize(ch_path)
                     print("ch_path: %s" % ch_path)
                     print("prid: %s" % prid)
                     cxp.upload(ch_path, prid)
                     #print(cxp.data)
                     #print()
                     if cxp.data is None:
                        continue
                     if "success" in cxp.data:
                        if not cxp.data["success"]:
                           continue
                     if "result" in cxp.data:
                        if not cxp.data["result"]:
                           continue
                     is_record = True
                     f_c+=1
                     if is_record:
                        item={}
                        item["size"]=str(cxp.bytes2human(size))
                        item["part"]=ch_ff
                        record.append(item)
                        count+=1
                        total_size+=size
                     print('')
                size=str(cxp.bytes2human(total_size))
                data=json.dumps({"id":str(prid), "name":ff, "size":size, "total":count, "record":record})
                rf="%s_%s.record" % (ff, size)
                rf_path = os.path.join(pp, rf)
                with open(rf_path, "w") as f:
                     f.write(data)
                print("\033[1;6;32m> upload record: %s\033[m" % rf)
                cxp.upload(rf_path, part)
              else:
                print("\033[1;6;33m> upload file: %s\033[m" % ff)
                cxp.upload(pp, part)
              print('')
