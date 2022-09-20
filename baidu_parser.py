#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-20 11:57
# @Author   : NING MEI
# @Desc     :


import os
from dparser import DDParser

ddp = DDParser()





if __name__ == '__main__':
    text = '我家客厅要装修成后现代风格的，88平米， 预算大概是4w+人民币。朋友家的卧室是北欧风格的，也差不多花了4w， 17平米。'
    dres = ddp.parse(text)
    print(dres)