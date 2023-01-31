#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import json
import string
# sys.path.append("./uie_torch")
# from uie_predictor import UIEPredictor
from typing import (List, Dict, Tuple)
from key_pharse.doc_extract.process.date_process import time_parser
from key_pharse.doc_extract.process.area_process import area_process
from key_pharse.doc_extract.process.cost_process import currency_process
from key_pharse.doc_extract.process.location_process import location
from collections import defaultdict, OrderedDict

from paddlenlp import Taskflow
from os.path import abspath, dirname, join
from fastapi import FastAPI

app = FastAPI()




def init_model():
    """ 加载标题uie模型 """

    # 加载关键字
    template_dict = {}
    current_dir = abspath(dirname(__file__))
    template_file = abspath(join(current_dir, 'process/project_templates1.2.json'))
    templates = json.load(open(template_file, 'r', encoding='utf-8', errors='ignore'))
    base_schema = templates['base_schema']

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

    # 加载标题模型
    tmodel_dir = abspath(join(current_dir, 'models/uie_base_zmtitle5'))
    title_schema = ['作品名称', '作品设计', '作品面积', '地址', '作品风格', '时间', '设计师', '户型布局', '空间场所', '造价']
    model_title = Taskflow( task="information_extraction",
                            schema=title_schema,
                            batch_size=4,
                            device='gpu',
                            task_path=tmodel_dir,
                            use_fp16=True
                            )

    # 加载中文预训练模型
    model1_dir = abspath(join(current_dir, 'models/uie-base'))
    model_cn = Taskflow( task="information_extraction",
                         batch_size=4,
                         task_path=model1_dir,
                         use_fp16=True,
                         schema=base_schema,
                         schema_lang="cn"
                        )

    # 加载英文预训练模型
    model2_dir = abspath(join(current_dir, 'models/uie-base-en'))
    model_en = Taskflow( task="information_extraction",
                          batch_size=4,
                          task_path=model2_dir,
                          use_fp16=True,
                          schema=base_schema,
                          schema_lang="en"
                         )

    return model_title, model_cn, model_en, template_dict, base_schema





def generic_filter(res: Dict, use_filter: bool=True):

    """ 通用过滤 """

    def _lange_classifier(strs, rm_dt: bool=True, is_cn: bool=True):
        """ 字符串语言种类判断 """

        def is_all_english(strs):
            for i in strs:
                if i not in string.ascii_lowercase + string.ascii_uppercase:
                    return False
            return True

        def is_all_chinese(strs):
            for i in strs:
                if not '\u4e00' <= i <= '\u9fa5':
                    return False
            return True


        _reg = '~`!#$%^&*()_+-=|\';":/.,?><~·！@[\\]【\\】#￥%……&*（）——+-=“：’；、。，？》《{}'
        reg = _reg + '|\s|\W|\d' if rm_dt else _reg + '|\s|\W'
        strs = re.sub(rf"[{reg}]*", "", strs)

        if is_cn:
            return is_all_chinese(strs), strs
        else:
            return is_all_english(strs), strs


    def filter_prob_length(res: Dict, use_filter:bool=True, params:List[Tuple]=[('作品名称', 0.25, 0.45, 10, 2, 30, 3)])-> Dict:
        # 阈值过滤机长度处理
        """
        Args: 字段阈值及长度过滤, 适合处理字段：'作品名称','作品设计','地址','作品风格', '设计师','户型布局','空间场所'
            res: 原始预测结果，dict
            use_filter: 是否过滤，
            params: [(关键字(作品名称)，中文prob阈值(0.25)，英文prob阈值(0.45)，
                    中文text最大长度(10)，中文text最小长度(2)，英文text最大长度(30)，英文text最大长度(3) )]
        Returns: dict
        """

        dic = defaultdict(list)
        for k, vs in res.items():
            for v in vs:
                text = v.get('text').strip()
                prob = v.get('probability')
                if text:
                    param = list(filter(lambda x: x[0] == k, params)) if use_filter else []
                    param = param[0] if param else []

                    if param:
                        assert len(param) == 7, "params: 参数长度有误 "
                        is_cn, strs = _lange_classifier(text)
                        _, prob_cn, prob_en, maxlen_cn, minlen_cn, maxlen_en, minlen_en = param

                        if is_cn:
                            if prob_cn and maxlen_cn and minlen_cn and (prob > prob_cn) and (
                                    maxlen_cn >= len(strs) >= minlen_cn):
                                dic[k].append(text)
                        else:
                            if prob_en and maxlen_en and minlen_en and (prob > prob_en) and (
                                    maxlen_en >= len(strs) >= minlen_en):
                                dic[k].append(text)
                    else:
                        dic[k].append(text)
                del text, prob
        del res, params

        return dict(dic)



    def filter_area(res:Dict, use_filter:bool=True):
        """
        面积处理
        """

        if use_filter:
            key = '作品面积'
            if key in res:
                areas = res.get(key)
                if areas:
                    areas = list(filter(bool, map(lambda x: area_process(x), areas)))
                    if areas:
                        res.update({key: areas})
                    else:
                        del res[key]

        return res


    def filter_time(res: Dict, use_filter: bool=True):
        """ 时间处理"""

        if use_filter:
            key = '时间'
            dates = res.get(key)
            if dates:
                dates = list(filter(bool, map(lambda x: time_parser.process(x), dates)))
                if dates:
                    res.update({key: dates})
                else:
                    del res[key]

        return res


    def filter_currency(res: Dict, use_filter: bool=True):

        if use_filter:
            key = '造价'
            costs = res.get(key)

            if costs:
                costs = list(filter(bool, map(lambda x: currency_process(x), costs)))
                if costs:
                    res.update({key: costs})
                else:
                    del res[key]

        return res


    def filter_location(res: Dict, use_filter: bool=True):

        if use_filter:
            key = '地址'
            loc_data = res.get(key)
            if loc_data:
                loc_data = list(filter(bool, map(lambda x: location(x), loc_data)))
                if loc_data:
                    res.update({key: loc_data})
                else:
                    del res[key]

        return res


    params1 = [('作品名称', 0.50, 0.50, 15, 3, 70, 5),
                ('作品设计', 0.26, 0.50, 15, 2, 50, 3),
                ('作品风格', 0.30, 0.45, 15, 2, 15, 3),
                ('空间场所', 0.26, 0.45, 10, 2, 20, 3),
                ('户型布局', 0.30, 0.45, 15, 2, 15, 3),
                ('设计师',   0.40, 0.45, 15, 2, 50, 3),
                ('地址',    0.30, 0.45, 20, 2, 20, 3)]

    if res:
        res = filter_prob_length(res, use_filter=use_filter, params= params1)
        res = filter_area(res, use_filter=use_filter)
        res = filter_time(res, use_filter=use_filter)
        res = filter_currency(res, use_filter=use_filter)
        res = filter_location(res, use_filter=use_filter)

    return res



def title_extract(text:str, use_filter: bool =True):
    """ 标题内容提取 """

    title = TitleModel(text)

    if title[0]:
        title = title[0]
        return generic_filter(title, use_filter)
    else:
        return ''



def docment_extract(docments: List, use_filter: bool =True):
    " 正文信息抽提 "

    invalid_tags = {
        "设计主创": ["硬装", "软装", "空间与道具", "半包硬装", "建筑", "结构", "2009-2010年"],
        "项目户型": ['自然', "森林 · 光"],
        "项目风格": ['项目风格'],
        "施工单位": ['图标'],
        "项目地址": ['454m2'],
        "项目名称": ['Area 175.0 m2']
    }


    def pre_extract(texts):

        def match(LINE: str, TAGS: Dict, TEMPLATE_DICT: Dict):
            res = []
            words = list(filter(lambda w: (w in LINE) or (w in LINE.upper()), list(TEMPLATE_DICT.keys())))
            if words:
                for w in words:
                    if is_contains_chinese(LINE):  # 中文模式
                        reg = rf"([【]?[\s]?{w}[\s]?[】]?[\s]?([:|：|┃|/|／|│|丨|｜|︱]([\s\S]*?))(\。|\；|\;|$))"
                        reg_match = re.search(reg, LINE, re.IGNORECASE)

                    else:  # 英文模式
                        reg = rf"([【]?[\s]?{w}[\s]?[】]?[\s]?([:|：|┃|/|／|│|丨|｜|︱]([\s\S]*?))(\。|\.\s|\；|\;|$))"
                        reg_match = re.search(reg, LINE, re.IGNORECASE)
                        if not reg_match:  # 检查长度
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
                            #     if len(re.findall(reg2, mline)) > 512:
                            #         mline = re.split('[。|？|.|?|，|,]', mline)[0]

                            res.append(mline)
            del LINE
            return res

        candidates = []
        tags = OrderedDict()
        lines = texts.split("\n")
        for line in lines:
            line = line.replace(u"\xa0 \xa0 ", "").replace(u"\xa0", "")
            mlines = match(line, tags, TAGS_DICT)
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


    def is_contains_chinese(strs):
        """检验是否含有中文字符"""
        for _char in strs:
            if '\u4e00' <= _char <= '\u9fa5':
                return True
        return False


    def number_identify(res: Dict):
        # 数值数据过滤
        valid_key = ["项目面积", "项目造价", "硬装造价", "软装造价", "装修造价", "造价预算", "设计时间", "完工时间"]

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

        key = '项目面积'
        if key in res:
            areas = res.get(key)
            if areas:
                areas = list(filter(bool, map(lambda x: area_process(x), areas)))
                if areas:
                    res.update({key: areas})
                else:
                    del res[key]

        cost_keys = ['项目造价', '硬装造价', '软装造价', '造价预算']
        for key in cost_keys:
            if key in res:
                costs = res.get(key)
                if costs:
                    costs = list(filter(bool, map(lambda x: currency_process(x), costs)))
                    if costs:
                        res.update({key: costs})
                    else:
                        del res[key]


        return res


    def process(res: List[Dict], tags: Dict, use_filter:bool=True):
        dic = defaultdict(list)

        if res[0]:
            res = res[0]
            for k, vs in res.items():
                v = list(filter(bool, list(
                    filter(lambda i: i not in invalid_tags.get(tags.get(k), []) and i not in TAGS_DICT,
                           list(set([x.get("text") for x in vs]))))))
                # print("v ==>>>> ", v)
                if v:
                    for i in v:
                        if i not in dic[tags.get(k)]:
                            dic[tags.get(k)].append(i)

        if use_filter:
            # return dict(dic)
            return number_identify(dict(dic))
        else:
            return dict(dic)


    def uie_task(text: str, tags:Dict, schema: List, use_filter:bool=True):

        if schema is None:
            MODEL.set_schema(BASE_SCHEMA)
            res = MODEL(text)

        elif not is_contains_chinese("".join(schema)) and not is_contains_chinese(text):
            MODEL2.set_schema(schema)
            res = MODEL2(text)
        else:
            MODEL.set_schema(schema)
            res = MODEL(text)

        res = process(res, tags, use_filter)

        return res

    data = []
    for paragraph in docments:
        candidate_texts, tags = pre_extract(paragraph)
        if tags:
            res = uie_task(candidate_texts, tags, list(tags.keys()), use_filter)

            data.append(res)

    return data


TitleModel, MODEL, MODEL2, TAGS_DICT, BASE_SCHEMA = init_model()


