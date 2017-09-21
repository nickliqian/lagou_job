import requests
import json
import jsonpath
import urllib.parse
import time
from lxml import etree
from ManyUserAgents import getRandomUserAgent
from ManyProxes import getProxy,getSingleProxy
from queue import Queue
import queue
import threading
from LagouRequestAndParse import getjoblist,get_job_detail,parse_html
import csv


# 多线程获取job_id
class GetJobList(threading.Thread):
	def __init__(self, city_typeQueue,  job_listQueue):
		super(GetJobList, self).__init__()
		self.city_typeQueue = city_typeQueue
		self.job_listQueue = job_listQueue

	def run(self):
		while not self.city_typeQueue.empty():
			city, keyword = self.city_typeQueue.get()
			job_id_list = getjoblist(city, keyword)
			time.sleep(2)
			for job_id in job_id_list:
				self.job_listQueue.put((job_id,keyword))
	
# 多线程请求单个职位页面
class GetJobDetail(threading.Thread):
	def __init__(self, job_listQueue, lock, output):
		super(GetJobDetail, self).__init__()
		self.job_listQueue = job_listQueue
		self.lock = lock
		self.output = output

	def run(self):
		while True:
			try:
				job_id,keyword = self.job_listQueue.get(timeout=60)
				resposne = get_job_detail(job_id)
				item = parse_html(resposne, job_id, keyword)
				with self.lock:
					data = json.dumps(item,ensure_ascii=False).encode('gbk','ignore')
					data = str(data, encoding='gbk', errors='ignore')
					self.output.write(data + ',')
				time.sleep(2)
			except queue.Empty:
				print('***Info: timeout > 60, break!')
				break

def main():
	# 加上一个log文件

	city_list = ['深圳', '北京', '广州' ,'上海', '武汉', '杭州', '成都']
	job_type_list = ['python','java', 'php', 'go', 'Android', 'C', 'C++']
	city_typeQueue = Queue()
	job_listQueue = Queue()
	lock = threading.Lock()
	output = open('lagou_data.json', 'w')
	output.write('[')

	# 搜索条件存入队列
	for city in city_list:
		for keyword in job_type_list:
			condition = (city, keyword)
			city_typeQueue.put(condition)

	# 创建五个线程
	jobList = []
	for i in range(10):
		t1 = GetJobList(city_typeQueue, job_listQueue)
		t1.start()
		jobList.append(t1)

	# 创建五个线程
	jobdetail = []
	for i in range(10):
		t2 = GetJobDetail(job_listQueue, lock, output)
		t2.start()
		jobList.append(t2)

	for i in jobList:
		i.join()
	for i in jobdetail:
		i.join()

	with lock:
		output.write(']')
		output.close()

if __name__ == '__main__':
	main()