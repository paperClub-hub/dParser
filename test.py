

import os
import jieba
from pathlib import Path
from ordered_set import OrderedSet
from collections import defaultdict
from copy import deepcopy



res = [{'场所类': [{'text': '客厅',
    'start': 3,
    'end': 5,
    'probability': 0.9999873042509506}],
  '数量': [{'text': '105平方',
    'start': 24,
    'end': 29,
    'probability': 0.9973127905104349},
   {'text': 'w+', 'start': 1, 'end': 3, 'probability': 0.9832261021452595},
   {'text': '内85',
    'start': 31,
    'end': 34,
    'probability': 0.9500173885872627}]}]


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


def _format(target_res):
    res = deepcopy(target_res)
    res = res[0]
    if res:
        for k, kv in res.items():
            for kk in kv:
                if isinstance(kk, dict):
                    del kk['start'], kk['end']
                if 'relations' in kk:
                    relastions = kk.get('relations')
                    # print(relastions)
                    for rk, rv in relastions.items():
                        for rkk  in rv:
                            del rkk['start'], rkk['end']

    return [res]


from collections import defaultdict
def _format2(target_res, threshold:float = None):
    out = defaultdict(list)
    res = target_res[0]

    if res:
        for k, kv in res.items():
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
                        out[k].append({"text": item['text'],
                                       "probability": item['probability'],
                                       'relations': dict(item_relations_dict)
                                       })
                    else:
                        out[k].append({"text": item['text'],
                                       "probability": item['probability']
                                       })

    return [dict(out)]

res0 = _format(res)
res2 = _format2(res, threshold=0.9999)

print(res)
print(res0)
print(res2)