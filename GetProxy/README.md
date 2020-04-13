# GetProxy

## 介绍
采用多进程+协程的方式进行爬取,爬取的内容会写入到proxy.txt
![运行结果](https://github.com/cuokon/MyTools/blob/master/GetProxy/end.png)
## 环境
python3
python库
```
gevent
multiprocessing
requests
re
optparse
```
### 用法
python3 proxy -h
![帮助信息](https://github.com/cuokon/MyTools/tree/master/GetProxy/help.png)
参数有
```
-h: 获取帮助信息
-p: 设置进程数,默认参数3
-g: 设置协程数,默认参数50
-n: 设置爬取页数,默认参数10
```