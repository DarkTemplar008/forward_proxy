# -*- coding=UTF-8 -*-

import sys
import getopt
import subprocess

def help():
    print("tool.py --cmd=runas [<param1>...] 管理员权限启动程序")
    print("tool.py --cmd=crash <pid> 主动崩溃某进程")

def main(argv):
    try:
        opts, param = getopt.getopt(argv, "", longopts=["cmd="])
    except getopt.GetoptError:
        help()
        return

    print("cmd:", opts, "args:", param)
    if len(opts) == 0 and len(param) == 0:
        help()
        return
        
    cmd = opts[0][1]
    if cmd == "runas":
        subprocess.call([cmd+"32.exe", ] + param)
    elif cmd == "crash":
        subprocess.call(["runas32.exe", "crash32.exe "] + param)

if __name__ == "__main__":
    main(sys.argv[1:])