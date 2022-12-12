# coding=utf-8
from socket import *
import re
import multiprocessing
from datetime import datetime
import framework
import sys
import PySimpleGUI
import os
from loguru import logger
Userdirectory = "./"
FileNotFoundIndicator = False
NoRights = False
GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT+0800 (CST)'
GMT_FORMAT1 = '%d%b%Y'
logger.add(sink='log/'+str(datetime.utcnow().strftime(GMT_FORMAT1)), encoding='utf-8')

class WebServer:

    def __init__(self, server_port):

        # create socket
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        # 设置当服务器先close 即服务器端4次挥手之后资源能够立即释放，这样就保证了，下次运行程序时 可以立即绑定7788端口
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # 设置服务端提供服务的端口号
        self.server_socket.bind(('', server_port))
        # 使用socket创建的套接字默认的属性是主动的，使用listen将其改为被动，用来监听连接
        self.server_socket.listen(128)  # 最多可以监听128个连接

    def start_http_service(self, server_port):
        # 开启while循环处理访问过来的请求
        if(re.search('john',Userdirectory) != None):
            print("The Server is already start!")
            print("The port for this server is:" + str(server_port))
            print("You can just type the localhost:" + str(server_port) + "/john/XXX in the web browser")
        else:
            print("The Server is already start!")
            print("The port for this server is:" + str(server_port))
            print("You can just type the localhost:" + str(server_port) + "/richard/XXX in the web browser")
        while True:
            # 如果有新的客户端来链接服务端，那么就产生一个新的套接字专门为这个客户端服务
            # client_socket用来为这个客户端服务
            # self.server_socket就可以省下来专门等待其他新的客户端连接while True:
            client_socket, clientAddr = self.server_socket.accept()
            # handle_client(client_socket)
            # 设置子进程
            new_process = multiprocessing.Process(target=self.handle_client, args=(client_socket, Userdirectory))
            new_process.start()  # 开启子进程
            # 因为子进程已经复制了父进程的套接字等资源，所以父进程调用close不会将他们对应的这个链接关闭的
            client_socket.close()

    def handle_client(self, client_socket, Userdirectory):
        # initiate the global variable
        global FileNotFoundIndicator
        global NoRights
        # 接收对方发送的数据
        recv_data = client_socket.recv(1024).decode("utf-8")  # 1024表示本次接收的最大字节数
        # 打印从客户端发送过来的数据内容
        # print("client_recv:",recv_data)
        # print("client_recv_over!")
        request_header_lines = recv_data.splitlines()
        for line in request_header_lines:
            print(line)

        # 返回浏览器数据
        # 设置内容body
        # 使用正则匹配出文件路径
        # print("------>", request_header_lines[0])
        print("file_path---->", "./html/" + re.match(r"[^/]+/([^\s]*)", request_header_lines[0]).group(1))
        logger.info(request_header_lines[0])
        ret = re.match(r"[^/]+/([^\s]*)", request_header_lines[0])
        if ret:
            file_path = "./" + ret.group(1)
            if(re.search(Userdirectory,file_path) == None):
                NoRights = True
            print("file_path *******", file_path)
            temp_file_path = file_path
            new_name = ""
            try:
                if temp_file_path.endswith("py"):
                    filename = os.path.splitext(temp_file_path)
                    if filename[1] == ".py":
                        new_name = filename[0] + ".html"
                else:
                    new_name = file_path
                print("***" + str(new_name))
                f = open(new_name)
                f.close()
            except FileNotFoundError:
                print("File is not found.")
                FileNotFoundIndicator = True

        # 判断file_path是否py文件后缀，如果是则请求动态资源，否则请求静态资源
        if file_path.endswith(".py"):
            print("FileNotFoundIndicator =" + str(FileNotFoundIndicator))
            # framework.application(client_socket)
            # 支撑WGSI协议的调用方式
            environ = {'REQUEST_URI': file_path}
            response_body, FileNotFoundIndicator, NoRights = framework.application(environ, self.start_response,
                                                                         FileNotFoundIndicator, Userdirectory, NoRights)
            # 设置返回的头信息header
            # 1.拼接第一行HTTP/1.1 200 OK + 换行符内容
            response_headers = "HTTP/1.1 " + self.application_header[0] + "\r\n"
            logger.info('response_headers:HTTP/1.1 ' + self.application_header[0] + " ")
            # 2.循环拼接第二行或者多行元组内容：Content-Type:text/html

            for var in self.application_header[1]:
                response_headers += var[0] + ":" + var[1] + "\r\n"
                logger.info(var[0] + ":" + var[1] + " ")
            # 3.空一行与body隔开
            response_headers += "\r\n"
            # 4.打印看看header的内容信息
            print("response_header:")
            print(response_headers)

            # 设置返回的浏览器的内容
            client_socket.send(response_headers.encode("utf-8"))
            client_socket.send(response_body.encode("utf-8"))
        else:
            # 请求静态资源
            # try:
            # 设置返回的头信息 header
            # response_headers = "HTTP/1.1 200 OK\r\n"  # 200 表示找到这个资源
            # response_headers += "\r\n"  # 空一行与body隔开
            # 读取html文件内容
            file_name = file_path  # 设置读取的文件路径
            if NoRights: #when the user want to acess others file the system will automatically redirect to 404 page and help user to go back
                response_headers = "HTTP/1.1 404 not found\r\n"  # 200 表示找到这个资源
                response_headers += "\r\n"  # 空一行与body隔开
                logger.info("HTTP/1.1 404 not found " )
                print("WARNING MESSAGE: You can not access other users file so the server reply 404.html as a feedback!")
                print("FileNotFoundIndicator =" + str(FileNotFoundIndicator))
                f = open(Userdirectory + "404.html", "rb")  # 以二进制读取文件内容
                response_body = f.read()
                f.close()
                # print("NoRights =" + str(NoRights))
            elif FileNotFoundIndicator: #when the user want to acess a file whcih is not exist then the system will redirect to index.html
                response_headers = "HTTP/1.1 404 not found\r\n"  # 200 表示找到这个资源
                response_headers += "\r\n"  # 空一行与body隔开
                logger.info("HTTP/1.1 404 not found " )
                print("WARNING MESSAGE: There is no such file so the server directly reply index.html as a feedback!")
                f = open(Userdirectory + "index.html", "rb")  # 以二进制读取文件内容
                response_body = f.read()
                f.close()
                # print("FileNotFoundIndicator =" + str(FileNotFoundIndicator))
            elif(NoRights == False and FileNotFoundIndicator == False):
                print("FileNotFoundIndicator =" + str(FileNotFoundIndicator))
                f = open(file_name, "rb")  # 以二进制读取文件内容
                response_body = f.read()
                f.close()
                data_length = len(response_body)
                response_headers = "HTTP/1.1 200 OK\r\n"  # 200 表示找到这个资源
                logger.info("HTTP/1.1 200 OK ")
                if (file_path.endswith(".html")):
                    response_headers += "Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + "\r\n"
                    logger.info("Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + " ")
                    response_headers += "Content-Type: TEXT/HTML\r\n"
                    logger.info("Content-Type: TEXT/HTML ")
                    response_headers += "Content-Length:" + str(data_length) + "\r\n"
                    logger.info("Content-Length:" + str(data_length) + " ")
                    response_headers += "\r\n"  # 空一行与body隔开
                elif (file_path.endswith(".jpg")):
                    response_headers += "Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + "\r\n"
                    logger.info("Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + " ")
                    response_headers += "Content-Type: image/jpg\r\n"
                    logger.info("Content-Type: image/jpg ")
                    response_headers += "Content-Length:" + str(data_length) + "\r\n"
                    logger.info("Content-Length:" + str(data_length) + " ")
                    response_headers += "\r\n"  # 空一行与body隔开
                elif (file_path.endswith(".png")):
                    response_headers += "Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + "\r\n"
                    logger.info("Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + " ")
                    response_headers += "Content-Type: application/x-png\r\n"
                    logger.info("Content-Type: PNG")
                    response_headers += "Content-Length:" + str(data_length) + "\r\n"
                    logger.info("Content-Length:" + str(data_length) + " ")
                    response_headers += "\r\n"  # 空一行与body隔开
                elif (file_path.endswith(".gif")):
                    response_headers += "Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + "\r\n"
                    logger.info("Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + " ")
                    response_headers += "Content-Type: image/gif\r\n"
                    logger.info("Content-Type: PNG")
                    response_headers += "Content-Length:" + str(data_length) + "\r\n"
                    logger.info("Content-Length:" + str(data_length) + " ")
                    response_headers += "\r\n"  # 空一行与body隔开
                elif (file_path.endswith(".mp3")):
                    response_headers += "Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + "\r\n"
                    logger.info("Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + " ")
                    response_headers += "Content-Type: MP3\r\n"
                    logger.info("Content-Type: MP3 ")
                    response_headers += "Content-Length:" + str(data_length) + "\r\n"
                    logger.info("Content-Length:" + str(data_length) + " ")
                    response_headers += "\r\n"  # 空一行与body隔开
                elif (file_path.endswith(".mp4")):
                    response_headers += "Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + "\r\n"
                    logger.info("Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + " ")
                    response_headers += "Content-Type: MP4\r\n"
                    logger.info("Content-Type: MP4 ")
                    response_headers += "Content-Length:" + str(data_length) + "\r\n"
                    logger.info("Content-Length:" + str(data_length) + " ")
                    response_headers += "\r\n"  # 空一行与body隔开
                elif (file_path.endswith(".ico")):
                    response_headers += "Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + "\r\n"
                    logger.info("Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + " ")
                    response_headers += "Content-Type: ICO\r\n"
                    logger.info("Content-Type: ICO ")
                    response_headers += "Content-Length:" + str(data_length) + "\r\n"
                    logger.info("Content-Length:" + str(data_length) + " ")
                    response_headers += "\r\n"  # 空一行与body隔开
                elif (file_path.endswith(".css")):
                    response_headers += "Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + "\r\n"
                    logger.info("Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + " ")
                    response_headers += "Content-Type: text/css\r\n"
                    logger.info("Content-Type: text/css ")
                    response_headers += "Content-Length:" + str(data_length) + "\r\n"
                    logger.info("Content-Length:" + str(data_length) + " ")
                    response_headers += "\r\n"  # 空一行与body隔开
                elif (file_path.endswith(".js")):
                    response_headers += "Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + "\r\n"
                    logger.info("Date:" + str(datetime.utcnow().strftime(GMT_FORMAT)) + " ")
                    response_headers += "Content-Type: text/javascript\r\n"
                    logger.info("Content-Type: JS")
                    response_headers += "Content-Length:" + str(data_length) + "\r\n"
                    logger.info("Content-Length:" + str(data_length) + " ")
                    response_headers += "\r\n"  # 空一行与body隔开

                # response_headers += "\r\n"  # 空一行与body隔开
                # print("response_header:")
                # print(response_headers)
            # 返回数据给浏览器
            client_socket.send(response_headers.encode("utf-8"))  # 转码utf-8并send数据到浏览器
            client_socket.send(response_body)  # 转码utf-8并send数据到浏览器
            FileNotFoundIndicator = False
            NoRights = False
            # except:
            #     # 如果没有找到文件，那么就打印404 not found
            #     # 设置返回的头信息 header
            #     print("exception case!")
            #     response_headers = "HTTP/1.1 404 not found\r\n"  # 200 表示找到这个资源
            #     response_headers += "\r\n"  # 空一行与body隔开
            #     print("WARNING MESSAGE: There is no such file so the server directly reply test2.html as a feedback!")
            #     response_body = "<h1>sorry,file not found</h1>"
            #     response = response_headers + response_body
            #     client_socket.send(response.encode("utf-8"))

    def start_response(self, status, header):
        self.application_header = [status, header]
        # print("application_header=", self.application_header)


def main():
    # login page
    global Userdirectory
    layout = [
        [PySimpleGUI.Text("Please login your server account to start the server!")],
        [PySimpleGUI.Text("username"), PySimpleGUI.InputText(do_not_clear=False)],
        [PySimpleGUI.Text("password"), PySimpleGUI.InputText(password_char="*", do_not_clear=False)],
        [PySimpleGUI.Button("login"), ]
    ]
    windows = PySimpleGUI.Window("Login page", layout)

    while True:
        event, values = windows.read()

        if event == PySimpleGUI.WIN_CLOSED:
            windows.close()
            break
        if event == "login":
            username = values[0]
            password = values[1]
            accountUsername = ["john","richard"]
            accountPassword = ["123","456"]
            if username not in accountUsername:
                PySimpleGUI.PopupNoButtons("WRONG USERNAME!")
                continue
            else:
                if username == accountUsername[0] and password != accountPassword[0]:
                    PySimpleGUI.PopupNoButtons("WRONG PASSWORD!")
                    continue
                elif username == accountUsername[0] and password == accountPassword[0]:
                    # 通过sys.argv来获取服务端的端口号
                    print("Now you enter as server user: john !")
                    print("You can only request the file in the directory under 'john/' !")
                    Userdirectory += "john/"
                    windows.close()
                    # server_port = int(sys.argv[1])
                    webserver = WebServer(80)
                    webserver.start_http_service(80)
                    break
                elif username == accountUsername[1] and password != accountPassword[1]:
                    PySimpleGUI.PopupNoButtons("WRONG PASSWORD!")
                    continue
                elif username == accountUsername[1] and password == accountPassword[1]:
                    # 通过sys.argv来获取服务端的端口号
                    print("Now you enter as server user: richard !")
                    print("You can only request the file in the directory under 'richard/' !")
                    Userdirectory += "richard/"
                    windows.close()
                    # server_port = int(sys.argv[1])
                    webserver = WebServer(80)
                    webserver.start_http_service(80)
                    break

if __name__ == "__main__":
    main()
