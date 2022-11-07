#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-10-24 8:59
# @Author   : NING MEI
# @Desc     :



#------------------------------------------------------------
#   案例文本项目信息抽提
#------------------------------------------------------------


import re
import os
from glob import glob
from typing import List, Dict
from collections import defaultdict
from process.vars import *
from paddlenlp import Taskflow
import asyncio


class PROJECT_INFO():
    """ 文本中项目关键字抽提 """

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


        return dict(result)



def custom_uiemodel(text: str):
    """ 模型补充提取 """

    if len(text) > 512:
        text = text[-512:]

    data = defaultdict(list)
    res = MODEL(text)
    if res[0]:
        for k, v in res[0].items():
            vs = list(set([x.get('text') for x in v]))
            data[k].extend(vs)

    return dict(data)




def run_zm_dataset(save_dir):

    def uie_extract(text: str):
        " uie 抽提项目信息 "
        if len(text) > 512:
            text = text[-512:]

        data = defaultdict(list)
        res = MODEL(text)
        if res[0]:
            for k, v in res[0].items():
                vs = list(set([x.get('text') for x in v]))
                data[k].extend(vs)

        return dict(data)


    def task_func(doc):
        url = doc['url']
        doc_id = url.split("/")[-2]
        doc_txt = [d.get('txt') for d in doc.get('medias') if d.get('txt')]

        if doc_txt:
            print("doc_id: ", doc_id)
            save_json = os.path.join(save_dir, f"{doc_id}.json")
            texts = "\n".join(doc_txt)
            project_info = pinfo.extract(texts)

            if project_info:
                print(json.dumps({
                    "url": url,
                    "project_info": project_info,
                }, ensure_ascii=False), file=open(save_json, 'w'))

            else:
                project_info = uie_extract(texts)
                if project_info:
                    print(json.dumps({
                        "url": url,
                        "project_info": project_info,
                    }, ensure_ascii=False), file=open(save_json, 'w'))

    def task_run(zm_data):
        """ 协程处理 """
        tasks = [task_func(doc) for doc in zm_data]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    zm_data = json.load(open("./zhimo_all.json", 'r'))
    if not os.path.exists(save_dir): os.makedirs(save_dir)
    done_files = [os.path.splitext(os.path.basename(x))[0] for x in glob(save_dir + "/*.json") if x]
    zm_data = [x for x in zm_data if x['url'].split("/")[-2] not in done_files]

    task_run(zm_data)





MODEL = None
if MODEL is None:
    MODEL = Taskflow(task='information_extraction',
                    schema=templates["project_templates"],
                    use_faster=True
	                )



pinfo = PROJECT_INFO()


if __name__ == '__main__':

    texts = '邱德光畅谈绿城·盛世滨江四重空间所演绎的艺术生活“因为深知黄浦江与外滩对于上海这座城市的意义，所以在设计绿城·盛世滨江这样一线江景豪宅时，我们力图将最大的手笔留给滨江的视野。让室内、室外空间浑然天成，让客户透过270°的视角，感受最极致的江景。这是我的设计初衷，也是对黄浦江的敬意。”——邱德光2014年10月24日，一场以“巨匠·境界——邱德光畅谈滨江艺术人居”为主题的发布会在位于外滩世博滨江板块内的绿城·盛世滨江盛大召开。众多业内、媒体及文化艺术人士齐聚现场，与邱德光先生一同探讨申城滨江豪宅生活及设计理念。被誉为“新装饰主义大师”、“台湾设计界领军人物”的邱德光先生，纵横业界三十多年，专注室内空间中艺术细节和整体氛围的呈现，在世界各地均有知名豪宅项目由其设计打造。其中绿城·盛世滨江坐拥外滩一线江景，其于2014年8月起陆续推出的江景王座特邀邱德光先生倾力加盟，根据户型及景观面度身定制打造了四大精装样本，充分运用华丽、艺术、时尚元素以及接轨世界的巴洛克、Art Deco风格，塑造符合全球顶级人士尊贵身份的作品。首批Art Deco样板间开放首日，就吸引了千人的热情品鉴，销售业绩一路高涨，引发上海豪宅市场的高度关注，开盘当月销售金额就突破了亿。根据网上房地产相关数据，绿城·盛世滨江2014年以网签金额21亿的成绩稳居上海6万以上豪宅产品销售冠军。绿城·盛世滨江江景王座8月公开之后，9-10月份，陆续上海中心城区有多个滨江豪宅项目力邀邱德光先生加盟，业内甚至戏言，上海滨江豪宅进入了所谓“邱德光时间“。“作豪宅室内设计，最关键的就是帮客户把艺术在室内进行还原，让艺术家的感性与设计师的理性巧妙地融合在一起。而在这里，我让时尚·中国·艺术三大元素贯穿在绿城·盛世滨江室内的各个细节，让客户自然地被其感动。”“不同于之前的基调，这次在绿城·盛世滨江，我的设计语言更偏年轻化个性化，更符合目前豪宅客户发展的趋势。这是我非常满意的“邱德光甚至表示，无论是中国大陆，还是中国台湾，这可能是我所有作品里，我自己最想居住的地方。”发布会现场，绿城·盛世滨江项目总经理王喆先生表示，绿城·盛世滨江是融创绿城在上海最重要的项目之一，其本身外滩土地价值就不可估量，而这次邱大师的作品完美还原了土地的景观资源及文化艺术价值，达到了豪宅专家融创绿城最初的预期。据悉，本次发布会也宣告了邱德光定制的绿城·盛世滨江全新220-265平环幕江景大宅的公开，申城豪宅销冠2014年最后2个月的收官成绩无疑将引发业内的极大关注。 【项目二】：上海融创 盛世滨江 2501【设计者】：邱德光【参与者】： 杨尹赢、陈立筠【空间性质】：住宅【坐落位置】：上海市黄浦区中山南一路500弄【主要材料】：黑檀木皮、橡木染灰木皮、银白龙石材、珊瑚海石材、镀钛不锈钢、烤漆、明镜【面 积】：149㎡'
    texts = """2014年3月，深圳国际家具展，“德光居 HOME”惊世亮相，一时间引起行业轰动。这个由台湾著名设计师邱德光先生亲自操刀设计的家具品牌一经推出受到家具业普遍关注。笑称是“被逼”出来的 HOME，以其独创的Neo-Art Deco东方美学风格结合时尚观察，打造出中国第一个具备国际视野的精品家具品牌。被誉为新装饰主义neo-art deco东方美学风格的创始人邱德光先生一直致力于中国顶级豪宅设计，参与两岸许多高级室内设计案与建筑公共区域的规划案，在华人经济圈室内设计领域具有绝对的影响力。今天干货君独家年度回顾的正是邱德光设计师事务所2014年年度代表作――盛世滨江四大样板间，这个被他称为“自己最想居住的地方”。而这四大样板间最大的特点就是“德光居 HOME”在这里成了主角。干货君独家奉送，作为新年礼物呈现给大家。【项目一】：上海融创 盛世滨江 2101【设计者】：邱德光【参与者】： 刘琼文、林纯萱【空间性质】：住宅【坐落位置】：上海市黄浦区中山南一路500弄【主要材料】：圣罗兰黑金石材、新法国米黄石材、雅士白石材、仿古明镜、仿古银箔、古铜金箔、黑檀木皮、烤漆板、镀钛不锈钢、烤漆玻璃、特殊壁纸【面 积】： 211O【设计时间】： 2013 年 9月至 2014 年 8 月【施工时间】： 2014 年 7月至 2014 年 9 月"""

    print(pinfo.extract(texts))

    save_dir = "output/project_info2"
    run_zm_dataset(save_dir)



