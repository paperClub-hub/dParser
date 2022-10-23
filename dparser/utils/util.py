#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-10-20 14:48
# @Author   : NING MEI
# @Desc     :



import os
import json
from collections import defaultdict



def load_json(json_file: str):

    return json.load(open(json_file, 'r', encoding='utf-8'))

def load_stopwords(file:str):

    return [line.strip() for line in open(file, 'r', encoding='utf-8').readlines() if line.strip()]


def create_jieba_dict(txt_file: str, jieba_path:str):
    data = []
    with open(txt_file, 'r') as f:
        for line in f.readlines():
            line = line.strip().split("/")[0]
            data.append(line)
    print('\n'.join(data), file=open(jieba_path, 'w', encoding='utf-8'))


def uie_postprocess(target_res, threshold: float = None, reform: bool = True):
    """ uie 抽提结果过滤处理 """

    target_res = target_res[0]
    if target_res:
        if reform:  # 用于生成实体及关系三元组
            ners = defaultdict(list)  # 实体
            relations = []  # 关系三元组
            for k, kv in target_res.items():
                items = list(filter(lambda x: x.get('probability') > threshold, kv)) if threshold else kv
                ners[k].extend([item.get('text') for item in items])
                rel_items = list(filter(lambda x: 'relations' in x, items))
                if rel_items:
                    for item in rel_items:
                        node = item.get("text")
                        edges = item.get("relations")
                        for attri, _edge_values in edges.items():
                            edge_values = list(filter(lambda ev: ev.get("probability") > threshold,
                                                      _edge_values)) if threshold else _edge_values
                            if edge_values:
                                edge_values = [ev.get('text') for ev in edge_values]
                                if [node, attri, edge_values] not in relations:
                                    relations.append([node, attri, edge_values])


            result = [{"ner": dict(ners), "triplets": relations}]

            return result

        else:  # 保存格式不变，probability过滤
            result = defaultdict(list)
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
                                        item_relations_dict[rk].append(
                                            {'text': relation['text'], 'probability': relation['probability']})
                        if item_relations_dict:
                            added_item = {"text": item['text'],
                                          "probability": item['probability'],
                                          'relations': dict(item_relations_dict)}
                            if added_item not in result[k]: result[k].append(added_item)

                        else:
                            added_item = {"text": item['text'], "probability": item['probability']}
                            if added_item not in result[k]: result[k].append(added_item)

            return [dict(result)]

    else:
        return target_res


_root_path = os.path.dirname(os.path.abspath(__file__))
template_file = os.path.normpath(os.path.join(_root_path, "../model_files/templates.json"))
custom_dict_file = os.path.normpath(os.path.join(_root_path, "../model_files/custom_dict.txt"))
jieba_dict_file = os.path.normpath(os.path.join(_root_path, "../model_files/jieba_dict.txt"))
stopwords_file = os.path.normpath(os.path.join(_root_path, "../model_files/stopwords.txt"))

create_jieba_dict(custom_dict_file, jieba_dict_file)
templates = load_json(template_file)
stopwords = load_stopwords(stopwords_file)


if __name__ == '__main__':

    print()
