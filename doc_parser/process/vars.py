#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-10-24 9:47
# @Author   : NING MEI
# @Desc     :




import os
import re
import json



def load_json(json_file: str):
    return json.load(open(json_file, 'r', encoding='utf-8'))


def load_stopwords(file:str):
    return [line.strip() for line in open(file, 'r', encoding='utf-8').readlines() if line.strip()]


def create_jieba_dict(txt_file: str, jieba_path:str):
    data = []
    dic = {}
    with open(txt_file, 'r', encoding="utf-8") as f:
        for line in f.readlines():
            items = line.strip().split("/")
            if len(items) > 1:
                w = items[0]
                label = items[-1]
                dic[w] = label
            else:
                w = items[0]
            data.append(w)

    print('\n'.join(data), file=open(jieba_path, 'w', encoding='utf-8'))

    return dic


#----------------------------- 正则规则
# 面积提取
_AREA_UNITS = r"(平(方)?(千)?(分)?(厘)?(米|英尺)|平|km²|hm²|㎡|M²|M2|dm²|cm²|mm²|(公)?亩|(公)?顷|英尺|(square meter))"
_CN_NUMBER = r"((零|一|二|三|四|五|六|七|八|九)?(\s)?(十|百|千|万|亿)?(\s)?(零|一|二|三|四|五|六|七|八|九)?)+"
INDOOR_AREA_REG = "|".join(
    [
        f"(([\d]+(\s)?{_AREA_UNITS})|({_CN_NUMBER})(\s)?{_AREA_UNITS})",
        "((面积|大小)((:|：|\n|\r)|(\s)?|\s|是|为|有|(大)?约|(大概)|(接近)|((估|预)计)|相当))" + f"([\d]+|({_CN_NUMBER}))" + f"{_AREA_UNITS}?"
        ]
    )


INDOOR_AREA_PATTERN = re.compile(INDOOR_AREA_REG, re.I)



_root_path = os.path.dirname(os.path.abspath(__file__))
template_file = os.path.normpath(os.path.join(_root_path, "../process/templates.json"))
custom_dict_file = os.path.normpath(os.path.join(_root_path, "../process/custom_dict.txt"))
jieba_dict_file = os.path.normpath(os.path.join(_root_path, "../process/jieba_dict.txt"))
stopwords_file = os.path.normpath(os.path.join(_root_path, "../process/stopwords.txt"))
custom_model_path = os.path.normpath(os.path.join(_root_path, "../process/model_best"))
templates = load_json(template_file)
stopwords = load_stopwords(stopwords_file)

wordflagdict = {}
if not wordflagdict:
    wordflagdict = create_jieba_dict(custom_dict_file, jieba_dict_file)


# if __name__ == '__main__':
#     text = "房间大小是三十平米，适合一个人居住。"
#     res = [item.group().strip() for item in  INDOOR_AREA_PATTERN.finditer(text)]
#     print(res)