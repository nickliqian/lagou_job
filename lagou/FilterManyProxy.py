#coding=utf-8

import requests
from queue import Queue
import threading
import time
import re
from ManyUserAgents import getRandomUserAgent



# testurl = 'http://www.baidu.com'
testurl = 'https://mp.weixin.qq.com/s/PxxuPQX2LsY0vZIqsa6XWw'
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"
}

class IPTest(threading.Thread):
    def __init__(self,beforeQueue,afterQueue):
        threading.Thread.__init__(self)
        self.beforeQueue = beforeQueue
        self.afterQueue = afterQueue

    def run(self):
        # 测试，筛选，构造代理IP
        while True:
            if self.beforeQueue.empty():
                break
            else:
                ip = self.beforeQueue.get()
                proxies = {'http': 'http://' + ip,}
                userage = ip_test(proxies)
                if userage == 1:
                    self.afterQueue.put(ip)


def get_ip_list(testNUM):
    # 从代理网站获取免费代理IP
    apifreeurl = 'http://www.66ip.cn/nmtq.php?getnum='+str(testNUM)+'&isp=0&anonymoustype=4&start=&ports=&export=&ipaddress=&area=0&proxytype=0&api=66ip'
    # 从代理网站获取收费代理IP
    apiurl = 'http://www.66ip.cn/getzh.php?getzh=2017092063988&getnum='+str(testNUM)+'&isp=0&anonymoustype=4&start=&ports=&export=&ipaddress=&area=0&proxytype=0&api=https'
    testProxy = requests.get(url=apiurl, headers=headers, timeout=5)
    text = testProxy.text
    proxyList = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)<br>',text) 
    # 返回代理IP的，存入队列
    return proxyList


def ip_test(proxies):
    headers = {"User-Agent":getRandomUserAgent()}
    # 测试代理IP，通过返回1，不通过返回0
    try:
        responseP = requests.get(url=testurl, headers=headers, proxies=proxies, timeout=10)
        if responseP.status_code == 200:
            return 1
    except:
        return 0


def ip_to_json(afterQueue):
    import json
    # 代理IP写入文件
    total = 0
    good_ip_list = []
    # IP写入列表
    while True:
        if afterQueue.empty():
            break
        else:
            good_ip_list.append(afterQueue.get())
            total += 1
    # IP写入文件
    with open('ip_data.json','a') as f:
        f.write(json.dumps(good_ip_list, ensure_ascii=False))
    return total


def ip_to_redis(set_name,afterQueue):
    import redis
    client = redis.Redis(host="127.0.0.1", port=6379)
    # 代理IP写入文件
    total = 0
    good_ip_list = []
    # IP写入列表
    while True:
        if afterQueue.empty():
            break
        else:
            client.sadd(set_name, afterQueue.get().encode('utf-8'))
            total += 1
    return total


def main():
    stime = time.time()
    # 线程个数
    threadNUM = 30
    # 测试的IP数量
    testNUM = 100
    beforeQueue = Queue()
    afterQueue = Queue()

    print("正在获取代理ip...")
    ip_list = get_ip_list(testNUM)
    
    print("正在测试代理ip...")
    for ip in ip_list:
        beforeQueue.put(ip)

    # 多个线程测试ip
    tlist = []
    for i in range(threadNUM):
        t = IPTest(beforeQueue,afterQueue)
        t.start()
        tlist.append(t)
    for t in tlist:
        t.join()

    # total = ip_to_json(afterQueue)
    # 存入ip到指定名称的Redis集合中去
    total = ip_to_redis('proxy_ip',afterQueue)

    print('\n<--------INFO--------->')
    print('有用的IP个数是：',total)
    print('使用的线程数量是：%d'%threadNUM)
    print('筛选的IP数量为：%d个'%testNUM)
    print('检测完耗时：%fs'%(time.time()-stime))
    print('已经写入完毕。')



if __name__=='__main__':
    main()