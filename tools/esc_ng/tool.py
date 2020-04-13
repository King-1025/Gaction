#!/usr/bin/env python3
# -*- coding: utf-8; -*-

import os
import sys
import json
import shutil

def exec_command(path, comm):
    if path is not None and os.path.exists(path):
       print(comm)
       os.system(comm)
    else:
       print("%s not exist!" % path)

def exec_install_command(path):
    comm="android install %s" % path
    exec_command(path, comm)

def exec_view_command(path):
    comm="android view -f %s" % path
    exec_command(path, comm)

def exec_fusion_command(parts, path):
    comm="cat %s/* > %s" % (parts, path)
    exec_command(parts, comm)

def may_download_record(esc, path):
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
    return path
