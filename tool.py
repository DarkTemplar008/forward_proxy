# -*- coding=UTF-8 -*-

import sys
import getopt
import subprocess

ssh_server_host = "123.57.229.246"

def help():
    print("tool.py --cmd=runas [<param1>...] 管理员权限启动程序")
    print("tool.py --cmd=crash <pid> 主动崩溃某进程")
    print("tool.py --cmd=sss 阿里云服务器IP")

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
    elif cmd == "sss":
        print(ssh_server_host)

if __name__ == "__main__":
    main(sys.argv[1:])