#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-10-20 14:36
# @Author   : NING MEI
# @Desc     :



################################################################################
#
#  建E网、知末等项目关键词信息抽提。（project info extract）
#
#################################################################################


import re
from typing import List, Dict
from paddlenlp import Taskflow
from typing import Dict, List, Union
from collections import defaultdict
from dparser.utils.util import templates, uie_postprocess
from dparser.extract.uextract import uie


class CASE_INFO():
    """ 文本中项目关键字信息抽提 """

    def __init__(self):
        self.project_templates = templates.get("project_templates")

    def extract(self, text: str) -> Dict:
        """ 项目信息抽提入口 """

        result = defaultdict(list)

        if all([symbol in text for symbol in ["【", "】", "："]]):
            reg = re.compile("(【(.*)】：(.*))")
            macth = re.findall(reg, text)
            if macth:
                text = max(macth[0], key=len)
                texts = [t for t in re.split("[【|】|：]", text) if t]
                if texts:
                    _res = dict([texts[i], texts[i + 1]] for i in range(0, len(texts) - 1, 2))
                    for _k, _v in _res.items():
                        for k, v in self.project_templates.items():
                            if _k in k or _k in v:
                                result[k].append(_v.strip())

        else:  # 通用
            if "\n" in text:
                texts = [t for t in text.split('\n') if t]
            else:
                texts = [t for t in text.split() if t]

            for line in texts:
                key = ''
                vaule = []
                for k, v in self.project_templates.items():
                    if (k in line and ("｜" in line or "丨" in line or "|" in line)) or \
                            (k in line and (":" in line or "：" in line)) or \
                            (k in line and ("/" in line)) or \
                            (len(list(filter(lambda x: x in line, v))) > 0 and ( "｜" in line or "丨" in line or "|" in line)) or \
                            (len(list(filter(lambda x: x in line, v))) > 0 and (":" in line or "：" in line)) or \
                            (len(list(filter(lambda x: x in line, v))) > 0 and ("/" in line)):

                        key = k
                        if "：" in line:
                            vaule = line.split("：")[-1].strip()
                        elif ":" in line:
                            vaule = line.split(":")[-1].strip()
                        elif "｜" in line:
                            vaule = line.split("｜")[-1].strip()
                        elif "丨" in line:
                            vaule = line.split("丨")[-1].strip()
                        elif "|" in line:
                            vaule = line.split('|')[-1].strip()
                        elif "/" in line:
                            vaule = line.split('/')[-1].strip()

                if key and vaule:
                    vaule = vaule.strip().replace("?", "")
                    if len(vaule) <= 30 and len(re.findall(r'[(^)$%~!@#$…&%￥—+=、。，；‘’“”：]', vaule)) <= 10:
                        result[key].append(vaule.strip())

        if not result:

            result = self._uie_case_info(text)

        return dict(result)


    def _uie_case_info(self, text: str, threshold: float = 0.35):
        result = defaultdict(list)
        print("uie ... ")
        res_uie = uie.base_extract(text, schema=list(self.project_templates.keys()))
        info = uie_postprocess(res_uie, threshold=threshold, reform=False)
        if info:
            info = info[0]
            for k, v in info.items():
                vs = [x.get("text") for x in v]
                result[k].extend(vs)

        return result


