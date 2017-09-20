import json
import csv

filename = input('请输入要转换文件的名称：')

with open(filename,'r',encoding='utf-8') as f:

	text = f.read().replace(',]',']')

	content = json.loads(text)

	with open(filename + 'COPY.csv','w',encoding='utf-8',newline='') as csvfile:

		writer = csv.writer(csvfile)

		i = 1
		for each in content:

			if i == 1:
				writer.writerow(each.keys())

			writer.writerow(each.values())
			print('insert %d'%i)
			i += 1