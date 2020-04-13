import gevent
from gevent import monkey;monkey.patch_all()
import requests
import re
import multiprocessing
import optparse

# 输出到的文件
f = open('proxy.txt','a+')
class IpProxy(object):
    # 获取进程数目,协程数目,爬取页数
    def __init__(self, Proce_Num, Geve_Num, page):
        self.Proce_Num = Proce_Num
        self.Geve_Num = Geve_Num
        # 获取网页ip和端口的正则表达式
        self.r = re.compile("<td>((?:\d{0,3}\.){3}\d{0,3})</td><td>(\d{0,5})</td>")
        self.page = page
        # 设置每个进程爬取的url个数
        self.step = self.page//self.Proce_Num
        # 进程锁
        self.lock = multiprocessing.Lock()
        # 请求头
        self.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
        }

    # 用来获取网页匹配到的IP和端口
    # begin: 开始爬取的url
    # end:   结束的url
    def GetIp(self,begin,end):
        # 爬取的目标url
        url = 'http://www.66ip.cn/{}.html'
        data = []
        for i in range(begin,end):
            res = requests.get(url.format(i),headers=self.headers).text
            for ip,port in self.r.findall(res):
                # 用CheckIp来验证ip的有效性
                data.append(gevent.spawn(self.CheckIp,ip,port))
        # 下面代码是自己写的协程池
        i = 0
        # 此循环用来根据设置的协程中数来创建和执行我们设置的协程个数
        while len(data)//self.Geve_Num!=i:
            print('-'*40)
            gevent.joinall(data[i*self.Geve_Num:(i+1)*self.Geve_Num])
            i+=1
        # 因为有可能数据和协程数不会整除,所以这里要判断一下,然后把剩下的数据也进行执行
        if(len(data)%self.Geve_Num!=0):
            gevent.joinall(data[i*self.Geve_Num:])
        # 用来获取每个协程执行后的结果,然后并且写入到文件中
        for i,g in enumerate(data):
            self.lock.acquire()
            if(g.value!=None):
                f.write(g.value)
            self.lock.release()


    # 验证代理是否可用
    # ip: ip
    # port: 端口
    def CheckIp(self, ip, port):
        url = 'http://ifconfig.me/ip'
        proxy = ip + ":" + str(port)
        proxies = {'http': 'http://' + proxy}
        s = ''
        try:
            requests.get(url, timeout=5, proxies=proxies)
            print(proxies)
            s = str(proxies)+"\n"
            proxies = {'https': 'https://' + proxy}
            requests.get(url, timeout=5, proxies=proxies)
            print(proxies)
            s = s+ str(proxies)+"\n"
            return s
        except Exception as e:
            pass

    def run(self):
        all_process = []
        # 让我们的page和进程数可用整除
        temp = (self.page-(self.page%self.Proce_Num))
        # 分配每个进程执行多少个url
        for i in range(0, temp,self.step):
            p = multiprocessing.Process(target=self.GetIp, args=(i+1,i+1+self.step))
            all_process.append(p)
        # 因为存在不整除的情况所以要把剩余的url也加入到最后一个进程中
        if(self.page%self.Proce_Num!=0):
            all_process[-1]=multiprocessing.Process(target=self.GetIp,args=(temp-self.step+1,self.page+1))
        for p in all_process:
            p.start()
            p.join()

    def __del__(self):
        f.close()

if __name__ == '__main__':
    parse = optparse.OptionParser(usage="proxy.py -p 10 -t 20")
    parse.add_option('-n', '--number', dest='page', help='Page Number')
    parse.add_option('-p', '--process', dest='process', help='Process Number')
    parse.add_option('-g', '--gevent', dest='gevent', help='gevent Number')
    option, args = parse.parse_args()
    Process_Num = option.process if option.process == '' else 3
    Gevent_Num = option.gevent if option.gevent == '' else 50
    Page = option.page if option.page == '' else 10
    a = IpProxy(int(Process_Num), int(Gevent_Num), Page)
    a.run()