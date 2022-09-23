#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-22 18:52
# @Author   : NING MEI
# @Desc     :


import os
from typing import List
from collections import defaultdict
from paddlenlp import Taskflow
from dparser.utils.util import BASE_SCHEMA
import  warnings
warnings.filterwarnings('ignore')




class UIE():
    """ 信息抽提 """
    def __init__(self):
        checkpoint = self._get_abs_path("../model_files/uie_checkpoint/best_f1_0.6854")
        self.based_schema = BASE_SCHEMA
        self.model = Taskflow(task='information_extraction', task_path=checkpoint, schema=self.based_schema, position_prob=0.95)


    def _get_abs_path(self, path):
        return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), path))

    def _process(self, target_res, threshold: float = None):
        """ uie 抽提结果处理 """

        result = defaultdict(list)
        target_res = target_res[0]
        if target_res:
            for k, kv in target_res.items():
                items = list(filter(lambda x: x.get('probability') > threshold, kv)) if threshold else kv
                if items:
                    for item in items:
                        item_relations_dict = defaultdict(list)
                        if "relations" in item:
                            item_relations = item.get('relations')
                            for rk, rv in item_relations.items():
                                relations = list(filter(lambda r: r.get('probability') > threshold, rv)) if threshold else rv
                                if relations:
                                    for relation in relations:
                                        item_relations_dict[rk].append({'text': relation['text'],
                                                                        'probability': relation['probability']})
                        if item_relations_dict:
                            added_item = {"text": item['text'],
                                          "probability": item['probability'],
                                          'relations': dict(item_relations_dict)}
                            if added_item not in result[k]: result[k].append(added_item)

                        else:
                            added_item = {"text": item['text'], "probability": item['probability']}
                            if added_item not in result[k]: result[k].append(added_item)

        return [dict(result)]


    def extract(self, text, task_schema:List=None, threshold:float=0.99):
        """ 信息抽提 """

        if task_schema:
            self.model.set_schema(task_schema)
        else:
            self.model.set_schema(self.based_schema)

        task_res = self.model(text)

        return task_res, self._process(task_res,threshold)



