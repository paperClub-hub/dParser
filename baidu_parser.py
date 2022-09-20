#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-20 11:57
# @Author   : paperClub
# @Desc     :

import os
import json
from dparser import DDParser
from dparser.dextract import *
ddp = DDParser()





if __name__ == '__main__':
    
    text = '三室一厅的毛坯房，108平米，装修预算40万，希望主卧独卫，客厅放L形沙发，厨房干湿分离，餐厅为红木餐桌。'
    ddp_res = ddp.parse(text)
    fine_info = FineGrainedInfo(ddp_res[0])
    out = fine_info.parse()
    out = [tuple(filter(lambda i:i !=None, x[:-1][0])) for x in out]

    print("#" * 100)
    print(f"输入：{text}")
    print()

    print("解析结果：")
    for x in out:
        print(f" --- {x}")
