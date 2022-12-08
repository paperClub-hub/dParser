#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-13 11:04
# @Author   : NING MEI
# @Desc     :


import os
import json
import pandas as pd
from math import ceil
from typing import List
import networkx as nx
from tqdm.auto import tqdm
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class load_doccano_label():

    """ 加载 doccano标注json文件 """
    # TODO: doccano有bug, 标注结果有错乱现象，如品牌（'品牌': ['了\n', '\n用',]）, 需要排查原因。


    def __init__(self, json_path, save_dir="output"):
        Jdat = self.load_json(json_path)
        self.jdat = Jdat.copy()
        save_dir = os.path.join(os.getcwd(), save_dir)
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        self.out_dir = save_dir
        self.labelCounts, self.lableItems, self.lableInfos = self._to_label_dict(Jdat)

    def load_json(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            jdat = [json.loads(line.strip()) for line in f.readlines()]
        return jdat

    def _to_label_dict(self, jdat):
        """ 获得标注标签字典 """
        from collections import defaultdict
        labels = defaultdict(list)
        if jdat:
            for ele in jdat:
                text = ele['text']
                entities = ele['entities']
                if entities:
                    for ent in entities:
                        label_type = ent['label']
                        start_offset, end_offset = ent['start_offset'], ent['end_offset']
                        label_name = text[start_offset:end_offset]
                        labels[label_type].append(label_name)

            label_counts = dict([k, len(v)] for k, v in labels.items())
            label_items = dict([k, list(set(v))] for k, v in labels.items())
            return label_counts, label_items, labels
        else:
            return {}, {}, {}


    def net_visualization(self):

        """ 实体网络绘图 """
        def ner_net(k:str='风格类', v:List=['北美', '简约'], savepng="./demo1.png"):

            g = nx.DiGraph()
            g.add_node(k)
            edges = [(k,x) for x in v]
            g.add_edges_from(edges, name='包含')

            pos = nx.spring_layout(g)
            elabels = nx.get_edge_attributes(g, 'name')
            nx.draw(g, pos, node_color='y', edge_color='gray',node_size=800, alpha=0.5, style='dashdot')
            nx.draw_networkx_labels(g, pos, font_color='blue')
            nx.draw_networkx_edge_labels(g, pos, edge_labels=elabels)

            print(elabels, file=open(str(os.path.splitext(savepng)[0]+"-ner.txt"), 'w'))
            plt.savefig(savepng, format="PNG")
            plt.close()
            del g

        def relation_net(relations: List = [('客厅', '风格', '法式设计'), ('客厅', '风格', '法式')], savepng="./demo2.png"):
            """ 关系绘图 """
            g = nx.DiGraph()
            for rel in relations:
                g.add_edge(rel[0], rel[-1], name=rel[1])

            pos = nx.spring_layout(g)
            elabels = nx.get_edge_attributes(g, 'name')
            nx.draw(g, pos, node_color='blue', edge_color='green', node_size=500, alpha=0.5, style='dashdot')
            nx.draw_networkx_labels(g, pos, font_color='red')
            nx.draw_networkx_edge_labels(g, pos, edge_labels=elabels)

            print(elabels, file=open(str(os.path.splitext(savepng)[0] + "-rel.txt"), 'w'))
            plt.savefig(savepng, format="PNG")
            plt.close()
            del g

        def _split(big_st, num):
            """ 把大列表拆分成 num元素的小列表 """
            return list(map(lambda x: big_st[x * num : x * num + num], list(range(0, ceil(len(big_st) / num)))))

        def _visualization():

            # 实体绘图
            for i, (k,v) in tqdm(enumerate(self.lableItems.items())):
                imgpath = os.path.join(self.out_dir, f"{i}_ner.png")
                ner_net(k,v ,imgpath)

            # 关系图
            labeled_relations = _split(self.event_tuples()[-1], 20)
            for i, relations in tqdm(enumerate(labeled_relations)):
                imgpath = os.path.join(self.out_dir, f"{i}_rel.png")
                relation_net(relations, imgpath)

        print("绘图...")
        _visualization()



    def event_tuples(self):
        """ 获取标注标签 """

        Results = []
        for i, ele in enumerate(self.jdat):
            text_id = ele['id']
            text = ele['text']
            entities = ele['entities']
            relations = ele['relations']

            for ent in entities:
                word = text[ent['start_offset']: ent['end_offset']]
                ent['word'] = word

            if relations:
                for rel in relations:
                    from_id = rel['from_id']
                    to_id = rel['to_id']
                    label = rel['type']
                    from_word = [ent['word'] for ent in entities if ent['id'] == from_id][0]
                    to_word = [ent['word'] for ent in entities if ent['id'] == to_id][0]
                    rel['tuple'] = (from_word, label, to_word)

            ent_dat = [(ent['word'], ent['label']) for ent in entities]
            rel_dat = [rel['tuple'] for rel in relations if relations]
            Results.append({"id": text_id, "entities": ent_dat, "relations": rel_dat})

        # print(Results)
        all_entities, all_relations = [], []
        for d in Results:
            if d.get('entities'):
                all_entities.extend(d.get('entities'))
            if d.get("relations"):
                all_relations.extend(d.get('relations'))

        # print(all_entities)


        return all_entities, all_relations




if __name__ == '__main__':

    json_path = './data/json/demo.jsonl'
    LOAD = load_doccano_label(json_path)
    labelCounts = LOAD.labelCounts
    lableItems = LOAD.lableItems
    lableInfos = LOAD.lableInfos
    entities, relations = LOAD.event_tuples()
    # LOAD.net_visualization()
    print(lableItems)
    print(relations)

