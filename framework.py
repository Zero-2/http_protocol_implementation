import re
import time

# 支撑WGSI协议
def application(environ, start_response, FileNotFoundIndicator, Userdirectory, NoRights):
    start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
    # 接受需要打开的文件路径
    print("dynamic_file_path= ", environ['REQUEST_URI'])

    file_path = re.sub(r".py", ".html", environ['REQUEST_URI'])
    if(NoRights ==True):
        with open( Userdirectory+"404.html","rb") as f:
            response_body = f.read()
        esponse_body = response_body.decode("UTF-8")
        NoRights = False
    elif(FileNotFoundIndicator == True):
        with open( Userdirectory+"index.html","rb") as f:
            response_body = f.read()
        response_body = response_body.decode("UTF-8")
        FileNotFoundIndicator = False
    else:
        response_body = "hello! Welcome to use the dynamic request"

    return response_body, FileNotFoundIndicator, NoRights

# def encode(s):
#     return ' '.join([bin(ord(c)).replace('0b','') for c in s])