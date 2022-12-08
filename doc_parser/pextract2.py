#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-10-24 8:59
# @Author   : paperclub
# @Desc     : paperclub@163.com



#------------------------------------------------------------
#   案例文本项目信息抽提: 使用torch提取 + 规则处理
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

    invalid_tags = {
        "设计主创": ["硬装", "软装", "空间与道具", "半包硬装", "建筑", "结构", "2009-2010年"],
        "项目户型": ['自然', "森林 · 光"],
        "项目风格": ['项目风格'],
        "施工单位": ['图标'],
        "项目地址": ['454m2'],
        "项目名称": ['Area 175.0 m2']
    }

    def number_identify(res: Dict):
        # 数值数据过滤
        valid_key = ["项目面积", "项目造价", "硬装造价", "软装造价", "装修造价", "造价预算", "设计时间"]
        reg = '([\d|一|二|三|四|五|六|七|八|九|十|壹|贰|叁|弎|仨|肆|伍|陆|柒|捌|玖|俩|两|零|百|千|万|亿|兆|拾|佰|仟|萬|億]+)'
        reg += "|(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?Dec(ember)?)"
        reg += "|(zero|one|two|three|four|five|six|seven|eight|nine)"

        patten = re.compile(reg)
        if res:
            for key in valid_key:
                if key in res:
                    vs = res.get(key)
                    if vs and isinstance(vs, list):
                        vs = list(filter(lambda v: patten.search(v), vs))
                        if vs:
                            res.update({key: vs})
                        else:
                            del res[key]

        return res


    def process(res: List[Dict], tags):
        dic = defaultdict(list)
        if res[0]:
            res = res[0]
            for k, vs in res.items():
                v = list(filter(bool, list(
                    filter(lambda i: i not in invalid_tags.get(tags.get(k), []) and i not in template_dict,
                           list(set([x.get("text") for x in vs]))))))
                if v:
                    for i in v:
                        if i not in dic[tags.get(k)]:
                            dic[tags.get(k)].append(i)

        return number_identify(dict(dic))


    if schema is None:
        MODEL.set_schema(base_schema)
        res = MODEL(text)

    elif not is_contains_chinese("".join(schema)) and not is_contains_chinese(text):
        MODEL2.set_schema(schema)
        res = MODEL2(text)
    else:
        MODEL.set_schema(schema)
        res = MODEL(text)

    del text

    return process(res, tags)




def is_contains_chinese(strs):
    """检验是否含有中文字符"""
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


def is_all_english(strs):
    """ 检测是否全是英文字符 """
    reg = '~`!#$%^&*()_+-=|\';":/.,?><~·！@[\\]【\\】–#￥%……&*（）——+-=“：’；、。，？》《{}|\W'
    strs = re.sub(f"[{reg}", "", strs)
    for i in strs:
        if i not in string.ascii_lowercase + string.ascii_uppercase:
            return False
    return True



def pre_extract(texts):

    def match(LINE: str, TAGS: Dict, TEMPLATE_DICT: Dict):
        res = []
        words = list(filter(lambda w: (w in LINE) or (w in LINE.upper()), list(TEMPLATE_DICT.keys())))
        if words:
            for w in words:
                if is_contains_chinese(LINE): # 中文模式
                    # reg = rf"([【]?[\s]?{w}[\s]?[】]?[\s]?"  # 关键字
                    # # reg += r"([:|：|┃|/|／|│|丨|｜|︱])(.*?)" # 识别符 + 随从句子
                    # reg += r"([:|：|┃|/|／|│|丨|｜|︱]([\s\S]*?))"
                    # reg += r"(\。|\.\s|\；|\;|$))"  # 终止符
                    reg = rf"([【]?[\s]?{w}[\s]?[】]?[\s]?([:|：|┃|/|／|│|丨|｜|︱]([\s\S]*?))(\。|\；|\;|$))"
                    reg_match = re.search(reg, LINE, re.IGNORECASE)

                else: # 英文模式
                    reg = rf"([【]?[\s]?{w}[\s]?[】]?[\s]?([:|：|┃|/|／|│|丨|｜|︱]([\s\S]*?))(\。|\.\s|\；|\;|$))"
                    reg_match = re.search(reg, LINE, re.IGNORECASE)
                    if not reg_match: # 检查长度
                        reg_ = rf"([【]?[\s]?{w}[\s]?[】]?[\s]?([\s\S]*?)(\。|\.\s|\；|\;|$))"
                        reg_match_ = re.search(reg_, LINE, re.IGNORECASE)
                        if reg_match_:
                            start_ = reg_match_.start()
                            if len(LINE) - (start_ + len(w) + 1) <= 35:
                                reg_match = reg_match_

                if reg_match:
                    TAGS.update({w: TEMPLATE_DICT[w]})
                    mline = reg_match.group()
                    if mline not in res:
                        reg2 = '[\u4e00-\u9fa5]|[a-zA-Z0-9]'
                        if len(re.findall(reg2, mline)) > 512:
                            mline = re.split('[。|？|.|?]', mline)[0]
                        res.append(mline)
        del LINE
        return res


    candidates = []
    tags = OrderedDict()
    lines = texts.split("\n")
    for line in lines:
        line = line.replace(u"\xa0 \xa0 ", "").replace(u"\xa0", "")
        mlines = match(line, tags, template_dict)
        if mlines:
            for mline in mlines:
                if mline not in candidates:
                    if candidates:
                        is_involved = all([mline not in _x for _x in candidates])
                        if is_involved:
                            candidates.append(mline)
                    else:
                        candidates.append(mline)

    return "\n".join(candidates), dict(tags)



def get_project_templates(templates: Dict):
    template_dict = {}
    project_templates = templates['project_templates']
    for name, words in project_templates.items():
        template_dict[name] = name
        for word in words:
            if word not in template_dict:
                template_dict[word] = name

            if word.upper() not in template_dict:
                template_dict[word.upper()] = name

            if word.lower() not in template_dict:
                template_dict[word.lower()] = name

    return project_templates, template_dict



templates = load_json('./project_templates.json')
base_schema = templates['base_schema']
project_templates, template_dict = get_project_templates(templates)
MODEL = None
if MODEL is None:
    MODEL = UIEPredictor(model='uie_torch/uie-base',
                         task_path='uie_torch/uie_base_pytorch',
                         device='gpu',
                         batch_size=16,
                         use_fp16=True,
                         schema=base_schema)
    MODEL2 = UIEPredictor(model='uie_torch/uie-base',
                         task_path = 'uie_torch/uie_base_en_pytorch',
                         device='gpu',
                         batch_size=16,
                         use_fp16=True,
                         schema=base_schema)


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
                candidate_texts, tags = pre_extract(paragraph)
                if tags:
                    print("tags: ", tags)
                    print("candidate_texts: ", candidate_texts)
                    stime = time.time()
                    print("i= ", i, "url: ", url)
                    res = uie_extract(candidate_texts, tags, list(tags.keys()))
                    if res:
                        print("uie: ", res)
                        print("----------------------------")
                        if res not in data['info']:
                            data['info'].append(res)
                        print("time_cost: ", time.time() - stime)
                    else:
                        NOT_EXT.append(str((str(i), url)))

            if data['info']:
                print(json.dumps(data, ensure_ascii=False, indent=4), file=open(save_file, 'w', encoding='utf-8'))






if __name__ == '__main__':
    # run_task()

    
    texts = """项目坐标｜Address：雅戈尔未来城
    项目类型｜Type：私宅
    项目面积｜Area：140㎡
    设计时间｜Time：2020.08
    拍摄时间｜Time：2022.10
    设计机构｜Design：晓安设计
    施工单位｜Design：安君精造
    软装设计｜Design：蕊芯卡萨
    文案策划｜Editor：修合文化
    视觉表现｜Visual Expression：影之内
    摄影机构｜Visual Expression：AK空间摄影"""

    candidate_texts, tags = pre_extract(texts)
    # print(candidate_texts)
    res = uie_extract(candidate_texts, tags, list(tags.keys()))
    print("res: ", res)

