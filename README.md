# LFTP(大文件传输)
使用方法如下。

首先将4个文件《server.py》,《sender.py》，《receiver.py》，《dataSolver.py》这四个文件上传到服务端某个文件夹中.
将4个文件《client.py》,《sender.py》，《receiver.py》，《dataSolver.py》放在自己的电脑的某个文件夹中。

服务端输入下述命令即可启动服务器。
> * python server.py
客户端按照老师要求，可以输入以下两条命令发送文件或接受文件。	
> * python client.py lsend ip mylargefile
> * python client.py lget ip mylargefile

ip为服务器的ip地址，我这里应为120.77.172.46，mylargefile为发送文件的路径，以下为示例。
> * python client.py lsend 120.77.172.46 1.bmp
