#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-01-31 12:30
# @Author   : NING MEI
# @Desc     :


""" 文本标题信息抽提 """


import re
import string
from typing import (List, Dict, Tuple)
from process.date_process import time_parser
from process.area_process import area_process
from process.cost_process import currency_process
from process.location_process import location
from collections import defaultdict, OrderedDict

from paddlenlp import Taskflow
from os.path import abspath, dirname, join
from fastapi import FastAPI


app = FastAPI()



def init_model():
    """ 加载标题uie模型 """

    # 加载关键字

    current_dir = abspath(dirname(__file__))

    # 加载标题模型
    tmodel_dir = abspath(join(current_dir, 'models/uie_base_zmtitle5'))
    title_schema = ['作品名称', '作品设计', '作品面积', '地址', '作品风格', '时间', '设计师', '户型布局', '空间场所', '造价']
    model_title = Taskflow( task="information_extraction",
                            schema=title_schema,
                            batch_size=4,
                            device='gpu',
                            task_path=tmodel_dir,
                            use_fp16=True)

    return model_title





def generic_filter(res: Dict, use_filter: bool=True):

    """ 通用过滤 """

    def _lange_classifier(strs, rm_dt: bool=True, is_cn: bool=True):
        """ 字符串语言种类判断 """

        def is_all_english(strs: str):
            for i in strs:
                if i not in string.ascii_lowercase + string.ascii_uppercase:
                    return False
            return True

        def is_all_chinese(strs: str):
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




def title_extract(text: str, use_filter: bool=True):
    """ 标题内容提取 """

    title = TitleModel(text)

    if title[0]:
        title = title[0]
        return generic_filter(title, use_filter)
    else:
        return {}




TitleModel= None
if TitleModel is None:
    TitleModel = init_model()



@app.post("/title")
async def title_extractor(params: dict):

    text = params.get('text')
    isfilter = params.get('isfilter')
    try:
        res = title_extract(text, use_filter=isfilter)
    except Exception as error:
        print(f"error: {error}")
        res = {}

    return res




if __name__ == '__main__':
    ip = "0.0.0.0"
    port = 5001
    import uvicorn

    uvicorn.run(app='task_title:app', host=ip, port=port, reload=True)

