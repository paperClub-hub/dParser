#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-20 11:57
# @Author   : NING MEI
# @Desc     :

import os
import json
from dparser import DDParser
from dparser.dextract import *
from dparser.kextract import *


ddp = DDParser(prob=True)
wse = wordExtract()

def do_dextract(text, useFine=True):
    """ """
    ddp_res = ddp.parse(text)
    res_info = FineGrainedInfo(ddp_res[0]).parse() if useFine else CoarseGrainedInfo(ddp_res[0]).parse()
    
    del ddp_res
    # print(res_info)

    return res_info



if __name__ == '__main__':
    text = '我家客厅要装修成后现代风格的，88平米， 预算大概是4w+人民币。朋友家的卧室是北欧风格的，也差不多花了4w， 17平米。'
    text = '三室一厅的毛坯房，108平米，装修预算40万，希望主卧独卫，客厅放L形沙发，厨房干湿分离，餐厅为红木餐桌。'
    # text = '卫生间满足我们的需求做了三分离设计，在早上的使用高峰期或者多人使用起来更加方便。'

    cats, ws = wse.matched(text)
    res_info = do_dextract(text, True)
    print(res_info)
    print(cats, ws)

    
    
