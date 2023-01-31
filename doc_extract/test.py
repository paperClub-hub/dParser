#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-01-03 12:30
# @Author   : NING MEI
# @Desc     :


import requests
import json




def test_title():


	params = {
		"text": '2017海滨城众茗阁茶楼',
		"isfilter": True,
	}

	resp = requests.post(url="http://192.168.0.17:5002/title",
	                     data=json.dumps(params)
	                     )

	print(resp.text)

	if resp.status_code == 200:
		return resp.text
	else:
		return {}


def test_content():
	params = {
		"texts": ['项目时间：2017 2017海滨城众茗阁茶楼'],
		"isfilter": True,
	}

	resp = requests.post(url="http://192.168.0.17:5002/content",
	                     data=json.dumps(params)
	                     )

	print(resp.text)



test_title()
test_content()
