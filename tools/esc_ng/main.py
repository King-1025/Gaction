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
from data import ESC_CONFIG as CONFIG
from data import ESC_LOCAL_PATH as LPATH


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

       if action == "setup":
          print("* create team...")
          zone=esc.create_team("gaction")
          if zone:
             print("* mkdir video...")
             prid=esc.base_mkdir("video", "0", zone).data["resource"]["rid"]
             if not prid:
                prid="0"
             print("success! prid: %s\n" % prid)
             print("* mkdir video/part...")
             part_id=esc.base_mkdir("part", prid, zone).data["resource"]["rid"]
             if not part_id:
                part_id="0"
             print("success! part_id: %s\n" % part_id)
             print("* check local path: %s..." % LPATH)
             if not os.path.exists(LPATH):
                print("* mkdir local path...")
                os.makedirs(LPATH)
                print("success!\n")
             else:
                print("skip!\n")
             print("* gen config %s..." % CONFIG)
             data=json.dumps({"zone":str(zone), "prid":str(prid), "part_id":str(part_id), "local_path":str(LPATH)})
             with open(CONFIG, "w") as f:
                  f.write(data)
             print("success!")

       elif action == "list":
          if argc > 4:
            prid=str(sys.argv[4])
            esc.base_query(prid).format()
          else:
            esc.query().format()

       elif action == "json":
          print(json.dumps(esc.query().data["children"]))

       elif action == "query" and argc > 4:
          print(json.dumps(esc.base_query(str(sys.argv[4])).data))

       elif action == "quit_team":
          if argc > 4:
             print(json.dumps(esc.quit_team(str(sys.argv[4])).data))
          else:
             print(json.dumps(esc.quit_team().data))

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

       elif action == "mkdir":
          if argc == 5:
             print(json.dumps(esc.mkdir(str(sys.argv[4])).data))
          elif argc == 6:
             print(json.dumps(esc.mkdir(str(sys.argv[4]), str(sys.argv[5])).data))
          elif argc >= 7:
             print(json.dumps(esc.base_mkdir(str(sys.argv[4]), str(sys.argv[5]), str(sys.argv[6])).data))

       elif action == "create_team":
          zone = None
          if argc == 5:
             zone=esc.create_team(str(sys.argv[4]))
          elif argc >= 6:
             zone=esc.create_team(str(sys.argv[4]), str(sys.argv[5]), force=True)
          if zone is not None:
             print(zone)

       elif action == "pure_download":
          if argc == 5:
             path=esc.download(None, str(sys.argv[4]), _check=False)
          elif argc >= 6:
             path=esc.download(str(sys.argv[5]), str(sys.argv[4]), _check=False)

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
            print("work_dir: %s\n" % work_dir)
            for ff in os.listdir(work_dir):
              pp = os.path.join(work_dir, ff)
              if os.path.isdir(pp):
                print("> upload_dir: %s" % ff)
                #print("\033[1;6;37m> upload_dir: %s\033[m" % ff)
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
                else:
                   print("skip prid: %s" % prid)
                record=[]
                count, p_c=0, 0
                total_size=0
                for parent, _, files in os.walk(pp, followlinks=True):
                  p_c+=1
                  f_l, f_c=len(files), 1
                  for ch_ff in files:
                     print("\033[1;6;32m> upload part... (%d/%d %d:%d)\033[m" % (f_l, f_c, p_c, count))
                     size=os.path.getsize(os.path.join(parent, ch_ff))
                     data=esc.upload(parent,ch_ff,prid).data["resource"]
                     f_c+=1
                     if data is not None:
                        item={}
                        item["id"]=str(data["rid"])
                        item["size"]=str(esc.bytes2human(size))
                        item["part"]=data["fileName"]
                        record.append(item)
                        count+=1
                        total_size+=size
                     print('')
                size=str(esc.bytes2human(total_size))
                data=json.dumps({"id":str(prid), "name":ff, "size":size, "total":count, "record":record})
                rf="%s_%s.record" % (ff, size)
                with open(os.path.join(pp, rf), "w") as f:
                     f.write(data)
                print("\033[1;6;32m> upload record: %s\033[m" % rf)
                esc.upload(pp, rf)
              else:
                print("\033[1;6;33m> upload file: %s\033[m" % ff)
                esc.upload(work_dir, ff)
              print('')
