#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-10-24 8:59
# @Author   : NING MEI
# @Desc     :



#------------------------------------------------------------
#   案例文本项目信息抽提
#------------------------------------------------------------


import re
import os
import json
import time
from typing import List, Dict
from collections import defaultdict, OrderedDict
from paddlenlp import Taskflow




def load_json(file_in):
    return json.load(open(file_in, 'r', encoding='utf-8', errors='ignore'))


def doc2paragraph(doc):
    """ 文章段落拆分  """
    paras = []
    text = []
    for i, content in enumerate(doc['medias']):
        if isinstance(content, dict):
            if "photoFile" in content:
                if text:
                    paras.append("\n".join(text))
                text = []
            else:
                text.append(content.get("txt"))
                if i == len(doc['medias']) - 1:
                    paras.append("\n".join(text))

    return paras



def uie_extract(text:str, tags: Dict, schema: List=None):
    """ UIE 信息抽提 """

    def process(res: List[Dict], tags):
        dic = defaultdict(list)
        if res[0]:
            res = res[0]
            for k, vs in res.items():
                v = [x.get("text") for x in vs]
                dic[tags.get(k)].extend(v)

        return dict(dic)


    if schema is None:
        MODEL.set_schema(base_schema)
    else:
        MODEL.set_schema(schema)

    res = MODEL(text)
    del text

    return process(res, tags)



def pre_extract1(texts):
    """ 方法1： 项目信息预抽提
     """

    paragraphs = texts.split("\n")
    candidate_texts = []
    tags = OrderedDict()
    for line in paragraphs:
        line = line.replace(u"\xa0 \xa0 ", "").replace(u"\xa0", "")
        for tk, tvs in project_templates.items():
            matched_line = ''
            reg = rf"([【]?[\s]?{tk}[\s]?[】]?[\s|:|：|┃|/|／|│|丨|｜|︱|\s](.*))"
            reg_match = re.search(reg, line)

            if reg_match:
                tags[tk] = tk
                matched_line = reg_match.group()
            else:
                for tv in tvs:
                    reg_tv = rf"([【]?[\s]?{tv}[\s]?[】]?[\s|:|：|┃|/|／|│|丨|｜|︱|\s](.*))"
                    reg_match = re.search(reg_tv, line)
                    if reg_match:
                        tags[tv] = tk
                        matched_line = reg_match.group()
                        break

            if matched_line:
                candidate_texts.append(matched_line)

    return "\n".join(candidate_texts), tags




def pre_extract2(texts):
    " 方法2：项目信息预抽提 "

    tags = OrderedDict()
    candidate_texts = []
    project_words = set()
    for k, v in project_templates.items():
        project_words.add(k)
        project_words.update(v)
    project_words = list(project_words)

    spans = sorted(set([texts.find(w) for w in project_words if texts.find(w) !=-1]))
    if spans:
        for i, idx in enumerate(spans[:-1]):
            line = texts[idx: spans[i+1]]
            if i == len(spans[:-1])-1:
                line = texts[spans[i]:]

            if line.strip():
                line = line.replace(u"\xa0 \xa0 ", "").replace(u"\xa0", "").replace("\n", " ")
                for tk, tvs in project_templates.items():
                    matched_line = ""
                    reg = rf"([【]?[\s]?{tk}[\s]?[】]?[\s|:|：|┃|/|／|│|丨|｜|︱|\s](.*))"
                    reg_match = re.search(reg, line)
                    if reg_match:
                        tags[tk] = tk
                        matched_line = reg_match.group()
                    else:
                        for tv in tvs:
                            reg_tv = rf"([【]?[\s]?{tv}[\s]?[】]?[\s|:|：|┃|/|／|│|丨|｜|︱|\s](.*))"
                            reg_match = re.search(reg_tv, line)
                            if reg_match:
                                tags[tv] = tk
                                matched_line = reg_match.group()
                                break

                    if matched_line:
                        candidate_texts.append(matched_line)

    return "\n".join(candidate_texts), tags




templates = load_json('./project_templates.json')
project_templates = templates['project_templates']
base_schema = templates['base_schema']
print(project_templates)
print("base_schema: ", base_schema)


def run_task():

    zm_data = load_json("./zhimo_all.json")
    save_dir = "./out2"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for i, doc in enumerate(zm_data):
        data = {}
        url = doc['url']
        doc_id = url.split("/")[-2]
        data['url'] = url
        data['info'] = []
        save_file = os.path.join(save_dir, f"{doc_id}.json")
        if os.path.exists(save_file):
            print("已处理")
            continue

        paragraph_texts = doc2paragraph(doc)
        if paragraph_texts:
            for paragraph in paragraph_texts:
                candidate_texts, tags = pre_extract2(paragraph)
                # candidate_texts, tags = pre_extract1(paragraph)
                if tags:
                    stime = time.time()
                    res = uie_extract(candidate_texts, tags, list(tags.keys()))
                    # print("tags: ", tags)
                    # print("candidate_texts: ", candidate_texts)
                    # print("res: ", res)
                    # print("****************************")

                    if res:
                        # print("uie: ", res)
                        data['info'].append(res)
                        print("time_cost: ", time.time() - stime)

            if data['info']:
                print(json.dumps(data, ensure_ascii=False, indent=4), file=open(save_file, 'w', encoding='utf-8'))


MODEL = None
if MODEL is None:
    MODEL = Taskflow(task='information_extraction', schema=base_schema)



if __name__ == '__main__':
    run_task()


