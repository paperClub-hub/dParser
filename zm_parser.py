#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-10-20 14:28
# @Author   : NING MEI
# @Desc     :



import os
import json
import time
from dparser import case_info
from dparser.utils.util import *
from dparser.utils.process import *
from dparser import ddrelation
from dparser import text2words
from dparser import uie


def demo():
    text = """邱德光畅谈绿城·盛世滨江四重空间所演绎的艺术生活“因为深知黄浦江与外滩对于上海这座城市的意义，所以在设计绿城·盛世滨江这样一线江景豪宅时，我们力图将最大的手笔留给滨江的视野。让室内、室外空间浑然天成，让客户透过270°的视角，感受最极致的江景。这是我的设计初衷，也是对黄浦江的敬意。”——邱德光2014年10月24日，一场以“巨匠·境界——邱德光畅谈滨江艺术人居”为主题的发布会在位于外滩世博滨江板块内的绿城·盛世滨江盛大召开。众多业内、媒体及文化艺术人士齐聚现场，与邱德光先生一同探讨申城滨江豪宅生活及设计理念。被誉为“新装饰主义大师”、“台湾设计界领军人物”的邱德光先生，纵横业界三十多年，专注室内空间中艺术细节和整体氛围的呈现，在世界各地均有知名豪宅项目由其设计打造。其中绿城·盛世滨江坐拥外滩一线江景，其于2014年8月起陆续推出的江景王座特邀邱德光先生倾力加盟，根据户型及景观面度身定制打造了四大精装样本，充分运用华丽、艺术、时尚元素以及接轨世界的巴洛克、Art Deco风格，塑造符合全球顶级人士尊贵身份的作品。首批Art Deco样板间开放首日，就吸引了千人的热情品鉴，销售业绩一路高涨，引发上海豪宅市场的高度关注，开盘当月销售金额就突破了亿。根据网上房地产相关数据，绿城·盛世滨江2014年以网签金额21亿的成绩稳居上海6万以上豪宅产品销售冠军。绿城·盛世滨江江景王座8月公开之后，9-10月份，陆续上海中心城区有多个滨江豪宅项目力邀邱德光先生加盟，业内甚至戏言，上海滨江豪宅进入了所谓“邱德光时间“。“作豪宅室内设计，最关键的就是帮客户把艺术在室内进行还原，让艺术家的感性与设计师的理性巧妙地融合在一起。而在这里，我让时尚·中国·艺术三大元素贯穿在绿城·盛世滨江室内的各个细节，让客户自然地被其感动。”“不同于之前的基调，这次在绿城·盛世滨江，我的设计语言更偏年轻化个性化，更符合目前豪宅客户发展的趋势。这是我非常满意的“邱德光甚至表示，无论是中国大陆，还是中国台湾，这可能是我所有作品里，我自己最想居住的地方。”发布会现场，绿城·盛世滨江项目总经理王喆先生表示，绿城·盛世滨江是融创绿城在上海最重要的项目之一，其本身外滩土地价值就不可估量，而这次邱大师的作品完美还原了土地的景观资源及文化艺术价值，达到了豪宅专家融创绿城最初的预期。据悉，本次发布会也宣告了邱德光定制的绿城·盛世滨江全新220-265平环幕江景大宅的公开，申城豪宅销冠2014年最后2个月的收官成绩无疑将引发业内的极大关注。 【项目二】：上海融创 盛世滨江 2501【设计者】：邱德光【参与者】： 杨尹赢、陈立筠【空间性质】：住宅【坐落位置】：上海市黄浦区中山南一路500弄【主要材料】：黑檀木皮、橡木染灰木皮、银白龙石材、珊瑚海石材、镀钛不锈钢、烤漆、明镜【面 积】：149㎡"""
    data = []
    project_info = case_info.extract(text)
    # depency_res = ddrelation(text, True)
    keywords = text2words(text)
    relation_items = uie_postprocess(uie.cusom_extract(text, schema=templates['uie_task']))
    wordtag_items = []
    for t in text.split("\n"):
        wtag_res = uie.wordtag_extract(t)
        if wtag_res["pos_items"] and wtag_res["wordtag_rel"]:
            wordtag_items.append(wtag_res)

    data.append({
        "project_info": project_info,
        "keywords": keywords,
        "relation_items": relation_items,
        "wordtag_items": wordtag_items
    })

    print(data)


def spliter(doc_texts):
	all_texts = []
	max_lenght = 512
	_texts = []
	doc_texts = doc_texts.split("。")

	for i, text in enumerate(doc_texts):
		if len("".join(_texts)) <= max_lenght:
			_texts.append(text)
		else:
			all_texts.append(_texts)
			_texts = []
			_texts.append(text)

		if i == len(doc_texts) - 1 :
			all_texts.append(_texts)

	all_texts = [x for x in all_texts if "".join(x)]
	return all_texts


if __name__ == '__main__':
	print()

	from tqdm.auto import tqdm
	zm_data = load_json("dparser/demo/zhimo_all.json")

	for i, doc in tqdm(enumerate(zm_data)):
		start = time.time()
		url = doc.get('url')
		doc_txts = [d.get('txt') for d in doc.get('medias')  if d.get('txt') ]
		if doc_txts:

			doc_keywords = []
			doc_project_info = []
			doc_relation_items = []
			wordtag_items = []
			if len("\n".join(doc_txts)) > 500:
				split_doc_txts = spliter("\n".join(doc_txts))

				# print(split_doc_txts)

				for j, txts in enumerate(split_doc_txts):
					# print("txts: ", txts)
					if not txts:
						continue
					project_info = case_info.extract("。".join(txts))
					doc_project_info.append(project_info)
					keywords = text2words("。".join(txts))
					doc_keywords.append(keywords)
					relation_items = uie_postprocess(uie.cusom_extract("。".join(txts), schema=templates['uie_task']))
					doc_relation_items.append(relation_items)
					for txt in txts:
						if not txt:
							continue
						wordtag_res = uie.wordtag_extract(txt)
						if wordtag_res["pos_items"] and wordtag_res["wordtag_rel"]:
							wordtag_items.append(wordtag_res)

				data = {
				    "url": url,
				    "project_info": doc_project_info,
				    "keywords": doc_keywords,
				    "relation_items": doc_relation_items,
				    "wordtag_items": wordtag_items,
				    "time_cost": time.time() - start
				    }

				print("data: ", data)
				print(json.dumps(data, indent=True, ensure_ascii=False), file=open(f"dparser/demo/result/{i}.json", 'w'))

            # if len("\n".join(doc_txts)) > 500:
            #     continue

            # project_info = case_info.extract("\n".join(doc_txts))
            # keywords = text2words("\n".join(doc_txts))
            # relation_items = uie_postprocess(uie.cusom_extract("\n".join(doc_txts), schema=templates['uie_task']))
            # wordtag_items = []
            # for txt in doc_txts:
            #     wordtag_res = uie.wordtag_extract(txt)
            #     if wordtag_res["pos_items"] and wordtag_res["wordtag_rel"]:
            #         wordtag_items.append(wordtag_res)
            #
            # data = {
            #     "url": url,
            #     "project_info": project_info,
            #     "keywords": keywords,
            #     "relation_items": relation_items,
            #     "wordtag_items": wordtag_items,
            #     "time_cost": time.time() - start
            #     }
            #
            #
            # print(json.dumps(data, indent=True, ensure_ascii=False), file=open(f"dparser/demo/result/{i}.json", 'w'))





