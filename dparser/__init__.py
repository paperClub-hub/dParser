#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-20 11:54

"""dparser：对百度ddParser(v1.0.6)重构
"""

name = 'dparser'
version = "0.0.2"
version_info = (0, 0, 2)

from .run import DDParser
from .extract.kextract import text2words
from .extract.dextract import FineGrainedInfo, ddrelation
from .extract.pextract import CASE_INFO
from .extract.uextract import uie


case_info = CASE_INFO()
