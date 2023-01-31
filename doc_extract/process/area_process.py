#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @ Date    : 2022/12/27 11:44


###########################################################
#   室内面积归一化处理: 基于规则的归一化处理
###########################################################



import re

def _init_unit():

    unit_dict = {"平": "平方米", "坪": "平方米", "平米": "平方米", "平方米": "平方米", "方": "平方米", "平方": "平方米",
                 "坪方": "平方米", "㎡": "平方米", "m²": "平方米", "M²": "平方米", "M2": "平方米", "м²": "平方米",
                 "М2": "平方米", "sqm": "平方米", 'M平方': "平方米", "万平": "万平方米", "万平方": "万平方米", "万平米": "万平方米",
                 "平方英尺": "平方英尺", "sq ft": "平方英尺", "sqft": "平方英尺"}

    area_unit_map = {}
    for k, v in unit_dict.items():
        if k not in area_unit_map:
            area_unit_map.update({k: unit_dict.get(k)})
        if k.upper() not in area_unit_map:
            area_unit_map.update({k.upper(): unit_dict.get(k)})
        elif k.lower() not in area_unit_map:
            area_unit_map.update({k.lower(): unit_dict.get(k)})

    return area_unit_map




def chinese2digits(value):

    # 参考：https://www.cnblogs.com/anlizhaomi/p/15628838.html

    chinese_num = {
        u'〇': 0, u'零': 0,
        u'一': 1, u'壹': 1,
        u'二': 2, u'两': 2, u'贰': 2,
        u'三': 3, u'叁': 3,
        u'四': 4, u'肆': 4,
        u'五': 5, u'伍': 5,
        u'六': 6, u'陆': 6,
        u'七': 7, u'柒': 7,
        u'八': 8, u'捌': 8,
        u'九': 9, u'玖': 9,
        u'十': 10, u'拾': 10,
        u'百': 100, u'佰': 100,
        u'千': 1000, u'仟': 1000,
        u'万': 10000, u'萬': 10000,
        u'亿': 100000000, u'億': 100000000,
    }


    total = 0.00
    base_unit = 1
    dynamic_unit = 1
    for i in range(len(value) - 1, -1, -1):
        val = chinese_num.get(value[i]) # 最高位
        if val > 10:
            if val > base_unit:
                base_unit = val
            else:
                dynamic_unit = base_unit * val
        # 10既可以做单位也可做数字
        elif val == 10:
            if i == 0:
                if dynamic_unit > base_unit:
                    total = total + dynamic_unit * val
                else:
                    total = total + base_unit * val
            else:
                dynamic_unit = base_unit * val
        else:
            if dynamic_unit > base_unit:
                total = total + dynamic_unit * val
            else:
                total = total + base_unit * val

    return total



def area_process(strs: str):

    """ 面积处理 """

    # 面积匹配规则
    _area_units = r"(十|百|千|万|亿)?(平(方)?(千)?(分)?(厘)?(米|尺|方尺|英尺)|平(方公里|方)?|方(尺)?|坪|M平方|英寸|km²|hm²|㎡|M²|M2|м²|М2|dm²|cm²|mm²|(公)?亩|(公)?顷|英尺|sq ft|sqm|metre(s)?|(square meter))"

    reg = r"([\d]+|[\d]+[.|,][\d]+)(\+)?(\s)?"
    reg += _area_units
    reg += rf'|((零|一|二|三|四|五|六|七|八|九)?(十|百|千|万|亿)?(\s)?(零|一|二|三|四|五|六|七|八|九)?)(\s)?{_area_units}'

    # 面积数值数值
    # reg_digit = r'-?\d+\.?\,?\+?\d*|((零|一|二|三|四|五|六|七|八|九)?(十|百|千|万|亿)?(\s)?(点|零|一|二|三|四|五|六|七|八|九)?)'
    reg_digit = '(((\d+)(\.|\+)?(([,](\d+))+)?(\d+)?)|((零|一|二|三|四|五|六|七|八|九)(十|百|千|万|亿)+)+((零|一|二|三|四|五|六|七|八|九)?)?)'

    area_match_str = re.search(reg, strs, re.IGNORECASE)
    area_match_str = area_match_str.group() if area_match_str else ''
    
    area_info = ''
    if area_match_str:
        area_match_str = re.sub(r"[\s|\,|\，]", "", area_match_str)
        # area = re.search(reg_digit, area_match_str).group()
        _area = re.search(reg_digit, area_match_str)
        area = _area.group() if _area else ''

        if area:

            if len(re.findall(r'\d+', area)) == 0:
                area = chinese2digits(area)

            unit = area_match_str.replace(str(area), '')
            # print("unit: ", unit)
            unit = AreaUnitMap.get(unit) if unit in AreaUnitMap else unit
            area_info = f"{area}{unit}"

    return area_info


#
# def money_process(strs: str):
#     """ 造价金额处理 """
#
#     cn_num = '(一|二|三|四|五|六|七|八|九|壹|贰|叁|弎|仨|肆|伍|陆|柒|捌|玖|俩|两|零)'
#     chinese_unit = r'(〇|零|十|百|千|万|亿|兆|拾|佰|仟|萬|億|(million)|(billion)|(W|K))'
#     currency_unit = r'(块(钱)?(人民币)?|元((人民|港|日|澳|韩|(新)?台)币)?|(人民|港|日|澳|韩|(新)?台)币|圆(整)?|' \
#                     r'(美|港|澳门|日|韩|缅|马|新加坡|欧|加|新西兰|澳|澳大利亚)元|美(金|刀)|英镑|马克|法郎|卢布|泰铢|RMB)'
#
#     reg_digit = r"((\d+)(\.|-|\+)?(([,](\d+))+)?(\d+)?)(\s)?"
#
#     reg = '((' + reg_digit + '(' + chinese_unit + '[\s]?)?)(' + currency_unit + '[\s]?)?)?'
#
#     reg_cn = '((' + cn_num + chinese_unit + '+)+(' + cn_num + '?)?)'
#
#     p = '(((' + reg_digit + '(' + chinese_unit + '[\s]?)?)(' + currency_unit + '[\s]?)?)|' + '((' + cn_num + chinese_unit + '+)+(' + cn_num + '?)?))'
#
#
#     reg = '((' + reg_digit + '(' + chinese_unit + '[\s]?)?)(' + currency_unit + '[\s]?)?)?'
#
#     res = re.search(reg, strs)
#     print(strs)
#     if res:
#         res = res.group()
#         print("res ==>>> ", res)
#
#



AreaUnitMap = None
if AreaUnitMap is None:
    AreaUnitMap = _init_unit()


# if __name__ == '__main__':
#     t = '12m2'
#     # print(area_process(t))

