#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-20 11:57
# @Author   : NING MEI
# @Desc     :

from dparser import DDParser
from dparser.extract.dextract import *
from dparser.extract.kextract import *
from dparser.extract.uie_task import *
from dparser.utils import util


ddp = DDParser()
kwe = wordExtract()
uie = UIE()

def do_dextract(text, useFine=True):
    """ """
    ddp_res = ddp.parse(text)
    res_info = FineGrainedInfo(ddp_res[0]).parse() if useFine else CoarseGrainedInfo(ddp_res[0]).parse()

    del ddp_res
    # print(res_info)

    return res_info



if __name__ == '__main__':
    text = '我计划装修房子，总面积108m², 套内88平米，预算40w+, 想装修成现代简约风格，客厅放L形沙发和玻璃茶几，方便会客，餐厅配置红木餐桌椅和水晶吊灯 。'
    # text = '三室一厅的毛坯房，108平米，装修预算40万，希望主卧独卫，客厅放L形沙发，厨房干湿分离，餐厅为红木餐桌。'
    # text = '卫生间满足我们的需求做了三分离设计，在早上的使用高峰期或者多人使用起来更加方便。'

    kwe_cat, ws = kwe.matched(text)
    print(kwe_cat, ws)
    res_info = do_dextract(text, True)
    print(res_info)

    _, base_res = uie.extract(text)
    uie_cat = [list(x.keys()) for x in base_res][0]
    task_schema = util.task_setting(kwe_cat, uie_cat)
    print(base_res)
    print(task_schema)
    _, task_res = uie.extract(text, task_schema)
    print(task_res)
    util.network(task_res)

    
    
