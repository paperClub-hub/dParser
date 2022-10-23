
import os

import json
from typing import Union,List,Dict
from collections import defaultdict
import re



templates = json.load(open("./dparser/model_files/templates.json", 'r'))

res = ['邱德光凸显新上海派的年轻化与个性化设计语汇，在一气呵成的流畅时空中，映照出时尚家居艺术的别样奢华之感。', '时尚东方 中国', '时尚、东方、艺术，任凭流年轮转，总归是青春时期的人们不曾遗落的珍贵宝藏。通过在整个居住空间的精心铺排，紫、黄、白三色构成了客厅区域的奇妙序曲，稳重中不失跳跃，吟诵中不失高扬。', '在简化软装的设计思路下，一张大地色单椅被设计师安静地置于客厅中央，像是年轻人身上难以脱去的稚嫩、洒脱之风，轻盈和自在。', '而优雅的紫色餐椅与走廊尽头的一副如深海般沁蓝画作所形成的视觉感受，有流动韵律之感，让静谧的空间顿时生意盎然。', '由客厅转入卧室，安静的曲调在此绵延至心的深处。也让这方人文气息浓厚的小天地生随着生活的律动而多彩多姿。', '打破静谧的墙上那幅装饰画作，淡粉与浅蓝的色彩对比下，为居住于此的青年群体营造出极具审美个性的生活场景。']


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
                    print(re.findall(r'[(^)$%~!@#$…&%￥—+=、。，；‘’“”：]', vaule))
                    if len(vaule) <= 30 and len(re.findall(r'[(^)$%~!@#$…&%￥—+=、。，；‘’“”：]', vaule)) <= 10:
                        result[key].append(vaule.strip())



        return dict(result)





uie = CASE_INFO()
text = "\n".join(res)
text = """东方文明流传有序的沿袭长三角城市开放包容的结合，这种双向的文化接受度将会是新装饰主义的很好的载体。带着这种思想的契合，邱德光主笔保利·天悦的设计。他所呈现三户不同风格示范空间为这座城市重新定义豪宅生活风范，以世界同步的时尚生活方式，为南京这个时代铸造新的梦想空间。
梦幻东方 新装饰主义 时尚 都会
邱德光："南京在中国拥有一个不可取代的优势"就是东方文明流传有序的沿袭长三角城市开放包容的结合，这种双向的文化接受度将会是新装饰主义的很好的载体。带着这种思想的契合，邱德光主笔保利·天悦的设计。他所呈现三户不同风格示范空间为这座城市重新定义豪宅生活风范，以世界同步的时尚生活方式，为南京这个时代铸造新的梦想空间。"""

print(uie.extract(text))