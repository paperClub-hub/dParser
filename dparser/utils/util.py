#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-22 14:52
# @Author   : NING MEI
# @Desc     :

from collections import defaultdict


def process_uie(target_res, threshold: float = None):
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
                            relations = list(
                                filter(lambda r: r.get('probability') > threshold, rv)) if threshold else rv
                            if relations:
                                for relation in relations:
                                    item_relations_dict[rk].append({'text': relation['text'],
                                                                    'probability': relation['probability']})
                    if item_relations_dict:
                        result[k].append({"text": item['text'],
                                       "probability": item['probability'],
                                       'relations': dict(item_relations_dict)
                                       })
                    else:
                        result[k].append({"text": item['text'],
                                       "probability": item['probability']
                                       })

    return [dict(result)]




if __name__ == '__main__':
    print()

    res = [{'场所类': [{'text': '卧室',
                     'start': 38,
                     'end': 40,
                     'probability': 0.9998853236667564,
                     'relations': {'风格类': [{'text': '北欧风格',
                                            'start': 41,
                                            'end': 45,
                                            'probability': 0.9999649527746719}]}},
                    {'text': '客厅',
                     'start': 2,
                     'end': 4,
                     'probability': 0.9999797345232224,
                     'relations': {'风格类': [{'text': '现代简约风格',
                                            'start': 8,
                                            'end': 14,
                                            'probability': 0.999975383432556}]}}]}]



    out_res = process_uie(res)
    print(out_res)