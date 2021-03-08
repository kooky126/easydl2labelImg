#coding=utf-8
#baidu ai easydl toolkit by kooky126
import urllib.request
import os
import json
import re
import cv2
import socket
from xml.etree import ElementTree as ET
import http.cookiejar
import hashlib

#初始化lableImg的dom主体数据，只包含图片数据，不含标注数据
#name：图片文件名
#path：lableImg工作目录
def initxml(path,name):
	img = cv2.imread(path+os.sep+name)
	imgheight, imgwidth,imgdepth =img.shape
	annotation=ET.Element("annotation")
	folder=ET.Element("folder")
	folder.text = "folder"
	annotation.append(folder)
	filename=ET.Element("filename")
	filename.text = name
	annotation.append(filename)
	pathe=ET.Element("path")
	pathe.text = path+name
	annotation.append(pathe)
	source=ET.Element("source")
	database=ET.SubElement(source,'database')
	database.text = "Unknown"
	annotation.append(source)
	size=ET.Element("size")
	width=ET.SubElement(size,'width')
	width.text = "{:d}".format(imgwidth)
	height=ET.SubElement(size,'height')
	height.text = "{:d}".format(imgheight)
	depth=ET.SubElement(size,'depth')
	depth.text = "{:d}".format(imgdepth)
	annotation.append(size)
	segmented=ET.Element("segmented")
	segmented.text = "0"
	annotation.append(segmented)
	return annotation

#将一个标注数据加入到xml中
#annotation:dom主体
#location:标注数据，包含name，location，location下包含left，top，width，height
def appobj(annotation,label):
	object=ET.Element("object")
	name=ET.SubElement(object,'name')
	name.text = label["name"]
	pose=ET.SubElement(object,'pose')
	pose.text = "Unspecified"
	truncated=ET.SubElement(object,'truncated')
	truncated.text = "0"
	difficult=ET.SubElement(object,'difficult')
	difficult.text = "0"
	bndbox=ET.SubElement(object,'bndbox')
	xmin=ET.SubElement(bndbox,'xmin')
	xmin.text = "{:d}".format(label["x1"])
	ymin=ET.SubElement(bndbox,'ymin')
	ymin.text = "{:d}".format(label["y1"])
	xmax=ET.SubElement(bndbox,'xmax')
	xmax.text = "{:d}".format(label["x2"])
	ymax=ET.SubElement(bndbox,'ymax')
	ymax.text = "{:d}".format(label["y2"])
	annotation.append(object)

#将dom保存到xml文件
#annotation:dom主体
def savexml(annotation):
	imgfile = annotation.find("path").text
	xmlfile = imgfile.replace(".jpg",".xml")
	if not os.path.exists(xmlfile):	
		print("正在创建xml文件："+xmlfile)
		tree=ET.ElementTree(annotation)
		tree.write(xmlfile)

#将easydl的labels插入到dom主体中
#name：图片文件名
#path：lableImg工作目录
#labels：easydl数据集中的标注数据
def labels2xml(path,name,labels):
	annotation=initxml(path,name)
	for label in labels:
		appobj(annotation,label)
	savexml(annotation)

#附带cookie取easydl数据
#request_url：要取的链接
#params：附加参数
#type：取的数据类型，仅json和image
def getwithcookie(request_url,params,type="json"):
	try:
		request = urllib.request.Request(url=request_url, data=params)
		if type == "json":
			request.add_header("Accept","application/json, text/plain, */*")
			request.add_header("X-Requested-With","XMLHttpRequest")
			request.add_header("Content-Type","application/json;charset=UTF-8")
		else:
			request.add_header("Accept","image/webp,image/apng,image/*,*/*;q=0.8")
		#request.add_header("Accept-Encoding","gzip, deflate")
		request.add_header("Accept-Language","zh-CN,zh;q=0.9")
		request.add_header("Connection","keep-alive")
		jar = http.cookiejar.MozillaCookieJar()
		jar.load("cookie.txt", ignore_discard=True, ignore_expires=True)
		cookie = ""
		for c in jar:
			cookie += c.name + '=' + c.value + '; '
		request.add_header("Cookie",cookie)
		request.add_header('Referer', 'http://ai.baidu.com/')
		request.add_header("User-Agent","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
		response = urllib.request.urlopen(request,timeout=60)
		content = response.read()
		return content
	except socket.timeout:
		print("下载失败，重试……")
		return getwithcookie(request_url,params,type)

#附带cookie下载数据集中的图片，保存在path下，文件名未上传时的文件名，如果重名会忽略
#url：图片url
#name：图片文件名
#path：labelimg工作目录
def downloadimage(url,path,name):
	if not os.path.exists(path+name):
		print("正在下载图片："+url+" => "+path+name+";")
		content = getwithcookie(url,None,"image")
		with open(path+os.sep+name, 'wb') as f:
			f.write(content)   

#获取数据集json数据
#dataset_id：easydl数据集id
#path：lableImg的数据目录
#annotated:数据集中的分类，1：已标注，2：未标注
#offset：页面偏移量，第一页为0
def getdateset(dataset_id,annotated=1,offset=0):
	request_url = "http://ai.baidu.com/easydl/api"
	req = {}
	req['type'] = 2
	req['annotated'] = annotated
	req['datasetId'] = dataset_id
	req['offset'] = offset
	req['method'] = "entity/list"
	req['pageSize'] = 12
	req['labelName'] = None
	params = bytes(json.dumps(req),"utf8")
	content = getwithcookie(request_url,params)
	data = json.loads(content.decode('utf-8'))
	return data

#下载easydl数据集的一页数据并转换为labelImg规格
#dataset_id：easydl数据集id
#path：lableImg的数据目录
#annotated:数据集中的分类，1：已标注，2：未标注
#offset：页面偏移量，第一页为0
def downloaddatesetpage(dataset_id,path,annotated=0,offset=0):
	size=0
	data = getdateset(dataset_id,annotated,offset)
	#print(data)
	if 'success' in data:
		if data['success']:
			if 'result' in data:
				#total = data['result']['total']
				#entityCount = data['result']['entityCount']
				if 'items' in data['result']:
					size = len(data['result']['items'])
					for object in data['result']['items']:
						name = object['id']+".jpg"
						url = object['compress']
						if url[0]=='/':
							url = "http:"+url
						downloadimage(url,path,name)
						#如果是已标注的，同时生成xml文件
						if annotated==1:
							labels2xml(path,name,object['labels'])
		else:
			print(data['message']['global'])
	return annotated,size

#下载easydl数据集的数据并转换为labelImg规格
#dataset_id：easydl数据集id
#path：lableImg的数据目录
def downloaddateset(dataset_id,path):
	if os.path.exists(path):
		#从已标注的第一页开始处理
		offset = 0
		annotated = 1
		annotated,size = downloaddatesetpage(dataset_id,path,annotated,offset)
		#循环，未标注页的数据不足12则表示全部数据取完
		while annotated==1 or size==12:
			if size<12:
				annotated=annotated+1
				offset=0
			else:
				offset=offset+12
			annotated,size = downloaddatesetpage(dataset_id,path,annotated,offset)
		print("处理完成")
	else:
		print("工作目录不存在，请先创建工作目录")
