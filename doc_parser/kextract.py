#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-10-24 9:46
# @Author   : NING MEI
# @Desc     :


#------------------------------------------------------------
#   文本词关键词提取
#------------------------------------------------------------


import sys
from LAC import LAC
import time
import jieba
import os
import json
from glob import glob
import jionlp as jio
import jieba.posseg as pseg
from tqdm.auto import tqdm
from collections import defaultdict
from ordered_set import OrderedSet
from process.vars import *
import asyncio
from threading import Thread



def _time_extract(text:str):
    res = jio.ner.extract_time(text, time_base=time.time(), with_parsing=False)
    # return json.dumps(res, ensure_ascii=False, indent=4, separators=(',', ':'))
    return [x.get("text").strip() for x in res] if res else []


def _money_extract(text:str):
    res = jio.ner.extract_money(text, with_parsing=False)
    return [x.get("text").strip() for x in res] if res else []


def _location_extract(text:str):
    locations = []
    res = jio.recognize_location(text)
    if res:
        if res.get('domestic'):
            for item in res.get('domestic'):
                item = "".join(list(OrderedSet([x for x in item[0].values() if x])))
                locations.append(item)

        if res.get('foreign'):
            for item in res.get('foreign'):
                item = "".join(list(OrderedSet([x for x in item[0].values() if x and x != '中国'])))
                locations.append(item)
        if res.get('others'):
            item = "".join(list(OrderedSet([x for x in res.get('others').keys() if x and x != '中国'])))
            locations.append(item)

    return locations


def _keyphrase_extract(text: str):
    res = jio.keyphrase.extract_keyphrase(text, -1)
    return [x for x in res if len(x) > 1]


def _area_extract(text: str):
    res = [item.group().strip() for item in  INDOOR_AREA_PATTERN.finditer(text)]

    return list(filter(bool, res))


def text2words(text: str):
    """ 词提取 """
    valid_pos = ["户型", "材质", "形状", "颜色", "物体", "品牌", "风格", "布局", "纹理", "空间", "局部空间",
                 "人名", "地名", "作品名", "机构名",
                 ]

    # words = defaultdict(set)
    # jieb_cuts = pseg.cut(text, use_paddle=True)
    # for w, t in jieb_cuts:
    #     if w in wordflagdict:
    #         words[pos_dict[wordflagdict[w]]].add(w)
    #     elif t in pos_dict and pos_dict.get(t) in valid_pos:
    #         words[pos_dict.get(t)].add(w)
    # del jieb_cuts

    words = defaultdict(set)
    ws, tags, weights = lac.run(text)
    for w, t in zip(ws, tags):
        if t in pos_dict and pos_dict.get(t) in valid_pos:
            words[pos_dict.get(t)].add(w)

    words = dict(words)
    if words:
        for k, v in words.items():
            words[k]=list(v)

    del ws, tags, weights

    _res_time = _time_extract(text)
    _res_money = _money_extract(text)
    _res_location = _location_extract(text)
    _res_area = _area_extract(text)

    if _res_time:
        words.update({"时间": _res_time})
    if _res_money:
        words.update({"金额": _res_money})
    if _res_location:
        words.update({"地址": _res_location})
    if _res_area:
        words.update({"面积": _res_area})

    all_ws = set()
    for w, k in words.items():
        all_ws.update(k)
    _res_kp = _keyphrase_extract(text)
    _res_kp = list(filter(lambda w: w not in list(all_ws), _res_kp))
    if _res_kp:
        words.update({"短语": _res_kp})


    return words





pos_dict = {}
if not pos_dict:
    pos_dict = templates.get("pos_dict")

lac = None
if lac is None:
    lac = LAC(mode="rank")
    lac.load_customization(custom_dict_file)


def run_zm_dataset(save_dir):

    async def task_func(doc):
        """ 单片文章处理 """
        url = doc['url']
        doc_id = url.split("/")[-2]
        doc_txt = [d.get('txt') for d in doc.get('medias') if d.get('txt')]
        if doc_txt:
            print("doc_id: ", doc_id)
            texts = "\n".join(doc_txt)
            ner_words = text2words(texts)
            if ner_words:
                print(json.dumps({
                    "url": url,
                    "ner_words": ner_words,
                        }, ensure_ascii=False),
                    file=open(os.path.join(save_dir, f"{doc_id}.json"), 'w'))

    def task_run(zm_data):
        """ 协程处理 """
        tasks = [task_func(doc) for doc in zm_data]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))



    zm_data = json.load(open("./zhimo_all.json", 'r'))
    if not os.path.exists(save_dir): os.makedirs(save_dir)
    done_files = [os.path.splitext(os.path.basename(x))[0] for x in glob(save_dir + "/*.json") if x]
    zm_data = [x for x in zm_data if x['url'].split("/")[-2] not in done_files]

    task_run(zm_data)



if __name__ == '__main__':
    print()
    text = """2014年3月，100万元深圳国际家具展，“德光居  HOME”惊世亮相，一时间引起行业轰动。这个由台湾著名设计师邱德光先生亲自操刀设计的家具品牌一经推出受到家具业普遍关注。笑称是“被逼”出来的  HOME，以其独创的Neo-Art Deco东方美学风格结合时尚观察，打造出中国第一个具备国际视野的精品家具品牌。被誉为新装饰主义neo-art deco东方美学风格的创始人邱德光先生一直致力于中国顶级豪宅设计，参与两岸许多高级室内设计案与建筑公共区域的规划案，在华人经济圈室内设计领域具有绝对的影响力。今天干货君独家年度回顾的正是邱德光设计师事务所2014年年度代表作――盛世滨江四大样板间，这个被他称为“自己最想居住的地方”。而这四大样板间最大的特点就是“德光居  HOME”在这里成了主角。干货君独家奉送，作为新年礼物呈现给大家。【项目一】：上海融创 盛世滨江 2101【设计者】：邱德光【参与者】： 刘琼文、林纯萱【空间性质】：住宅【坐落位置】：上海市黄浦区中山南一路500弄【主要材料】：圣罗兰黑金石材、新法国米黄石材、雅士白石材、仿古明镜、仿古银箔、古铜金箔、黑檀木皮、烤漆板、镀钛不锈钢、烤漆玻璃、特殊壁纸【面 积】： 211O【设计时间】： 2013 年 9月至 2014 年 8 月【施工时间】： 2014 年 7月至 2014 年 9 月"""

    print(text2words(text))

    save_dir = "output/ner_words2"
    run_zm_dataset(save_dir)