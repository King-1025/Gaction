#!/usr/bin/env python3

from lanzou.cmder.cmder import Commander
from lanzou.cmder.utils import *

import sys

if __name__ == '__main__':
    argv = sys.argv
    argc = len(argv)
    if argc >= 4 and argv[1] == "once":
       #print(argv[4:])
       Commander().login(argv[2], argv[3]).run(argv[4:])
    else:
       set_console_style()
#       check_update()
#       print_logo()
       commander = Commander()
       commander.login()
    
       while True:
         try:
            commander.run()
         except KeyboardInterrupt:
            pass
         except Exception as e:
            error(e)
