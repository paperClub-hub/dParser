#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-11-08 17:49
# @Author   : NING MEI
# @Desc     :



from uie_predictor import UIEPredictor


base_schema = [
    "项目名称","业主单位", "项目地址", "设计风格", "项目面积", "项目造价", "项目设计",  "空间性质",
    "建筑设计", "硬装设计", "建筑设计", "设计主创", "设计总监",  "施工单位","参与设计", "设计时间",
    "完工时间","主要材料"
]

MODEL = None
if MODEL is None:
    MODEL = UIEPredictor(model='./uie-base',
                        device='gpu',
                        use_fp16 = True,
                        schema=base_schema)




if __name__ == '__main__':
    text = """Houses, London, United Kingdom
面积：  45 m²
年份：2020
建造商： DCW EDITIONS, Bert Frank, Claybrook, Diespeker, Dyke & Dean, Fakktory, Stuart Indge
Construction :H Quality Construction Ltd
Having decided to grow their family, the owners of the Glyn House were lacking a large open plan area where everyone can be together and enjoy the garden views. Our studio was therefore asked to rethink the rear part of their Victorian property, where the kitchen was located, and produce a large space that fits a variety of everyday activities while keeping a connection to the front living area of the house. That connection proved to be the biggest challenge of the project, as we dealt with a seven-step drop of levels between the living and kitchen areas while figuring ways of concealing a maze of plumbing pipes that surrounded the existing rear facade. The design solution took the form of an elongated capsule window with a stepped cill outlining its shape and hiding the building’s functional elements in its void.
A large skylight cuts the capsule win-dow in half and establishes a connection to the living area through the bottom half and cross ventilation of the space through the top. The generously glazed strip continues along the entire space bringing in ample natural light and wraps around the facade, creating a cosy daybed with tall uninterrupted views of the garden. The kitchen, dining, and daybed areas are all given a separate unforced presence inside the new space, taking into consideration their usability and the various functions of family life. It is clear that our studio’s proposal focuses on natural light and quality of space, but another major factor of our usual design process is materiality. A minimal facade with brutalist influences features vertical polished plaster pillars connected with black concrete panels and a pale brick floor stepping down towards the garden.
The capsule window also reflects in its shape those brutalist tendencies, but the stained oak timber of its frame reveals a softer approach to the design. Elements of the facade such as the pale bricks and the grey polished plaster are brought inside and are paired with warm oak carpentry, sand-colored plaster, and brass in a deliberate attempt to have the interior represent a more private version of the same architecture. Black volumes such as the bespoke terrazzo kitchen island and the dining unit, together with the white ceiling throughout the space are designed to provide the necessary contrast against the palette of natural materiality and therefore intensify the experience of raw, handmade surfaces. The result is a bright, spacious, and unique addition to a traditional property that connects the space to its landscape and celebrates the craftsmanship of its materiality.
项目完工照片 | Finished Photos"""

    res = MODEL(text)
    print(res)