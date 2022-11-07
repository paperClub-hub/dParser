

import json
import re
import os
from typing import List
from glob import glob
from collections import OrderedDict
from collections import defaultdict



def load_json(file_in):
    return json.load(open(file_in, 'r', encoding='utf-8', errors='ignore'))



def postprocess_triplets(jdat):
    """ uie 关系三元组后处理 """

    def customdict_init():
        custom_dict = defaultdict(list)
        custom_dictfile = "/data/1_qunosen/project/xhs/doc_parser/src/custom_dict.txt"
        with open(custom_dictfile, 'r') as f:
            for line in f.readlines():
                line = line.strip().split("/")
                if len(line) == 2:
                    custom_dict[line[-1]].append(line[0])

        custom_dict = dict(custom_dict)

        # 风格
        custom_dict['STYLE'].extend(['古朴'])
        # 物体
        custom_dict['OBJECT'].extend(['落地玻璃', '青砖墙', '岩板'])
        # 形状
        custom_dict['SHAPE'].extend(["椭圆形", "长条形"])
        # 颜色
        custom_dict['COLOR'].extend(["空白", "木纹色", "爵士白", "弧白", '理石白', '墨绿'])
        # 材质
        custom_dict['MATERIAL'].extend(['实木', '理石白'])
        # 纹理
        custom_dict['PATTERN'].extend(['朦胧', '花纹', '哑光'])
        # 品牌
        custom_dict['BRAND'] = ['GIORGETTI-FIT']

        # 无关联
        custom_dict['unrelate'] = ['热带雨', '180度', '白光耀眼', '白玉兰花', '分界线', '绢丝绣']


        return custom_dict


    def _money_filter(triplet: List):
        """['客厅', '费用', ['10万']]"""
        node, edge, rel_contents = triplet
        pattern_area = "((([\d]+|[\d]+[.][\d]+)(\s)?|([\d]+|[\d]+[.][\d]+)$"
        PATTERN = re.compile(pattern_area, re.I)
        data = []
        for rel_content in rel_contents:
            res = PATTERN.match(rel_content)
            if res:
                data.append(res.group())

        if data:
            return [node, edge, data]
        else:
            return []

    def _area_filter(triplet: List):
        """ ['客厅', '面积', ['4.8米']] """

        node, edge, rel_contents = triplet
        _AREA_UNITS = r"(平(方)?(千)?(分)?(厘)?(米|英尺)|平|km²|hm²|㎡|M²|M2|dm²|cm²|mm²|(公)?亩|(公)?顷|英尺|(square meter))"
        _CN_NUMBER = r"((零|一|二|三|四|五|六|七|八|九)?(十|百|千|万|亿)?(\s)?(零|一|二|三|四|五|六|七|八|九)?)+"
        pattern_area = f"((([\d]+|[\d]+[.][\d]+)(\s)?{_AREA_UNITS})|({_CN_NUMBER})(\s)?{_AREA_UNITS})|([\d]+|[\d]+[.][\d]+)$"

        PATTERN = re.compile(pattern_area, re.I)

        data = []
        for rel_content in rel_contents:
            res = PATTERN.match(rel_content)
            if res:
                data.append(res.group())

        if data:
            return [node, edge, data]
        else:
            return []



    CUSTOM_DICT = customdict_init()
    #  无效关系字典，如"颜色"描述词不能为”STYLE“类词
    INVALID_DICT = {
        '颜色': ['STYLE', 'SPACE', 'LOSPACE', 'OBJECT', 'SHAPE', 'MATERIAL', 'PATTERN'],
        '纹理': ['STYLE', 'SPACE', 'LOSPACE', 'OBJECT', 'SHAPE', 'COLOR', 'MATERIAL'],
        '材质': ['STYLE', 'SPACE', 'LOSPACE', 'OBJECT', 'SHAPE', 'COLOR', 'PATTERN'],
    }

    NERS = defaultdict(list)
    TRIPLETS = []
    items = jdat['item']
    for item in items:
        ner_dict = item['ner']
        triplets = item.get("triplets")
        if triplets:
            for _item in triplets:
                # 去除不相关
                if list(set(_item[-1]).intersection(set(CUSTOM_DICT['unrelate']))):
                    triplets.remove(_item)

                # 去除无效面积
                if _item[1] == "面积":
                    _res_area = _area_filter(_item)
                    triplets.remove(_item)
                    if _res_area:
                        triplets.append(_res_area)

                if _item[1] == "费用":
                    _res_money = _money_filter(_item)
                    triplets.remove(_item)
                    if _res_money:
                        triplets.append(_res_money)


                # 去除不合理组合
                if _item[1] in INVALID_DICT:
                    _invalid_ws = []
                    _rel_names = INVALID_DICT.get(_item[1])
                    for _name in _rel_names:
                        if _name in CUSTOM_DICT:
                            _invalid_ws.extend(CUSTOM_DICT.get(_name))
                    if _invalid_ws and list(set(_item[-1]).intersection(set(_invalid_ws))):
                        triplets.remove(_item)

        if ner_dict:
            for nk, nvs in ner_dict.items():
                for nv in nvs:
                    if nv not in NERS[nk]:
                        NERS[nk].append(nv)

        if triplets:
            for triplet in triplets:
                if triplet not in TRIPLETS:
                    TRIPLETS.append(triplet)


    return {"ner": dict(NERS), "triplets": TRIPLETS}




if __name__ == '__main__':

    pjfiles = glob("/data/1_qunosen/project/xhs/doc_parser2/output/project_info/*.json")
    ujfiles = glob("/data/1_qunosen/project/xhs/doc_parser2/output/uie_items/*.json")
    njfiles = glob("/data/1_qunosen/project/xhs/doc_parser2/output/ner_words/*.json")

    pjfiles2 = list(map(lambda x: os.path.basename(x), pjfiles))
    ujfiles2 = list(map(lambda x: os.path.basename(x), ujfiles))
    njfiles2 = list(map(lambda x: os.path.basename(x), njfiles))
    save_dir = "/data/1_qunosen/project/xhs/doc_parser2/output/merge"
    for i, jfile in enumerate(pjfiles):
        if os.path.basename(jfile) in ujfiles2 and os.path.basename(jfile) in njfiles2:
            ufile = f"/data/1_qunosen/project/xhs/doc_parser2/output/uie_items/{os.path.basename(jfile)}"
            nfile = f"/data/1_qunosen/project/xhs/doc_parser2/output/ner_words/{os.path.basename(jfile)}"

            print(jfile)
            data = OrderedDict()
            pdat = load_json(jfile)
            udat = load_json(ufile)
            ndat = load_json(nfile)
            del ndat['url']
            udict = postprocess_triplets(udat)
            data.update(**pdat)
            data.update(**udict)
            data.update(**ndat)

            print(json.dumps(data, ensure_ascii=False, indent=True),
                  file=open(f"{save_dir}/{os.path.basename(jfile)}", 'w'))
