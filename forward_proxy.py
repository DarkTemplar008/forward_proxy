# -*- coding=UTF-8 -*-

import socket
import json
import _thread
import sys
import getopt
import signal

# Ctrl+C 退出
signal.signal(signal.SIGINT, signal.SIG_DFL)

proxy_server_host = "123.57.229.246"
#proxy_server_host = socket.gethostname()
proxy_server_port = 10000
local_host = "127.0.0.1"

unique_session_id = 0
session = {}

def forward_data(from_conn, to_conn):
    print("peer:",from_conn.getsockname(),"->",from_conn.getpeername(),"|||",to_conn.getsockname(),"->",to_conn.getpeername())
    try:
        total_recv = 0
        total_stage = 1
        while True:
            data = from_conn.recv(32768)
            total_recv += len(data)
            if total_recv > 1024 * total_stage:
                print("forward: ", total_recv, "bytes")
                total_stage += 1
            to_conn.send(data)
    except:
        print("连接中断:", from_conn.getsockname(),"->",to_conn.getsockname())

    try:
        from_conn.close()
        to_conn.close()
    except:
        pass

def forward_service(from_conn, to_conn, session_id):
    forward_data(from_conn, to_conn)
    if session_id in session:
        if session[session_id]["server"] != None:
            session[session_id]["server"].close()
        if session[session_id]["client"] != None:
            session[session_id]["client"].close()
        del session[session_id]
    print("session:", session)

def send_data(sock, data):
    length = len(data)
    if length > 4096:
        raise "too big data"
    sock.send(length.to_bytes(2, "big"))
    sock.send(data)

def recv_data(sock):
    length_bytes = sock.recv(2)
    length = int.from_bytes(length_bytes, "big", signed=False)
    if length > 4096:
        raise "too big data"
    return sock.recv(length)

def proxy_server():
    server_sock = socket.socket()
    server_sock.bind((socket.gethostname(), proxy_server_port))
    server_sock.listen(5)

    while True:
        conn_sock, addr = server_sock.accept()
        try:
            print("connect from :", addr)
            req = recv_data(conn_sock).decode("utf-8")
            print("request: ", req)
            req = json.loads(req)
        except:
            print("请求不合法")
            continue

        global session
        global unique_session_id
        try :
            if req["cmd"] == "create_client":
                unique_session_id += 1
                session_id = unique_session_id
                session[session_id] = {"client":conn_sock, "server":None}
                send_data(conn_sock, json.dumps({"session_id":session_id}).encode("utf-8"))
                print("session:", session)
            elif req["cmd"] == "create_fake_host":
                session_id = int(req["session_id"])
                if session_id in session:
                    session[session_id]["server"] = conn_sock
                    print("waiting server response...")
                    server_status = recv_data(conn_sock).decode("utf-8")
                    print("server status:", server_status)
                    if server_status == "ready":
                        send_data(session[session_id]["client"], "ready".encode("utf-8"))
                        _thread.start_new_thread(forward_service, (session[session_id]["client"], session[session_id]["server"], session_id))
                        _thread.start_new_thread(forward_service, (session[session_id]["server"], session[session_id]["client"], session_id))
                    else:
                        conn_sock.close()
                        session[session_id]["server"] = None
                    print("session:", session)
                else:
                    conn_sock.close()
            else:
                conn_sock.close()
        except:
            print("网络异常,下一次请求...")
            conn_sock.close()
            pass

def client_server(port):
    proxy_sock = socket.socket()
    proxy_sock.connect((proxy_server_host, proxy_server_port))

    req = {"cmd":"create_client"}
    send_data(proxy_sock, json.dumps(req).encode("utf-8"))
    print("proxy response: ", recv_data(proxy_sock).decode("utf-8"))

    status = recv_data(proxy_sock).decode("utf-8")
    print("proxy status: ", status)
    if status != "ready":
        print("流程错误！")
        return

    # 连接本地服务，建立数据连接
    client_sock = socket.socket()
    client_sock.connect((local_host, port))
    print("本地服务连接成功")
    _thread.start_new_thread(forward_data, (client_sock, proxy_sock))
    forward_data(proxy_sock, client_sock)

def fake_host_server(session_id, port):
    proxy_sock = socket.socket()
    proxy_sock.connect((proxy_server_host, proxy_server_port))
    req = {"cmd":"create_fake_host", "session_id":session_id}
    send_data(proxy_sock, json.dumps(req).encode("utf-8"))
    server_sock = socket.socket()
    server_sock.bind((local_host, port))
    server_sock.listen(5)
    client_sock, addr = server_sock.accept()
    print("conn from: ", addr)
    send_data(proxy_sock, "ready".encode("utf-8"))
    _thread.start_new_thread(forward_data, (client_sock, proxy_sock))
    forward_data(proxy_sock, client_sock)

def help():
    print("sl_proxy.py --cmd=<cmd> --port=<port> --session_id=<session_id>")
    print("     cmd: create_client 被连接者，需要提供端口（sl_proxy.py --cmd=create_client --port=4024)")
    print("     cmd: create_fake_host 本地模拟远程被连接着，用连接者返回的session_id进行连接(sl_proxy.py --cmd=create_fake_host --session_id=1 --port=4024), port是本地监听端口")
    print("     cmd: create_server 服务程序")
    sys.exit(0)

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "", longopts=["cmd=", "port=", "session_id="])
    except getopt.GetoptError:
        help()

    if len(opts) == 0:
        help()

    cmd = None
    port = None
    session_id = None
    for opt, arg in opts:
        if opt == "--cmd":
            cmd = arg
        elif opt == "--port":
            port = int(arg)
        elif opt == "--session_id":
            session_id = arg

    if cmd == "create_server":
        proxy_server()
    elif cmd == "create_client":
        client_server(port)
    elif cmd == "create_fake_host":
        fake_host_server(session_id, port)
    else:
        help()

if __name__ == "__main__":
    main(sys.argv[1:])