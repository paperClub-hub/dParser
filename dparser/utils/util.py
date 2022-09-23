#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-22 14:52
# @Author   : NING MEI
# @Desc     :

from typing import List
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict





# 初始schema
BASE_SCHEMA = ['户型布局', '场所类', '局部', '风格类', '抽象风格', '家具物体', '组分', '色彩', '术语', '外形', '品牌']

# schema配对规则：
Rules = [['户型类','风格类'], ['户型类','抽象风格'], ['户型类','场所类'], ['户型类','面积'],['户型类', '费用'], ['户型类','长'],['户型类','宽'], ['户型类','高'], \
          ['户型类','色彩'], ['户型类','外形'], ['户型类', '属性'],['户型类', '局部'],['户型类','空间'],['户型类','属性'], # 户型类
          ['场所类','风格类'], ['场所类','抽象风格'], ['场所类','面积'], ['场所类','费用'], ['场所类','长'], ['场所类','宽'], ['场所类','高'], ['场所类','色彩'],\
          ['场所类','外形'], ['场所类','属性'], ['场所类','装饰'], ['场所类','方位'], ['场所类', '局部'], ['场所类','空间'], ['场所类','属性'], # 场所类
          ['物体家具','风格类'], ['物体家具','抽象风格'], ['物体家具','费用'], ['物体家具','长'], ['物体家具','宽'], ['物体家具','高'], ['物体家具','深'], ['物体家具','色彩'],\
          ['物体家具','外形'], ['物体家具','组分'], ['物体家具','品牌'], ['物体家具','纹理'], ['物体家具','观点倾向'], ['物体家具','装饰'], ['物体家具','属性'], # 物体类
          ['术语', '属性'], ['术语', '品牌'],
        ]



def task_setting(kwe_cat:List, uie_cat:List, scheduler:int=1):
    """ 信息抽提schema配置: 根据词类型进行组合和筛选, 构建多任务 uie-sechma
    """

    def _diff(st: List, types: List, inter=False):
        """ inter=True 获取 types列表中， 存在st的元素; inter=False, 获取 types列表中， 不在st的元素
         """
        if inter:
            return list(set(types).intersection(set(st)))
        else:
            return list(set(types).difference(set(st)))


    def _legalizer(rule):
        """ 规则筛选 """
        a, b, cdt1, cdt2 = rule[0], rule[1], rule[2], rule[3]
        if (a == cdt1 and b == cdt2) or (b == cdt1 and a == cdt2):
            return True
        else:
            return False


    def _scheduler3(all_cats):
        task_schema = []
        if all(x in all_cats for x in ['户型布局', '场所类', '家具物体', '风格类']):
            others = _diff(['户型布局', '场所类', '家具物体', '风格类'], all_cats)
            others = others if others else ['属性']
            task_schema = [{'户型布局':'场所类'}, {'场所类': ['风格', '家具物体'] + others}, {'场所类': ['物体', '风格'] + others},
                           {'家具物体': ['风格']+others}, {"户型布局": others}]

        elif all(x in all_cats for x in ['场所类', '家具物体', '风格类']):
            others = _diff(['场所类', '家具物体', '风格类'], all_cats)
            others = others if others else ['属性']
            task_schema = [{'场所类':['风格', '物体']+others}, {'场所类': ['家具物体','风格']+others}, {'家具物体':others}]

        elif all(x in all_cats for x in ['局部', '家具物体', '风格类']):
            others = _diff(['局部', '家具物体', '风格类'], all_cats)
            others = others if others else ['属性']
            task_schema = [{'局部': ['风格', '物体'] + others}, {'局部': ['家具物体', '风格'] + others}, {'家具物体': others}]

        elif all(x in all_cats for x in ['家具物体', '风格类']):
            others = _diff(['家具物体', '风格类'], all_cats)
            others = others if others else ['属性']
            task_schema = [{'家具物体': ['风格'] + others}, {'家具物体': others}]

        else:
            for i, c1 in enumerate(all_cats):
                for c2 in all_cats[i + 1:]:
                    if c1 == '风格类': continue
                    if {c1: c2} not in task_schema: task_schema.append({c1: c2})

        return task_schema


    def _scheduler2(all_cats):
        task_schema = []
        for i, c1 in enumerate(all_cats):
            for c2 in all_cats[i + 1:]:
                if c1 == '风格类': continue
                items = [[c1, c2] + r for r in Rules]
                for item in items:
                    rls = _legalizer(item)
                    if rls:
                        if {c1: c2} not in task_schema: task_schema.append({c1: c2})

        return task_schema


    def _scheduler1(all_cats):
        task_schema = []
        for i, c1 in enumerate(all_cats):
            for c2 in all_cats[i + 1:]:
                if c1 == '风格类': continue
                if {c1: c2} not in task_schema: task_schema.append({c1: c2})

        return task_schema


    def _category(kwe_cat: List, uie_cat:List) -> List:
        """ 生成组词类别列表 """
        all_cats = set()
        all_cats.update(kwe_cat)
        all_cats.update(uie_cat)
        all_cats = list(all_cats)

        if (any(x in all_cats for x in ['费用', '面积', '长', '宽', '高', '深'])) and '数量' in all_cats:
            all_cats = list(filter(lambda x: x != '数量', all_cats))

        Refence = ['户型布局', '场所类', '局部', '家具物体', '风格类', '抽象风格', '组分', '色彩', '术语', '外形', '品牌',
                   '数量', '长', '宽', '高', '深', '品牌', '纹理']
        all_cats = [x for x in Refence if x in all_cats]

        return all_cats

    # scheduler配置
    all_cats = _category(kwe_cat, uie_cat)
    if scheduler == 1:
        task_schema = _scheduler1(all_cats)
    elif scheduler == 2:
        task_schema = _scheduler2(all_cats)
    elif scheduler == 3:
        task_schema = _scheduler3(all_cats)
    else:
        print(f"scheduler should be in [1,2,3], you {scheduler} is invalid, and will be set to BASE_SCHEMA. ")
        task_schema = BASE_SCHEMA

    return task_schema




def network(res, addlabel=True, add_relation_node=True):
    """ 显示图网络 """

    G = nx.DiGraph()
    res = res[0]
    if not res:
        return

    for k, vs in res.items():
        G.add_node(k)
        if addlabel:
            G.add_edges_from([(k, d.get('text'), {"name": '包括', "weight": d.get('probability')}) for d in vs])
        else:
            G.add_edges_from([(k, d.get('text')) for d in vs])

        for d in vs:
            dk = d.get('text')
            relations = d.get('relations')
            if relations:
                for rk, rvs in relations.items():
                    if add_relation_node:  ## 添加关系节点
                        G.add_node(rk)
                        G.add_edge(dk, rk)

                        if addlabel:
                            edges = [(rk, rd.get('text'), {'name': rk, 'weight': rd.get('probability')}) for rd in rvs]
                        else:
                            edges = [(rk, rd.get('text')) for rd in rvs]
                        G.add_edges_from(edges)

                    else:
                        if addlabel:
                            edges = [(dk, rd.get('text'), {'name': rk, 'weight': rd.get('probability')}) for rd in rvs]
                        else:
                            edges = [(dk, rd.get('text')) for rd in rvs]
                        G.add_edges_from(edges)

    degrees = G.degree()
    elarger = [x[0] for x in degrees if x[1] > 1]
    enames = nx.get_edge_attributes(G, 'name')
    pos = nx.spring_layout(G)  # 默认布局：nx.spring_layout(G)， nx.kamada_kawai_layout(G)
    nx.draw(G, pos, node_color="b", node_size=1500, alpha=0.3, with_labels=True)
    options = {"node_color": "r", 'alpha': 0.3, 'node_size': 2000}
    if elarger:
        nx.draw_networkx_nodes(G, pos, nodelist=elarger, **options)
    if enames:
        nx.draw_networkx_edge_labels(G, pos, edge_labels=enames, font_family='SimHei')
    nx.draw_networkx_labels(G, pos, font_family='SimHei')

    plt.show()



if __name__ == '__main__':
    print()

    res = [{'场所类': [{'text': '卧室', 'start': 38, 'end': 40, 'probability': 0.9998853236667564, 'relations': {'风格': [{'text': '北欧风格', 'start': 41, 'end': 45, 'probability': 0.9999401577978233}], '面积': [{'text': '17平米', 'start': 57, 'end': 61, 'probability': 0.9999713303643176}], '大小': [{'text': '17平米', 'start': 57, 'end': 61, 'probability': 0.9999157803836596}]}}, {'text': '客厅', 'start': 2, 'end': 4, 'probability': 0.9999797345232224, 'relations': {'风格': [{'text': '现代简约风格', 'start': 8, 'end': 14, 'probability': 0.999971926399553}], '面积': [{'text': '88平米', 'start': 16, 'end': 20, 'probability': 0.99998301272813}], '大小': [{'text': '88平米', 'start': 16, 'end': 20, 'probability': 0.9999834895663042}]}}]}]
    res = [{'面积': [{'text': '108m²', 'probability': 0.9998678002081824}], '外形': [{'text': 'L形', 'probability': 0.9999839068034646, 'relations': {'场所类': [{'text': '客厅', 'probability': 0.9999819994767165}]}}], '费用': [{'text': '40w+', 'probability': 0.9999777079867336}], '场所类': [{'text': '客厅', 'probability': 0.9999849200795907, 'relations': {'风格类': [{'text': '现代简约风格', 'probability': 0.999899626873411}]}}, {'text': '餐厅', 'probability': 0.9999837279972041, 'relations': {'风格类': [{'text': '现代简约风格', 'probability': 0.9998426458833158}]}}]}]

    # network(res, addlabel=True, add_relation_node=False)
