## Collec lagou.com data
<br>
### 项目文件说明
#### Crawl.py
- 调度器，使用多线程分别执行请求和解析响应的任务，并存到本地或者写入数据库。
- 需要提供目标关键词和城市。
#### LagouRequestAndParse.py
- 封装针对logou.com的请求函数和响应解析函数
- 需要提供cookie。
#### FilterManyProxy.py
- 从网络上获取免费的代理ip，并筛选可用的代理ip:port。
- 存入本地redis数据库的proxy_ip集合（不会重复）里面，形成可用的ip池。
- 或者存入本地json文件。
#### ManyProxes.py
- 调用getSingleProxy从reids中随机获得一个代理ip。
- 调用getProxy(n)从redis中随机获得n个代理ip。
- 调用printProxyNums显示redis中当前的可用代理ip个数。
- 调用checkProxy检测redis中代理ip的可用性，并刷新数据库（尚未完成）。
#### ManyUserAgents.py
- 调用getRandomUserAgent，返回一个随机的User-Agent。
#### json_To_Csv_File.py
- 一键将本项目中的json文件转为csv文件。

### 如何使用
打开Crawl.py

### 下一个版本

#### 1.增加manage.py文件
计划增加manage.py文件，并把项目修改为类似API的形式。只需输入关键词，城市列表和线程数量，即可输出一个包含这些城市的职位信息的json文件。
> **示例-->**  
>  **input:**  
>  city_list = [ '北京', '广州' ... ]  
>  job_type_list = ['python'，'java'...]   
>  threading_num = 10  
>  **output:**   
>  FILE: lagou_data.json

#### 2.改善代理池的灵活性
- 增加更多免费获取代理ip的网址。
- 没有数据库连接，ip直接存到本地文件。
- 没有数据库连接，从本地文件获取ip。
- 支持更多类型数据库管理代理ip。