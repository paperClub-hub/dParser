#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-23 11:30
# @Author   : NING MEI
# @Desc     :


'''
结果处理
'''

from collections import defaultdict
from typing import List





def gen_relation_dict(uie_res: List, threshold:float = None, is_cat_dict=True):
    """ 构建uie抽提结果关系字典"""
    res_dict = {}
    ann_res = defaultdict(list)
    res = uie_res[0]
    if len(res) == 0:
        return res_dict

    for k, kv in res.items():
        items = list(filter(lambda x: x.get('probability') > threshold, kv)) if threshold else kv
        if is_cat_dict:
            items = [d.get('text') for d in items]
            if items:
                for w in items:
                    res_dict[w] = k
        else:
            _items = list(filter(lambda d: "relations" in d, items))
            items = list(filter(lambda x: x.get('probability') > threshold, _items)) if threshold else _items
            if items:
                for item in items:
                    start_node = item.get("text")
                    item_relations_dict = item.get('relations')
                    for rel, end_nodes in item_relations_dict.items():
                        for end_item in end_nodes:
                            ann_res[rel].append([start_node, end_item.get('text')])


    return res_dict if is_cat_dict else ann_res




def relationship(base_res, task_res, fine_res, kwe, add_fine=True):
    """ 关系处理 """

    def _annotate(base_res, fine_res, kwe):
        """ 组间关系 """

        # 剔除词列表
        rmws = ['的', '是', '成', '家', '放', '为', '花', '买', '采用', '使用'] + kwe.stopwords
        result = defaultdict(list)
        if len(fine_res) == 0:
            return []

        fine_res = [list(filter(bool, x[0])) for x in fine_res]
        base_dict = gen_relation_dict(base_res, is_cat_dict=True)

        ### 构建关系字典
        for _ws in fine_res:
            ws = list(filter(lambda x: x not in rmws, _ws))
            if not ws: continue
            for w in ws:
                _k, _c = kwe.matched(w)
                if _k:
                    base_dict.update({ w: _k[0] })

            rel = 'NON'
            if len(ws) == 1:
                if ws[0] in base_dict:
                    rel = base_dict.get(ws[0])

            else:
                if ws[0] in base_dict and ws[1] in base_dict:
                    rel = base_dict.get(ws[1])

                elif ws[0] in base_dict:
                    rel = base_dict.get(ws[0])
                    ws = ws[::-1]

                elif ws[1] in base_dict:
                    rel = base_dict.get(ws[1])

                else:
                    rel = None
                    k0, c0 = kwe.matched(ws[0])
                    k1, c1 = kwe.matched(ws[1])
                    if k0 and k1:
                        rel = k1[0]
                    elif k0:
                        rel = k0[0]
                        ws = ws[::-1]
                    elif k1:
                        rel = k1[0]

            if ws not in result[rel]:
                result[rel].append(ws)

        return result


    def _map(dic1, dict2):
        """ 关联见过处理 """
        for k, vs in dict2.items():
            if k in dic1:
                dic1[k].append(vs)
            else:
                dic1.update({k: vs})
        del dict2
        return dic1


    dict1 = _annotate(base_res, fine_res, kwe) # gold
    dict2 = gen_relation_dict(task_res, is_cat_dict=False)
    data = _map(dict1, dict2) if add_fine else dict2

    return dict(data)




def keywords(base_res, ws):
    """ 关键词 """

    words = list(gen_relation_dict(base_res, is_cat_dict=True).keys())
    words.extend(ws)

    return list(set(words))



if __name__ == '__main__':
    print()

    ws = ['客厅', '餐厅', '厨房', '布局', 'L形', '红木餐桌', '主卧', '沙发', '干湿分离']
    res_info = [(('三室一厅', '毛坯房'), 'ATT_N'), (('毛坯房', '108平米', None), 'SVO'), ((None, '预算', '40万'), 'SVO'),
                (('装修', '预算'), 'ATT_N'), ((None, '希望', '独卫'), 'SVO'), (('主卧', '独卫', None), 'SVO'),
                (('客厅', '放', '沙发'), 'SVO'), (('L形', '沙发'), 'ATT_N'), (('厨房', '采用', '布局'), 'SVO'),
                (('干湿分离', '布局'), 'ATT_N'), (('餐厅', '为', '红木餐桌'), 'SVO')]
    base_res = [{'户型布局': [{'text': '干湿分离', 'probability': 0.9999322902691254},
                          {'text': '三室一厅', 'probability': 0.9999591115139772}],
                 '场所类': [{'text': '客厅', 'probability': 0.9993501697305618},
                         {'text': '厨房', 'probability': 0.9995061172980115},
                         {'text': '餐厅', 'probability': 0.9974604306722412}],
                 '家具物体': [{'text': '沙发', 'probability': 0.9999782444091068},
                          {'text': '餐桌', 'probability': 0.9999611977307694}],
                 '外形': [{'text': 'L形', 'probability': 0.9999890327752574}]}]


    task_res = [{'户型布局': [{'text': '干湿分离', 'probability': 0.9999322902691254,
                           'relations': {'空间': [{'text': '厨房', 'probability': 0.999977648364947}],
                                         '外形': [{'text': 'L形', 'probability': 0.9960577641299722}]}},
                          {'text': '三室一厅', 'probability': 0.9999591115139772,
                           'relations': {'面积': [{'text': '108平米', 'probability': 0.9999833703593666}],
                                         '费用': [{'text': '40万', 'probability': 0.9975943592595655}]}}],
                '家具物体': [
                    {'text': '沙发', 'probability': 0.9999782444091068,
                     'relations': {'外形': [{'text': 'L形', 'probability': 0.9999889731708578}]}},
                    {'text': '餐桌', 'probability': 0.9999611977307694}]}
                ]
    # from key_pharse.parser.dparser.extract.kextract import wordExtract
    # kwe = wordExtract()
    # result = relationship(base_res, task_res, res_info, kwe)
    # print(result)

    # print(keywords(base_res, ws))
