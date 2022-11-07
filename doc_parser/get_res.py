#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-11-07 10:35
# @Author   : NING MEI
# @Desc     :



import os
import json
from glob import glob
from collections import defaultdict


def load_json(file_in):
	return json.load(open(file_in, 'r', encoding='utf-8', errors='ignore'))


def get_uieinfo(res):
	d = defaultdict(list)
	if res[0]:
		res = res[0]
		for k, vs in res.items():
			v = [x.get("text") for x in vs]
			d[k].extend(v)

	return dict(d)


save_dir = "/data/1_qunosen/project/xhs/doc_parser/out"
out_jfile = glob("/data/1_qunosen/project/xhs/doc_parser/output/project_info2/raw/*.json")
for i, jfile in enumerate(out_jfile):
	jdat = load_json(jfile)

	url = jdat.get('url')
	data = jdat.get('data')
	text = [x.get("text") for x in data if x.get("text")]
	base_info = [x.get("info") for x in data if x.get("info")]
	base_uie = [get_uieinfo(x.get("uie_base")) for x in data if x.get("uie_base")]
	uie_info = [get_uieinfo(x.get("uie")) for x in data if x.get("uie") if x.get("uie")]

	# print("text: ", text)
	# print("base_info: ", base_info)
	# # print("base_uie: ", base_uie)
	# print("uie_info: ", uie_info)
	# print(" ********************************* ")

	savefile = os.path.join(save_dir, os.path.basename(jfile))
	print(savefile)
	print(json.dumps({"url": url, "info": uie_info}, ensure_ascii=False), file=open(savefile, 'w'))

