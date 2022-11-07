#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-10-24 10:05
# @Author   : NING MEI
# @Desc     :


#------------------------------------------------------------
#   案例文本结构化信息抽提
#------------------------------------------------------------



import os
import time
from collections  import defaultdict
from typing import List, Dict, Union
from paddlenlp import Taskflow
from process.vars import *
from process.utils import uie_postprocess
from process.utils import paragraph_spliter
import asyncio



def model_init():
	MODEL = Taskflow(task='information_extraction',
	                 schema=templates['uie_task'],
	                 task_path=custom_model_path)

	return MODEL



def uie_task(text:str):
	""" 信息抽提 """
	patten = re.compile("[\w|\d]")
	if len(re.findall(patten, text)) < 4 or len(re.findall(patten, text)) > 512:
		return {}

	else:
		res = uie_postprocess(MODEL(text))[0]
		return res


def docment_extract(doc):
	""" 文本信息抽提 """
	url = doc['url']
	doc_txt = [d.get('txt') for d in doc.get('medias') if d.get('txt')]
	doc_id = url.split("/")[-2]

	if doc_txt:
		save_file = os.path.join(save_dir, f"{doc_id}.json")
		start = time.time()
		data = defaultdict(list)
		data["url"] = url

		if len("\n".join(doc_txt)) < 512:
			_res = uie_task("\n".join(doc_txt))
			if _res and any([_res.get("ner", ""), _res.get("triplets", "")]):
				_res_item = {
					"sentence": "\n".join(doc_txt),
					"ner": _res.get("ner", ""),
					"triplets": _res.get("triplets", "")
					}
				data["item"].append(_res_item)

		else:
			for paragraph in doc_txt:
				para_texts = paragraph_spliter(paragraph)
				for text in para_texts:
					_res = uie_task(text)
					if _res and any([_res.get("ner", ""), _res.get("triplets", "")]):
						_res_item = {
							"sentence": text,
							"ner": _res.get("ner", ""),
							"triplets": _res.get("triplets", "")
							}
						data["item"].append(_res_item)

		if data["item"]:
			print(json.dumps(dict(data), ensure_ascii=False, indent=True), file=open(save_file, 'w'))
			print(f"url={url}, cost: {time.time() - start}")



def zm_dataset(save_dir):
	import json
	import time
	from glob import glob
	zm_data = json.load(open("./zhimo_all.json", 'r'))
	if not os.path.exists(save_dir): os.makedirs(save_dir)
	done_files = [os.path.splitext(os.path.basename(x))[0] for x in glob(save_dir + "/*.json") if x]
	# zm_data = [x for i, x in enumerate(zm_data) if (x.get('url').split("/")[-2] not in done_files)]

	# zm_data = zm_data[::-1]

	# tasks = [docment_extract(doc) for doc in zm_data]
	# loop = asyncio.get_event_loop()
	# loop.run_until_complete(asyncio.wait(tasks))
	# loop.close()

	for i, doc in enumerate(zm_data):
		url = doc['url']
		doc_id = url.split("/")[-2]
		if doc_id not in done_files:
			print(f"当前处理：i = {i} , doc_id={doc_id}")
			docment_extract(doc)

		# else:
		# 	print(f"已处理：i = {i} , doc_id={doc_id}")




# print(custom_model_path)

MODEL = None
if MODEL is None:
	MODEL = model_init()



if __name__ == '__main__':
	text =  "在项目之初，Stack结合上海特有的文化现象，将古典、雅致与都市的现代开放相结合，同时，在设计手法上植入法式长窗等抽象元素，塑造国际化的生活方式。"
	print(uie_task(text))

	save_dir = "output/uie_items"
	zm_dataset(save_dir)

