#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-20 16:50
# @Author   : NING MEI
# @Desc     :

"""
关键词提取及关键词词类计算
"""


import os
import jieba
from ordered_set import OrderedSet
from collections import defaultdict

import warnings
warnings.filterwarnings('ignore')



class wordExtract():

    """ 关键词提取及词类型获取"""

    def __init__(self):
        self.dict_path = self._get_abs_path("model_files/custom_dict2.txt")
        self.jieba_path = self._get_abs_path("model_files/jieba_dict.txt")
        self.DICT = self._load_custom_dict()
        if self.DICT: self.save_dict()
        if os.path.exists(self.jieba_path): jieba.load_userdict(str(self.jieba_path))
        self.stopwords = self._load_stopwords()

    def _get_abs_path(self, path):
        return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), path))

    def _load_custom_dict(self):
        """ 加载 lac自定义字典 """
        # print('加载自定义词典... ')
        label_dict = defaultdict(list)
        with open(self.dict_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip()
                k, v = line.split('/')[-1].strip(), line.split('/')[0].strip()
                label_dict[k].append(v)
        label_dict = dict([k, sorted(v)] for k, v in label_dict.items())
        return label_dict


    def _load_stopwords(self):
        try:
            # print("加载停止词... ")
            stopwords = set()
            dir = self._get_abs_path("model_files/stopwords")
            for sp in ['baidu_stopwords.txt', 'cn_stopwords.txt', \
                       'hit_stopwords.txt', 'scu_stopwords.txt']:
                with open(os.path.join(dir, sp), 'r') as f:
                    stopwords.update([s.strip() for s in f.readlines() if s.strip()])
            return list(stopwords)
        except Exception:
            return []


    def save_dict(self):
        """ 生成自定义jieba字典 """
        label_set = OrderedSet()
        all_labels = self.DICT.values()
        for labels in all_labels:
            for label in labels:
                label_set.add(label)
        print('\n'.join(label_set), file=open(self.jieba_path, 'w', encoding='utf-8'))



    def matched(self, text):
        """ 行业词提取 及词类型匹配 """

        def _match(text):
            """ 自定义特殊分类词: 根据词出进行匹配 """
            cost = "费用|价格|花费|人民币|RMB|万|W|元|块|花了|"
            area = "面积|平米|平|m2|m²|cm|寸"
            sizes = "长|宽|高|深|"  # 一对一字典

            cats = set()
            text = text.upper()
            for string in [cost, area, sizes]:
                one2one = True if string[0] == '长' else False
                string = string.strip().strip("|").upper().split("|")
                string_dict = dict([x, x] for x in string) if one2one else {string[0]: string}
                out = list( filter(lambda x: x in text, list(string_dict.values()) if one2one \
                            else list(string_dict.values())[0]))

                if out:
                    if one2one:
                        cats.update([k for k, v in string_dict.items() if v in out])
                    else:
                        cats.update(string_dict.keys())

            return list(cats)

        CATS_DICT = {  # 自定义字典转化 ie 标签名
            "STYLE": "风格类", "SPACE": "场所类", "LOSPACE": "局部", "OBJECT": "家具物体",
            "SHAPE": "外形", "COLOR": "色彩", "MATERIAL": "组分", "PATTERN": "纹理",
            "FEATURE": "属性", "BRAND": "品牌", "PROPTY": "户型布局",
        }

        tokens = jieba.lcut(text)
        tokens = list(filter(lambda w: w not in self.stopwords, tokens))
        matches = set([(t, c) for t in tokens for c, ns in self.DICT.items() if t in ns])
        words = [x[0] for x in matches] if matches else []
        res = [CATS_DICT.get(x[1], None) for x in matches if CATS_DICT.get(x[1], None)] if matches else []
        res_defined = _match(text)
        res.extend(res_defined)

        return list(set(res)), list(set(words))




if __name__ == '__main__':
    text = '三室一厅的毛坯房，108平米，装修预算40万，希望主卧独卫，客厅有L形沙发，厨房干湿分离，餐厅为红木餐桌。'
    we = wordExtract()
    types, ws = we.matched(text)
    print(types)

