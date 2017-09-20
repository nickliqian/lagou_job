import requests
import json
import jsonpath
import urllib.parse
import time
from lxml import etree
from ManyUserAgents import getRandomUserAgent
from ManyProxes import getProxy,getSingleProxy
from queue import Queue
import threading


COOKIE = "user_trace_token=20170625144619-63cec145-7f03-4842-9935-ecf8977da4de; LGUID=20170625144629-04790cdb-5972-11e7-9e77-5254005c3644; index_location_city=%E6%B7%B1%E5%9C%B3; SEARCH_ID=8aafa92a57ff48c3a2f96e1ed136f2a2; TG-TRACK-CODE=search_code; JSESSIONID=ABAAABAAAFCAAEG33FE6E85472900086188CEB0ED794EBA; PRE_UTM=; PRE_HOST=; PRE_SITE=https%3A%2F%2Fwww.lagou.com%2Fjobs%2Flist_Java%3Fpx%3Ddefault%26city%3D%25E6%25AD%25A6%25E6%25B1%2589; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fjobs%2F3452360.html; X_HTTP_TOKEN=ef652cd49729dfb093d29a21177ecf4f; _gat=1; _gid=GA1.2.403225151.1505731071; _ga=GA1.2.583651597.1498373218; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1504182210,1504934501,1505731074,1505821830; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1505830430; LGSID=20170919214406-9b3cee90-9d40-11e7-91c6-5254005c3644; LGRID=20170919221352-c3e19a87-9d44-11e7-99c6-525400f775ce"

# 获取关键词下所有页面工作的jobid
def getjoblist(city, keyword):
	# The url and params of ajax reqeust.
	url = 'https://www.lagou.com/jobs/positionAjax.json'
	params = {
		'px' : 'default',
		'city' : city,
		'needAddtionalResult' : 'false',
		'isSchoolJob' : '0',
	}
	# This post request need headers with different Referer
	Referer_words = {
		'px' : 'default',
		'city' : city,
	}
	Referer_url = "https://www.lagou.com/jobs/list_?"
	Referer = Referer_url + urllib.parse.urlencode(Referer_words)
	# headers
	headers = {
		"Referer" : Referer,
		"User-Agent" : getRandomUserAgent(),
		"Cookie" : COOKIE,
	}
	# offset is job list page
	offset = 1
	all_job_list = []
	while True:
		formdata = {
			'first' : 'true',
			'pn' : str(offset),
			'kd' : keyword,
		}

		timeout = 4
		while timeout > 0:
			timeout -= 1
			try:
				proxies = {'http' : 'http://'+getSingleProxy()}
				response = requests.post(url, headers=headers, data=formdata, proxies=proxies, params=params)
				break
			except Exception as e:
				print('***list_request_failed:', e, url)
		if timeout <= 0:
			print('***timeout:', url)
			return []

		content = json.loads(response.text)
		company_list = jsonpath.jsonpath(content, '$..companyId')
		job_list = jsonpath.jsonpath(content, '$..positionId')
		if job_list == False:
			break
		print(job_list)
		all_job_list += job_list
		offset += 1

	return all_job_list


# 提供job_id，获取该job_id页面下工作的信息
def get_job_detail(job_id):
	headers = {
		"User-Agent" : getRandomUserAgent(),
		"Cookie" : COOKIE,	
		}
	url = 'https://www.lagou.com/jobs/' + str(job_id) + '.html'

	timeout = 4
	while timeout > 0:
		timeout -= 1
		try:
			proxies = {'http' : 'http://'+getSingleProxy()}
			response = requests.get(url, headers=headers, proxies=proxies)
			break
		except Exception as e:
			print('***detail_request_failed:', e, url)
	if timeout <= 0:
		print('***timeout:', url)
		return ''

	print('-->Request Info')
	print('status:',response,proxies)
	print('url:',response.url)
	print('history:',response.history)
	

	return response

# 使用xpath解析单个页面
def parse_html(response, job_id):
	
	if response == '':
		return {'job_id':job_id}

	item = {}

	try:
		html = etree.HTML(response.text)
	except Exception as e:
		print('Failed to transform etree, maybe you can retry, url: %s'%response.url)

	# 工作编号
	item['job_id'] = job_id

	# 发布时间
	try:
		publish_time = html.xpath('//p[@class="publish_time"]/text()')
		item['publish_time'] = publish_time[0].split(' ')[0].strip()
	except:
		item['publish_time'] = 'NULL'

	# 公司名称
	try:
		item['company_name'] = html.xpath('//div/div[@class="company"]/text()')[0]
	except:
		item['company_name'] = 'NULL'
	# 职位名称
	try:
		item['job_name'] = html.xpath('//div/span[@class="name"]/text()')[0]
	except:
		item['company_name'] = 'NULL'
	# 职位要求
	job_adt = html.xpath('//dd[@class="job_request"]/p/span/text()')
	job_adt_list = ''.join(job_adt).replace(' ','').split('/')
	item['salary'],item['location'],item['experience'],item['education'],item['how_time'] = job_adt_list

	# 职位标签
	try:
		item['job_tag'] = html.xpath('//ul[@class="position-label clearfix"]/li/text()')
	except:
		item['job_tag'] = 'NULL'

	# 职位诱惑
	try:
		job_reward = html.xpath('//dd[@class="job-advantage"]/p/text()')
		item['job_reward'] = job_reward[0].split('')
	except:
		item['job_reward'] = 'NULL'

	# 职位描述
	try:
		job_desc = html.xpath('//dd[@class="job_bt"]/div/p/text()')
		item['job_desc'] = '-'.join(job_desc)
	except:
		item['job_desc'] = 'NULL'

	# 地址
	try:
		job_addr_a = html.xpath('//div[@class="work_addr"]/a/text()')
		job_addr_a = job_addr_a[:-1]
		job_addr_b = html.xpath('//div[@class="work_addr"]/text() ')
		job_addr_b = ''.join(job_addr_b).replace('\n','').replace('-','').strip()
		item['job_addr'] = job_addr_a + job_addr_b
	except:
		item['job_addr'] = 'NULL'

	# 聊天意愿/简历处理/活跃时段
	try:
		hr_status = html.xpath('//span[@class="data"]/text()')
		item['hr_chat'] = hr_status[0]
		item['hr_view_resume'] = hr_status[1]
		item['hr_online'] = hr_status[2]
	except:
		item['hr_chat'] = 'NULL'
		item['hr_view_resume'] = 'NULL'
		item['hr_online'] = 'NULL'

	# 回复率--  用时2小时/处理率100%  用时1天 /下午2点最活跃
	try:
		hr_deal= html.xpath('//span[@class="tip"]/i/text()')
		item['hr_char_rate'] = hr_deal[0]
		item['hr_char_time'] = hr_deal[1]
		item['hr_view_rate'] = hr_deal[2]
		item['hr_view_time'] = hr_deal[3]
		item['hr_online_always'] = hr_deal[4]
	except:
		item['hr_char_rate'] = 'NULL'
		item['hr_char_time'] = 'NULL'
		item['hr_view_rate'] = 'NULL'
		item['hr_view_time'] = 'NULL'
		item['hr_online_always'] = 'NULL'

	item['comment'] = post_comment(job_id)



	print('-->Item Data')
	print(item)
	return item

# 描述相符 面试官 公司环境 star tag interview-process
def post_comment(job_id):
	url = 'https://www.lagou.com/interview/experience/byPosition.json'

	formdata = {
		'positionId':str(job_id),
		'pageSize':'500'
	}

	headers = {
		"X-Requested-With":"XMLHttpRequest",
	    "User-Agent": getRandomUserAgent(),
		"Cookie" : COOKIE,	
		}

	timeout = 4
	while timeout > 0:
		timeout -= 1
		try:
			proxies = {'http' : 'http://'+getSingleProxy()}
			response = requests.post(url,headers=headers,data=formdata,proxies=proxies)
			jsonobj = json.loads(response.text)
			result_list = jsonpath.jsonpath(jsonobj,'$..result')[0]
			return result_list
			break
		except Exception as e:
			print('***comment_request_failed:', e, url)
	if timeout <= 0:
		print('***timeout:', url)
		return []

'''
职位链接
https://www.lagou.com/jobs/3178430.html
公司链接
https://www.lagou.com/gongsi/j17311.html
'''