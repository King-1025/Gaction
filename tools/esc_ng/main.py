#!/usr/bin/env python3
# -*- coding: utf-8; -*-

import os
import sys
import json

from api import Escience

from tool import exec_view_command
from tool import may_download_record
from tool import exec_install_command

from data import ESC_PARTID as PART_ID


if __name__ == '__main__':
    argc=len(sys.argv)
#   print("argc: %s" %argc)
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
             path=esc.download(None, str(sys.argv[4]), _check=False)
          elif argc >= 6:
             path=esc.download(str(sys.argv[5]), str(sys.argv[4]), _check=False)
          may_download_record(esc, path)

       elif action == "ipk":
          path=None
          if argc == 5:
             path=esc.download(None, str(sys.argv[4]))
          elif argc >= 6:
             path=esc.download(str(sys.argv[5]), str(sys.argv[4]))

          exec_install_command(may_download_record(esc, path))

       elif action == "view":
          path=None
          if argc == 5:
             path=esc.download(None, str(sys.argv[4]))
          elif argc >= 6:
             path=esc.download(str(sys.argv[5]), str(sys.argv[4]))

          exec_view_command(may_download_record(esc, path))

       elif action == "upload" and argc > 4: 
          path = str(sys.argv[4])
          if os.path.exists(path) is False:
             print("%s not exists!" %path)
             sys.exit(1)
          if os.path.isfile(path):
             print("> upload file: %s" % path)
             work_dir = os.path.dirname(path)
             ff = os.path.basename(path)
             esc.upload(work_dir, ff)
          elif os.path.isdir(path):
            work_dir = path
            print("work_dir: %s" % work_dir)
            for ff in os.listdir(work_dir):
              pp = os.path.join(work_dir, ff)
              if os.path.isdir(pp):
                print("> upload dir: %s" % ff)
                part=PART_ID
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
