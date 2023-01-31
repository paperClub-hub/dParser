#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-01-31 12:30
# @Author   : NING MEI
# @Desc     :

"""文章关键字信息抽提"""

import re
import json
import string
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
    """ 加载uie模型 """

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

    # 加载标题模型(打标模型)
    tmodel_dir = abspath(join(current_dir, 'models/uie_base_zmtitle5'))
    title_schema = ['作品名称', '作品设计', '作品面积', '地址', '作品风格', '时间', '设计师', '户型布局', '空间场所', '造价']
    model_title = Taskflow(task="information_extraction",
                           schema=title_schema,
                           batch_size=4,
                           device='gpu',
                           task_path=tmodel_dir,
                           use_fp16=True)


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

    return model_title, model_cn,  model_en, template_dict, base_schema





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



def content_extract(docments: List, use_filter: bool =True):
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



def test_demo():
    doc_text = ["""项目名称：晋江青普梧林文化行馆
    位置：晋江
    设计公司：谜舍设计工作室
    摄影师：Ruijing Photo"""
                ]

    doc_text = [
        """青普梧林文化行馆位于福建省晋江市梧林古村落，场地面积约6000平米，由13栋福建传统民宅组成。谜舍设计受到著名人文度假集团青普TSINGPU的委托，主持将这个古建筑群落设计改造成客房、餐厅、茶馆、展览、论坛等兼具多元业态的文化旅游度假目的地。场地的建筑分为闽南红砖古厝以及南洋楼两种主要风格，形态迥异的建筑巧妙的彼此呼应，创造出极为丰富的建筑场所体验。我们希望保留这样自然原始的美感，并以较为谨慎的手法来处理整体的空间设计，尽可能的避免过度设计，在充分尊重地域的建筑文化的同时，并结合符合现代审美的设计语言，打造出具有文化性 及高品质度假感的“新闽南空间形态”。接待空间作为客人对于行馆室内空间形态的初次认知，我们保留了建筑的木结构，将划分房间的木质隔墙拆除，并通过引入玻璃天窗、暗藏空调等方式，营造出明亮通透且具有室内舒适性的空间，让客人感知到闽南古厝空间的 魅力及新的可能性。夯土材料的使用很好的呼应了传统建筑的历史感。我们重新整理了场地内每一栋闽南古厝的内部平面划分，做出了更为放松宜人的空间格局，并将面向内庭的立面打开，用木格栅进行填充，使自然光线进入到客房的同时又兼具相对的隐私性。
    客房内主要选用木质、涂料、草席等具有自然质感的材料。古建筑自身有时间肌理的闽南红砖墙、老木门等局部构件被有选择的保留了下来，并与现代崭新的材料在同一空间中形成巧妙的差异化美感，极大的提升了客房的体验以及空间张力。为了保证客人在古建筑中居住的舒适度，每间古厝客房都设置有空调和热水，并通过精确的机电设计，设备及管线被很好的隐藏在了空间的吊顶及墙体内部，力求不破坏客房空间古朴的氛围。房间的隔墙做了很好的隔音处理，我们在现场与工人师傅认真排查了梁柱交接处的空洞部分，保证客房有良好的隔音。古厝建筑的木窗被新的实木材料重新复刻，具有更好的使用性的同时，还原了老窗富有特色的开启方式。我们非常关注传统建筑中设计客房的空间尺度。过高过矮的空间都会影响住宿的舒适度，因此我们谨慎的处理不同区域的标高，希望客人在客房中既能体验到闽南古厝高大的建筑形制，又不失近人尺度的亲切感。我们向业主建议，在每一间客房都设置了黑胶唱机，梁柱中环绕着的音符会让有历史感的传统建筑空间显得更加丰富立体。部分较大的古厝两旁是有护厝的，我们将护厝的天井使用玻璃天窗封闭，在相对内向封闭的闽南古厝中打造出拥有自然光线的沐浴区域。
    南洋风格建筑是场地中另一种类别的闽南建筑，我们希望可以做出与闽南大厝风格有差异的南洋感客房空间。南洋文化是包容的文化，是多元的文化，我们试图通过设计将南洋文化的这一特质传递 给住在客房里的住客。在空间语言上，我们刻意的避开的传统南洋⻛格的典型符号，而是使用了较 为简约但是细部圆润处理的设计手法来营造出一种具有包裹感的空间。软装⻛格较为多元，融入大 量色彩、花纹及自然元素。这样的软硬装⻛格搭配方式，是我们对于南洋文化的解读，包容性强却又轻松自在。餐厅是最具有社交属性的公共空间。我们使用了新的设计手法对于空间的结构及材料进行演 绎，希望打造出一个非常开放明亮、且具有现代空间体验的闽南古厝。茶馆空间是连接行馆与行馆外的体验型空间，我们希望营造出层次丰富的空间氛围。一方 面，我们保留了古厝完整的院落格局及建筑形制，使访客可以感受到传统古厝的魅力;另 一方面，我 们也通过立面打开、玻璃盒子置入等方式创造出具有多场景及沉浸感的新型茶饮空间体验。茶馆空间的整体色调较为深沉，接近大地色，并融合具有时间感的中古风格的家具，与闽南古厝的历史厚重感相呼应。"""
    ]

    res = content_extract(doc_text)
    print(res)

    text = '2017海滨城众茗阁茶楼'
    res = title_extract(text)
    print(res)


TitleModel, MODEL, MODEL2 = None, None, None
if MODEL is None or MODEL2 is None:
    TitleModel, MODEL, MODEL2, TAGS_DICT, BASE_SCHEMA = init_model()



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


@app.post("/content")
async def content_extractor(params: dict):

    data = params.get('texts')
    isfilter = params.get('isfilter')

    try:
        res = content_extract(data, isfilter)

    except Exception as error:
        print(f"error: {error}")
        res = []

    return res


if __name__ == '__main__':
    ip = "0.0.0.0"
    port = 5002
    import uvicorn

    uvicorn.run(app='task_docment:app', host=ip, port=port, reload=True)
