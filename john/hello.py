import time
def application(env,startResponse):
    status = 'HTTP/1.1 200 OK'
    responseHeaders = [('Server','bfe/1.0.8.18'),('Date','%s'%time.ctime()),('Content-Type','text/plain')]
    startResponse(status,responseHeaders)

    responseBody = str(time.ctime())
    return responseBody