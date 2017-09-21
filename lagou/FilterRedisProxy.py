#coding=utf-8

import requests
from queue import Queue
from multiprocessing.dummy import Pool
import multiprocessing
import time
from ManyUserAgents import getRandomUserAgent
import redis

rmQueue = Queue()
def ip_test(proxies,rmQueue):
    global rmQueue
    testurl = 'http://www.baidu.com'
    # 测试代理IP，通过返回1，不通过返回0
    try:
        proxies = {'http':'http://'+str(proxies, encoding='utf-8')}
        headers = {"User-Agent":getRandomUserAgent()}
        response = requests.get(url=testurl, headers=headers, proxies=proxies, timeout=10)
        print('ok:',response)
        rmQueue.put(proxies)
    except Exception as e:
        print('error', e)

def main():
    stime = time.time()
    threadNUM = 30

    # 链接数据库
    client = redis.Redis(host="127.0.0.1", port=6379)
    beforeNum = client.scard("proxy_ip")
    proxes_list = client.smembers('proxy_ip')

    # 任务加入线程池
    pool = Pool(30)
    pool.map(ip_test, proxes_list)
    pool.close()
    pool.join()

    # 移除没有用的代理
    while not rmQueue.empty():
        client.srem("proxy_ip", rmQueue.get())
    
    afterNum = client.scard("proxy_ip")

    print('\n<--------INFO--------->')
    print('使用线程：%d个'%threadNUM)
    print('数据库原有ip：%d个：',beforeNum)
    print('数据库筛选后剩余ip：%d个：',afterNum)
    print('清理的IP数量为：%d个'%(beforeNum-afterNum))
    print('检测完耗时：%fs'%(time.time()-stime))
    print('处理完毕。')

if __name__=='__main__':
    multiprocessing.freeze_support()
    main()