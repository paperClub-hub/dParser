#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-10-24 8:59
# @Author   : NING MEI
# @Desc     :



#------------------------------------------------------------
#   案例文本项目信息抽提：基于规则的提取方法
#------------------------------------------------------------


import re
import os
import json
from glob import glob
from typing import List, Dict
from collections import defaultdict



def load_json(file_in):
    return json.load(open(file_in, 'r', encoding='utf-8', errors='ignore'))

def doc2paragraph(doc):
    """ 按照图片将文章拆分成段落  """
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




# templates = load_json("process/templates.json")
templates = load_json("process/templates.json")
project_templates = templates['project_templates']




def projectinfo_extract(texts):
    """ 项目信息抽提,
     """
    result = defaultdict(list)
    paragraphs = texts.split("\n")
    for line in paragraphs:
        line = line.replace(u"\xa0 \xa0 ", "").replace(u"\xa0", "")  # 富文本 &nbsp替换
        for tk, tvs in project_templates.items():
            key = ''
            value = ''
            matched_line = ''
            _start = -1
            _end = -1
            # reg = rf"([【]?[\s]?{tk}[\s]?[】]?)[\s|:|：|/|丨|｜|︱][\s]?(.*)"
            reg = rf"([【]?[\s]?{tk}[\s]?[】]?[\s|:|：|┃|/|／|│|丨|｜|︱|\s](.*))"
            reg_match = re.search(reg, line)

            if reg_match:
                key = tk
                matched_line = reg_match.group()
                _start = matched_line.find(tk)
                # print("matched_line: ", matched_line)
            else:
                for tv in tvs:
                    # reg_tv = rf"([【]?[\s]?{tv}[\s]?[】]?)[\s|:|：|/|丨|｜|︱][\s]?(.*)"
                    reg_tv = rf"([【]?[\s]?{tv}[\s]?[】]?[\s|:|：|┃|/|／|│|丨|｜|︱|\s](.*))"
                    reg_match = re.search(reg_tv, line)
                    if reg_match:
                        key = tk
                        _start = matched_line.find(tk)
                        matched_line = reg_match.group()
                        # print("matched_line: ", matched_line)
                        break

            if matched_line:

                # if "｜" in matched_line:
                #     value = matched_line.split("｜")[1].strip()
                # elif "丨" in matched_line:
                #     value = matched_line.split("丨")[1].strip()
                # elif "|" in matched_line:
                #     value = matched_line.split('|')[1].strip()
                # elif "︱" in matched_line:
                #     value = matched_line.split('︱')[1].strip()
                # elif "/" in matched_line:
                #     value = matched_line.split('/')[1].strip()
                # elif "／" in matched_line:
                #     value = matched_line.split("／")[1].strip()
                # elif "：" in matched_line:
                #     value = matched_line.split("：")[1].strip()
                # elif ":" in matched_line:
                #     value = matched_line.split(":")[1].strip()
                # elif " " in matched_line:
                #     value = matched_line.split(' ')[1].strip()

                vv = re.split('[：|:|｜|丨|︱|/|／|/|\s]', matched_line)
                vv = list(filter(bool, vv))
                # print(vv)
                value = vv[1] if len(vv) > 1 else vv[0]
                _end = matched_line.find(value)

            if key and value:
                span = _end - _start
                # print("span: ", span)
                result[key].append(value)

    return dict(result)


def projectinfo_extract2(texts):

    result = defaultdict(list)
    WORDS = set()
    for k, v in project_templates.items():
        WORDS.add(k)
        WORDS.update(v)
    WORDS = list(WORDS)

    # 拆分句子
    SPANS = sorted(set([text.find(w) for w in WORDS if text.find(w) != -1]))
    if SPANS:
        for i, _start in enumerate(SPANS[:-1]):
            line = texts[_start: SPANS[i + 1]]
            if i == len(SPANS[:-1]) - 1: # 最后一个
                line = texts[SPANS[i]: ]

            if line.strip():
                line = line.replace(u"\xa0 \xa0 ", "").replace(u"\xa0", "").replace("\n", " ")  # 富文本 &nbsp替换
                # print("line: ", line)
                _key_index = 0
                _vale_index = 0
                for tk, tvs in project_templates.items():
                    key = ''
                    value = ''
                    matched_line = ''
                    reg = rf"([【]?[\s]?{tk}[\s]?[】]?[\s|:|：|┃|/|／|│|丨|｜|︱|\s](.*))"
                    _reg_match = re.search(reg, line)
                    if _reg_match:
                        key = tk
                        matched_line = _reg_match.group()
                        _key_index = matched_line.find(tk)
                        # print("matched_line： ", matched_line)
                    else:
                        for tv in tvs:
                            reg_tv = rf"([【]?[\s]?{tv}[\s]?[】]?[\s|:|：|/|／|丨|｜|︱|\s](.*))"
                            _reg_match = re.search(reg_tv, line)
                            if _reg_match:
                                key = tk
                                matched_line = _reg_match.group()
                                _key_index = matched_line.find(tv)
                                # print("tv: ", tv, matched_line)
                                break

                    if matched_line:

                        if "｜" in matched_line:
                            value = matched_line.split("｜")[1].strip()
                        elif "丨" in matched_line:
                            value = matched_line.split("丨")[1].strip()
                        elif "|" in matched_line:
                            value = matched_line.split('|')[1].strip()
                        elif "︱" in matched_line:
                            value = matched_line.split('︱')[1].strip()
                        elif "/" in matched_line:
                            value = matched_line.split('/')[1].strip()
                        elif "／" in matched_line:
                            value = matched_line.split("／")[1].strip()
                        elif "：" in matched_line:
                            value = matched_line.split("：")[1].strip()
                        elif ":" in matched_line:
                            value = matched_line.split(":")[1].strip()
                        elif " " in matched_line:
                            value = matched_line.split(' ')[1].strip()
                        _vale_index = matched_line.find(value)

                    dist = _vale_index - _key_index
                    if key and value and (dist > 0 and dist < 20):
                        if len(value) > 30:
                            value = value.split()[0]
                        # print(_vale_index - _key_index)

                        result[key].append(value)

    return dict(result)


# text = "业主及规划竞赛程序：2013年 设计：曼哈德·冯·格康和尼古劳斯·格茨以及福克玛·西弗斯 竞赛阶段及实施阶段项目负责人：科杜拉·诺埃尔 竞赛阶段设计人员：伊讷斯·阿肯贝格瓦，伊莲娜·库维略，法比安·法贝尔，桑卓·科罗尔，马丁·马耶夫斯基，帕特里克·特茨拉夫，伊萨贝尔·孚美尔，阿费德·克瑙尔 实施阶段设计人员：伊莲娜·库维略，安娜·法肯巴赫，尤利娅·弗朗兹可，弗里德里克·海瑟尔，施特芬·洛佩奥兹，嘉宝·努讷曼，伊娃·史塔克，施特拉·特朗，米凯莱·瓦滕富尔，阮天洪阳（河内），陈丛德（河内），弗洛里安·维迪（上海） 合作设计单位：TwoG architects，胡志明市 幕墙设计：Drees & Sommer迪索工程咨询有限公司 结构设计：WSP global 灯光设计：ASA Lighting Design Studios 项目管理：Colliers International 业主：越南德国中心投资有限公司 建设周期：2014-2017年 总建筑面积：52704m2\nBuilding owner and planning competition awarded to gmp in 2013 Design: Meinhard von Gerkan with Nikolaus Goetze und Volkmar Sievers Project leader competition and detailed design: Kordula Noelle Competition design team: Ines Arkenbergova, Elena Cubillo, Fabian Faerber, Arved Knauer, Sandra Kroll, Martin Majewski, Patrick Tetzlaff, Isabel Vollmer Detailed design team: Elena Cubillo, Anna Falkenbach, Julia Franzke, Frederik Heisel, Steffen Lepiorz, Gabi Nunnemann, Eva Staack, Stella Tran, Michéle Watenphul, Tran Cong Duc (Hanoi), Nguyen Tien Hong Duong (Hanoi), Florian Wiedey (Shanghai) DGNB Auditor: Urs Wedekind Local architectural practice: TwoG Architecture Ho Chi Minh City Facade Consultants: Drees & Sommer SE Structural engineering & technical services engineering: WSP Vietnam Lighting design: ASA Lighting Design Studios Building and property management: Colliers Vietnam Client: Deutsches Haus Invest Ltd. Construction period: 2014–2017 GFA: 52,704 m2 (including basements)"
# text = "#项目信息#\n项目地址┃address：融侨华府\n项目风格┃style：现代\n建筑面积┃Built-up area：125㎡\n项目设计┃designer：三伏设计\n项目施工┃construction：三伏施工\n项目摄影┃ photograph:梵镜空间摄影\n总共花费┃Total cost：42万\n本案是一个125平的平层结构，目前主要是夫妻两人和母亲一起居住，男主人是大学老师，会有比较多的书籍和刊物，所以需要比较多的收纳空间还有独立的书房。通过沟通方案和风格喜好，我们确定了稳重又经久的现代风。"
# text  = "内里的心情和感受却又是精彩而不同的\n项目名称：《\nHalf Dream\n项目面积：\n360"
# text = "项目名称：《\nTangerine Tango\n项目面积：\n180"
# text = "◆address/东湖睿园◆\n◆style/现代台式简约◆\n◆Built-up area/160㎡◆\n◆designer/三伏装饰设计◆\n◆construction/三伏装饰设计◆\n◆Photographer/陈铭◆\n◆Total cost／45万◆\n本案经改造后变为一套四居室空间，四口常住人口，父母偶尔过来居住。女主在一家大型外企工作，经常出差居住各种酒店，选定室内设计氛围为现代。男主则充分尊重女主的意见。一个完整的室内家居空间表达既要在功能布置上给与流畅的动线互动，又需要在精神诉求上满足屋主所需。安藤忠雄曾说：奢华的家要有安静的感觉，触动心灵深处！"
# text = "项目名称：《\n中国式优雅\n项目\n面积\n170平\n项目楼盘：\n新湖国际天润阁\n项目用途：私人住宅\n空间设计\n叶永志\n软装设计"
# text = "华发·外滩首府\nProject name |\nHuafa ·\nwai tan shou fu\n项目面积  |\n约220m2\nArea  |   about 220m2\n项目风格  |\n现 代\n美 式\nProject style\nAmerican style\n设计团队  |  武汉品承空间设计有限公司\nDesign  team |\nWuhan pincheng space design co. LTD\n设计主材 |\n原木护墙板、\n实木地板\n、墙布、进口家具"
# text = "Project name |\nrong\nchuang yi hao\n项目面积  |\n约215m2\n|   about 215m2\nabout 215m2\n项目风格  |\n意 式 轻 奢\nProject style\nItalian luxury\n设计团队  |  武汉品承空间设计有限公司\nDesign  team |\nWuhan pincheng space design co. LTD\n设计主材 |\n岩板\n、木饰面、硬包、进口家具"
# text = "项目名称 |\n万 科 · 御 玺 滨 江\nProject name |\nVanke\n· yu xi bin jiang\n项目面积  |\n约225m2\nArea  |   about 225m2\n项目风格  |\n现 代 简 约 风\nProject style\nEntry lux\n设计团队  |  武汉品承空间设计有限公司\nDesign  team |\nWuhan pincheng space design co. LTD\n设计主材 |\n岩板\n、木饰面、不锈钢、进口家具"

text = "项目信息 项目名称：依云水岸样板房 项目地址：中国.武汉 竣工时间：2022年6月 项目面积：94㎡户型/108㎡户型 设计公司：青岛腾远 软装设计：深圳市里约环境与艺术设计有限公司 设计主创：丛欣.徐雅丽 业主团队：永同昌集团.招商蛇口.车都集团 业主设计管理团队：永同昌孙超、白磊"


res1 = projectinfo_extract(text)
res2 = projectinfo_extract2(text)

print("res1: ", res1)
print("res2: ", res2)

zm_data = load_json("./zhimo_all.json")


save_dir = "./out"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)


for i, doc in enumerate(zm_data):
    data = {}
    url = doc['url']
    doc_id = url.split("/")[-2]
    data["url"] = url
    data["data"] = []
    paragraph_texts = doc2paragraph(doc)
    if paragraph_texts:
        for p in paragraph_texts:
            # res = projectinfo_extract2(p)
            res = projectinfo_extract(p)
            if res:
                print("res: ", res)
                data["data"].append({
                    # "text": p,
                    "info": res
                })

        infos = [x['info'] for x in data['data'] if x['info']]
        if infos:
            print(json.dumps(data, ensure_ascii=False, indent=4), file=open(os.path.join(save_dir, f"{doc_id}.json"), 'w', encoding='utf-8'))

    if i > 100:
        break
