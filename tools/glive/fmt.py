#!/usr/bin/env python3
# -*- utf-8; -*-

import yaml
import sys
import os

if __name__ == "__main__":

  if len(sys.argv) <= 2:
      print("%s <in-file> <out-file>" % str(sys.argv[0]))
      sys.exit(0)
  inf = str(sys.argv[1])
  ouf = str(sys.argv[2])
  if not os.path.isfile(inf):
     print("in-file not exist! "+inf)
     sys.exit(0)

  with open(inf, "r") as f:
     data = yaml.load(f,  Loader=yaml.FullLoader)
     with open(ouf, "a+") as o:
       for video in data["details"]:

           name="glive_%s-%d" % (video["publish"], video["video"])
           for src in video["qualities"]:
               print("name: %s\nurl: %s\n" % (name, src["url"]))
               o.write("%s*%s\n" % (src["url"], name))
               break
