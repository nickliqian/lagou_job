import redis

def getProxy(num, host='127.0.0.1', port=6379, set_name='proxy_ip'):
	if not isinstance(num, int):
		num = int(num)
	client = redis.Redis(host='127.0.0.1', port=6379)
	proxy_list = client.srandmember(set_name, num)
	proxy_list = map(lambda ip:str(ip, encoding='utf-8'), proxy_list)
	return list(proxy_list)

def getSingleProxy(host='127.0.0.1', port=6379, set_name='proxy_ip'):
	client = redis.Redis(host='127.0.0.1', port=6379)
	proxy_list = client.srandmember(set_name, 1)
	proxy = str(proxy_list[0], encoding='utf-8')
	return proxy

def printProxyNums(set_name):
	client = redis.Redis(host='127.0.0.1', port=6379)
	print(client.scard(set_name))


def main():
	printProxyNums('proxy_ip')

if __name__ == '__main__':
	main()