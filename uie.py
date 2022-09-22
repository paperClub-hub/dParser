#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-20 18:49
# @Author   : NING MEI
# @Desc     :



from typing import List
from paddlenlp import Taskflow
import networkx as nx
from dparser.utils import util

import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

import  warnings
warnings.filterwarnings('ignore')



class UIE():

    def __init__(self):
        checkpoint = "./best_f1_0.6854"
        base_schema = ['户型布局', '场所类', '风格类', '家具物体', '组分', '色彩', '抽象风格', '术语', '局部', '外形']
        # base_schema = ['户型', '场所', '物体', '材质', '费用', '面积', '形状', '纹理', '色彩', '属性']
        self.based_schema = base_schema
        self.model = Taskflow(task='information_extraction', task_path=checkpoint, schema=base_schema, position_prob=0.95)


    def extract(self, text, task_schema, with_base=True):
        """ 信息抽提 """

        base_res = self.model(text) if with_base else None
        self.model.set_schema(task_schema)
        task_res = self.model(text)

        return base_res, task_res





if __name__ == '__main__':
    text = '我家客厅要装修成现代简约风格的，88平米， 预算大概是4w+人民币。朋友家的卧室是北欧风格的，也差不多花了4w， 17平米。'
    task_schema = {'家具物体': ['物体', '材质', '颜色', '纹理', '形状', '品牌名', '费用']}
    uie = UIE()
    base_res, task_res = uie.extract(text, task_schema, with_base=True)
    base_res2 = util.process_uie(base_res)
    task_res2 = util.process_uie(task_res)

    # print(f"base_res: {base_res}")
    # print(f"task_res: {task_res}")
    print(f"base_res2: {base_res2}")
    # print(f"task_res2: {task_res2}")
