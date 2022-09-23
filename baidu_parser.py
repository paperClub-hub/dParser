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
from dparser.utils import util, process



ddp, kwe, uie = None, None, None
if any([model is None for model in [ddp, kwe, uie]]):
    ddp = DDParser()
    kwe = wordExtract()
    uie = UIE()

def extractor(text, useFine=True, threshold=0.99, add_fine=True, without_non=True):
    ddp_res = ddp.parse(text)
    kwe_cat, ws = kwe.matched(text)
    _, base_res = uie.extract(text, task_schema=util.BASE_SCHEMA, threshold=threshold)
    fine_res = FineGrainedInfo(ddp_res[0]).parse() if useFine else CoarseGrainedInfo(ddp_res[0]).parse()

    uie_cat = [list(x.keys()) for x in base_res][0]
    task_schema = util.task_setting(kwe_cat, uie_cat, scheduler=3)
    _, task_res = uie.extract(text, task_schema=task_schema, threshold=threshold)
    relations = process.relationship(base_res, task_res, fine_res, kwe, add_fine=add_fine)
    keywords = process.keywords(base_res, ws)

    if without_non:
        relations = dict([k, v] for k, v in relations.items() if k != 'NON')


    return relations, keywords



if __name__ == '__main__':
    text = '我计划装修房子，总面积108m², 套内88平米，预算40w+, 想装修成现代简约风格，客厅放L形沙发和玻璃茶几，方便会客，餐厅配置红木餐桌椅和水晶吊灯 。'
    text = '三室一厅的毛坯房，108平米，装修预算40万，希望主卧独卫，客厅放L形沙发，厨房采用干湿分离布局，餐厅为红木餐桌。'
    text = '卫生间满足我们的需求做了三分离设计，在早上的使用高峰期或者多人使用起来更加方便。'
    text = '我家客厅要装修成现代简约风格的，88平米， 预算大概是4w+人民币。朋友家的卧室是北欧风格的，也差不多花了4w， 17平米。'

    relations, keywords = extractor(text, add_fine=True)
    print(relations)

