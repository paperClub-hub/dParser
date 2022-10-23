#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-22 18:52
# @Author   : NING MEI
# @Desc     :


import os
from typing import List, Dict, Union
from collections import defaultdict
from paddlenlp import Taskflow
from dparser.utils.util import templates
import  warnings
warnings.filterwarnings('ignore')




class UIE():
    """ 信息抽提 """
    def __init__(self):
        # model_root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../model_files"))
        # custom_model_path = os.path.normpath(os.path.join(model_root, "uie_checkpoint/best2_0.719"))
        # self.base_uie_model = Taskflow(task='information_extraction',
        #                             schema=templates["uie_task"],
        #                             precision="fp16",
        #                             use_faster=True
        #                             )
        #
        # self.custom_uie_model = Taskflow(task='information_extraction',
        #                             schema=templates["uie_task"],
        #                             task_path=custom_model_path,
        #                             precision="fp16",
        #                             use_faster=True
        #                             )
        #
        # self.base_wordtag_ie = Taskflow("knowledge_mining", with_ie=True, precision="fp16",  use_faster=True)

        self.base_uie_model = BASE_UIE_MODEL
        self.custom_uie_model = CUSTOM_UIE_MODEL
        self.base_wordtag_ie = BASE_WORDTAG_IE


    def base_extract(self, text: str, schema: Union[List, Dict] = None):
        if schema is None:
            schema = templates['uie_task']
        self.base_uie_model.set_schema(schema)

        return self.base_uie_model(text)


    def cusom_extract(self, text: str, schema: Union[List, Dict] = None):
        if schema is None:
            schema = templates['uie_task']
        self.custom_uie_model.set_schema(schema)

        return self.custom_uie_model(text)


    def wordtag_extract(self, text:str, schema:List=None):

        if schema is None:
            schema = templates["uie_sentence"]
        self.base_wordtag_ie.set_schema(schema)

        res = self.base_wordtag_ie(text)
        return self._wordtag_postprocess(res)


    def _wordtag_postprocess(self, res: Union[List[List]]):

        pos_items = res[0][0].get("items")
        pos_items = list(filter(lambda x: x.get("wordtag_label") in valid_tags, pos_items))
        for item in pos_items:
            del item['offset'], item['length']

        rel_items = res[1]
        wordtag_rel = defaultdict(list)
        for items in rel_items:
            for item in items:

                _item_head = item["HEAD_ROLE"]["item"]
                _item_tails = [x['item'] for x in item["TAIL_ROLE"]]
                _item_trig = ""
                if item.get("TRIG"):
                    _item_trig = [x['item'] for x in item.get("TRIG")]
                relation_name = item['GROUP']
                value = [_item_head, _item_tails, relation_name]

                wordtag_rel[relation_name].append(value)

        return {"pos_items": pos_items, "wordtag_rel": dict(wordtag_rel)}




model_root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../model_files"))
custom_model_path = os.path.normpath(os.path.join(model_root, "uie_checkpoint/best2_0.719"))

BASE_UIE_MODEL = None
if BASE_UIE_MODEL is None:
    BASE_UIE_MODEL  = Taskflow(task='information_extraction',
                                    schema=templates["uie_task"],
                                    precision="fp16",
                                    use_faster=True
                                    )
CUSTOM_UIE_MODEL = None
if CUSTOM_UIE_MODEL is None:
    CUSTOM_UIE_MODEL = Taskflow(task='information_extraction',
                                    schema=templates["uie_task"],
                                    task_path=custom_model_path,
                                    precision="fp16",
                                    use_faster=True
                                    )
BASE_WORDTAG_IE = None
if BASE_WORDTAG_IE is None:
    BASE_WORDTAG_IE = Taskflow("knowledge_mining", with_ie=True, precision="fp16",  use_faster=True)


uie = UIE()
valid_tags = templates['valid_tags']

# if __name__ == '__main__':
#     print()
#     uie = UIE()
#     uie.extract("你好")