#!/usr/bin/env python3
# -*- coding: utf-8; -*-

import os
import sys
import json
import shutil
import tempfile

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

def may_decompress_file(path):
    ch_dd=os.path.dirname(path)
    ch_ff=os.path.basename(path)
    comm, tmp, flag = None, None, None
    if ch_ff.endswith(".7z"):
       flag="7z"
       comm="7z e %s -o%s" % (path, ch_dd)
    elif ch_ff.endswith(".zip"):
       flag="zip"
       tmp = tempfile.mkdtemp()
       comm="unzip %s -d %s && mv %s/* %s" % (path, tmp, tmp, ch_dd)
    elif ch_ff.endswith(".tar"):
       flag="tar"
       comm="tar -xvf %s -C %s" % (path, ch_dd)
    elif ch_ff.endswith(".tar.gz"):
       flag="tgz"
       comm="tar -xzvf %s -C %s" % (path, ch_dd)
    elif ch_ff.endswith(".tar.bz2"):
       flag="tbz"
       comm="tar -xjvf %s -C %s" % (path, ch_dd)
    elif ch_ff.endswith(".tar.xz"):
       flag="txz"
       comm="tar -xJvf %s -C %s" % (path, ch_dd)

    if comm is not None:
    #   print(comm)
       print("> decompress(%s) file: %s" % (flag, path))
       os.system(comm)
       os.remove(path)

    if tmp is not None:
       shutil.rmtree(tmp, ignore_errors=True)

def may_download_record(esc, path):
    if path.endswith(".record"):
       data=None
       with open(path, "r") as jf:
          data=json.loads(jf.read())
       os.remove(path)
       if data is not None:
          print("")
          bsdir=os.path.dirname(path)
          parts=os.path.join(bsdir, "%s_parts" % data["name"])
          shutil.rmtree(parts, ignore_errors=True)
          os.makedirs(parts)
          total, count =int(data["total"]), 1
          for r in data["record"]:
              print("\033[1;6;32m> download part... (%d/%d)\033[m" % (total, count))
              path=esc.download(r["part"], r["id"], parts)
              print("")
              may_decompress_file(path)
              print("")
              count+=1
          path=os.path.join(bsdir, data["name"])
          exec_fusion_command(parts, path)
          shutil.rmtree(parts, ignore_errors=True)
          print("")
    return path
