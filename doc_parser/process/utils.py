#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-10-24 9:05
# @Author   : NING MEI
# @Desc     :



import os
import re
import json
from collections import defaultdict



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
        return [target_res]


def docment_spliter(doc_text: str, max_lenght: int = 512):
    """ 文本分割 """
    all_texts = []
    _texts = []
    doc_texts = doc_text.split("。")

    for i, text in enumerate(doc_texts):
        if len("".join(_texts)) <= max_lenght:
            _texts.append(text)
        else:
            all_texts.append(_texts)
            _texts = []
            _texts.append(text)

        if i == len(doc_texts) - 1:
            all_texts.append(_texts)

    all_texts = [x for x in all_texts if "".join(x)]
    return all_texts


def docment_cutter(para):
    """ 按照句子"""
    para = re.sub('([。！？\?])([^”’])', r"\1\n\2", para)
    para = re.sub('([\.;])(\s)', r"\1\n\2", para)  # 英文断句
    para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
    para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
    para = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
    para = para.rstrip()

    return list(filter(bool, para.split('\n')))


def paragraph_spliter(paragraph: str, max_len=512):
    """ 段落分割 """
    if len(paragraph) > max_len:
        ptexts = []
        all_texts = []
        sentences = docment_cutter(paragraph)
        for i, sent in enumerate(sentences):
            if len(sent) + len("".join(ptexts)) <= max_len:
                ptexts.append(sent)
                if i == len(sentences) - 1:  # 最后一句
                    all_texts.append(ptexts)

            else:
                all_texts.append(ptexts)
                ptexts = []
                ptexts.append(sent)
        del ptexts
        return ["".join(sents) for sents in all_texts]

    else:
        return [paragraph]


if __name__ == '__main__':

    print()

    zm_data = json.load(open("../zhimo_all.json", 'r'))
    print(zm_data)
