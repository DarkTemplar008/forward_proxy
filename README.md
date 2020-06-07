# forward_proxy
通过中间服务器进行转接tcp服务


# 目的
在aliyun上部署一个转发服务，可以让未知IP的服务可以像访问本地服务一样

比如：
在某内网主机提供了一个ssh服务，在这个主机上启动forward_proxy(python forward_proxy.py --cmd=create_client --port=22)。
然后在本地启动另外一个forward_proxy伪主机(python forward_proxy.py --cmd=create_fake_host --session_id=1 --port=22)。
此时就可以在本地试用ssh 127.0.0.1访问上面内网主机了