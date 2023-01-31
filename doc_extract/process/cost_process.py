#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @ Date    : 2022/12/29 9:06


###########################################################
#   作品造价处理
###########################################################


import re



def currency_process(strs: str):


    def money2digits(value):

        num_map = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
            '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}

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
            u'兆': 1000000000000,
        }

        chinese_num.update(num_map)

        total = 0.00
        base_unit = 1
        dynamic_unit = 1
        for i in range(len(value) - 1, -1, -1):
            val = chinese_num.get(value[i])  # 最高位
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


    cn_num = '(〇|一|二|三|四|五|六|七|八|九|壹|贰|叁|弎|仨|肆|伍|陆|柒|捌|玖|俩|两|零)'
    ch_unit = '(十|百|千|(多)?万|(多)?亿|兆|拾|佰|仟|(多)?萬|(多)?億|W|K|(million)|(billion))'
    cu_unit = r'(块(钱)?(人民币)?|元((人民|港|日|澳|韩|(新)?台)币)?|(人民|港|日|澳|韩|(新)?台)币|圆(整)?|' \
              r'(美|港|澳门|日|韩|缅|马|新加坡|欧|加|新西兰|澳|澳大利亚)元|美(金|刀)|英镑|马克|法郎|卢布|泰铢|RMB)'
    digit = r"((\d+)(\.|-|\+)?(([,](\d+))+)?(\d+)?)(\s)?"

    # 1. 整数 + 汉字数值单位，如， ‘3百多万’，‘150万’, '400亿'
    currency_reg1 = '(^(\d+)' + ch_unit + '+)$'

    # 2. 数值混合类金额, 如，'7.5W', '5.99亿', ‘3000块钱’, '20-50万'
    currency_reg2 = '((^' + digit + '(' + ch_unit + '[\s]?)?)(' + cu_unit + '[\s]?)?)$'

    # 3. 纯汉字金额, 如, '一百五十二万元'
    currency_reg3 = '(^(' + cn_num + ch_unit + '+)+(' + cn_num + '?)' + cu_unit + '?)$'

    PATTERN = '|'.join([currency_reg1, currency_reg2, currency_reg3])


    money_match_str = re.search(PATTERN, strs, re.IGNORECASE)
    money_match_str = money_match_str.group() if money_match_str else ''

    special_maps = {'W': '万', 'w': '万', 'K': '千', 'k': '千'}
    money_info = ''
    if money_match_str:

        unit_ = re.search(cu_unit, money_match_str, re.IGNORECASE)
        UNIT = unit_.group() if unit_ else ''
        MONEY = money_match_str.replace(UNIT, '') if UNIT else money_match_str

        chunit_ = re.search(ch_unit, MONEY, re.I) # 金额单位
        if chunit_:
            chunit_ = chunit_.group()
            if chunit_ in special_maps:
                MONEY = MONEY.replace(chunit_, special_maps.get(chunit_))

        # if re.search(currency_reg1, strs, re.I):
        #     if len(re.findall('\d', strs)) == 1:
        #         MONEY = money2digits(MONEY)

        if re.search(currency_reg3, strs, re.I):
            MONEY = money2digits(MONEY)

        if UNIT in ['块', '块钱', '人民币', '元人民币', 'RMB', 'rmb']:
            UNIT = ''


        if UNIT:
            money_info = f"{MONEY}{UNIT}"
        else:
            money_info = MONEY


    return money_info



def demo():
    ts = ['2.5亿',
          '两千块',
          '4000',
          '62w',
          '50-100万',
          '1100',
          '25亿美元',
          '熊本·八百万',
          '8万块钱',
          '23.8亿',
          '13万',
          '1000000',
          '7 亿',
          '3000',
          '一加亿',
          '37万',
          '3K',
          '600',
          '三百亿',
          '8000',
          '60w',
          '4.4亿',
          '400亿',
          '5000万',
          '壹念叁仟',
          '超千万',
          '1w',
          '70亿',
          '仟佰亿',
          '2,000',
          '206万',
          '银亿',
          '800万',
          '20万',
          '13.6亿',
          'W',
          '12亿',
          '11000',
          '1W',
          '75万',
          '800',
          '10 亿美金',
          '3.1 亿',
          '3亿',
          '400 million',
          '2.2 亿',
          '12,000',
          '2.25亿',
          '2K',
          '50',
          '10万',
          '500亿',
          '10w',
          '3.2亿',
          '红万',
          '10000元',
          '3 亿美元',
          '75w',
          '280',
          '70W',
          '1400',
          '7.5W',
          '26万',
          '55万',
          '3000元',
          '85W',
          '千百億',
          'LTW',
          '3000块钱',
          '10000',
          '100万',
          '30万',
          '200万',
          'JSW',
          '11万',
          '千千万',
          '2亿',
          '40万',
          '78亿',
          '1.6亿',
          '1500',
          '15000',
          '40xxx',
          '金百万',
          '6万',
          '十亿',
          '20-50万',
          '千万',
          '51亿人民币',
          '49万',
          '5.99亿',
          '60万',
          '于千万',
          '28W',
          '250',
          '4000万',
          '1.1亿',
          '80万',
          '一万元',
          '3.8亿',
          '1万元',
          '2000',
          '350 w',
          '10亿美金',
          '190 w',
          '60元人民币',
          '0.000',
          '3 亿',
          '5千万',
          '上亿',
          '一万八',
          '五十',
          '23万',
          '260万元',
          '30亿',
          '1600万',
          '16万',
          '10亿',
          '298',
          '上千万',
          '5000',
          '160 million',
          '数百万',
          '45万',
          '46亿',
          '6000',
          '1800',
          '15万',
          '1.亿',
          '22万',
          '1.3亿',
          '2.4亿',
          '8,000',
          '几百万',
          '20亿美元',
          '38亿',
          '70万',
          '12万',
          '3百多万']

    for t in ts:
        t = t.replace(' ', '')
        out = currency_process(t)
        print(f'{t} >>>>> {out}')




