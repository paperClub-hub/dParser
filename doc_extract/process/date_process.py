#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-12-22 13:53
# @Author   : NING MEI
# @Desc     :

###########################################################
#   日期过滤与归一化处理: 基于规则的归一化处理
###########################################################


import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List
from zhdate import ZhDate as lunar_date


class date_parser():

	def __init__(self):

		self.month_dict, self.day_dict, self.year_char2num_map = self.datetime_unit()

	def datetime_unit(self):
		""" 日期键值对映射 """

		# 汉字数字映射
		YEAR_CHAR2NUM_MAP = {'零': '0', '〇': '0', '一': '1', '二': '2', '三': '3', '四': '4',
		                     '五': '5', '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'}

		# 英文 month映射
		month_dict = {'January': '1', 'Jan.': '1', 'February': '2', 'Feb.': '2', 'March': '3', 'Mar.': '3',
		              'April': '4', 'Apr.': '4', 'May': '5', 'May.': '5', 'June': '6', 'Jun.': '6',
		              'July': '7', 'Jul.': '7', 'August': '8', 'Aug.': '8', 'September': '9', 'Sep.': '9', 'Sept.': '9',
		              'October': '10', 'Oct.': '10', 'November': '11', 'Nov.': '11', 'December': '12', 'Dec.': '12',
		              'may': '5'
		              }

		# 英文节日与月份映射
		_festival_to_month_map = {'Christmas': '12', "New Year’s Day": '1', "NewYear'Day": '1', 'May Day': '5',
		                          "International Workers' Day": '5'}

		month_dict.update(_festival_to_month_map)

		# 英文 day映射
		_day_dict = {'1st': '1', '21st': '21', '31st': '31', '2nd': '2', '22nd': '22', '3rd': '3', '23rd': '23'}
		DAY_DICT = dict([str(x), str(x)] for x in range(1, 32))
		DAY_DICT.update(_day_dict)
		DAY_DICT.update(dict([f"{i}th", str(i)] for i in range(1, 32) if str(i) not in list(_day_dict.values())))
		# day顺序：先英文day，再纯数字day
		DAY_DICT = dict(sorted(DAY_DICT.items(), key=lambda d: len(d[0]), reverse=True))

		# 创建月份大字典
		MONTH_DICT = defaultdict(list)
		for k, vs in month_dict.items():
			if k not in MONTH_DICT:
				MONTH_DICT.update({k: month_dict.get(k)})
			if k.upper() not in MONTH_DICT:
				MONTH_DICT.update({k.upper(): month_dict.get(k)})
			elif k.lower() not in MONTH_DICT:
				MONTH_DICT.update({k.lower(): month_dict.get(k)})

		del month_dict, _day_dict

		return MONTH_DICT, DAY_DICT, YEAR_CHAR2NUM_MAP



	def chinese_dtime_preNormalization(self, strs: str):
		"""
		殊特型纯中文日期转归一化处理: 如，'二零二一年一月' >>> '2022年1月1日'
		eg:
			'二〇二二年十二月三十一日'， '二〇二二年正月月初二'， '二零二一年元月'

		Args:
			strs:

		Returns:

		"""


		def _cn_preprocess(strs: str, to_lunar: bool = False):
			""" 汉字年月日转化 """
			# 纯转化可参考：https://blog.csdn.net/qq_35332332/article/details/123881533

			_year, _month, _day = '', '', ''

			# 字符串替换
			if '月份' in strs:
				strs = strs.replace('月份', '月')
			if '腊月' in strs:
				strs = strs.replace('腊月', '十二月')
			if ('元月' in strs) or ('正月' in strs):
				strs = strs.replace('腊月', '一月').replace('正月', '一月')
			if ('农历' in strs) or ('阴历' in strs) or ('初' in strs):
				strs = strs.replace('农历', '').replace('阴历', '').replace('初', '')
			if ('号' in strs) or ('號' in strs):
				strs = strs.replace('号', '日').replace('號', '日')
			if ('月' in strs) and ('日' not in strs) and (strs.index('月') < len(strs) - 1):
				strs += '日'


			# 条件：有年月日等字段
			if any([i in strs for i in ['年', '月', '日']]):

				if all(i in strs for i in ['年', '月', '日']):
					_year, _month, _day, _ = re.split('[年|月|日]', strs)

				elif all(i in strs for i in ['年', '月']):
					_year, _month, _ = re.split('[年|月]', strs)

				elif '年' in strs:
					_year, _ = re.split('年', strs)

				if len(_day) >= 3: # 如，二十二
					_day = _day[0] + _day[2]


				_year = ''.join([self.year_char2num_map.get(i) for i in _year if i in self.year_char2num_map]) if _year else ''
				_month = ''.join([self.year_char2num_map.get(i) for i in _month if i in self.year_char2num_map]) if _month else ''
				_day = ''.join([self.year_char2num_map.get(i) for i in _day if i in self.year_char2num_map]) if _day else ''

				if len(_month) == 3:
					_month = _month[0] + _month[2]
				if len(_day) == 3:
					# 如，二十二 =>>> 2 10 2
					_day = _day[0] + _day[2]


			if to_lunar:
				# 农历转阳历
				if all([i.isdigit() for i in [_year, _month, _day]]):  # 年月日
					try:
						return lunar_date(int(_year), int(_month), int(_day)).to_datetime().strftime('%Y-%m-%d')
					except:
						return ''
				elif all([i.isdigit() for i in [_year, _month]]):  # 年月
					try:
						return lunar_date(int(_year), int(_month), 1).to_datetime().strftime('%Y-%m')
					except:
						return ''
				else:
					return ''
			else:
				if _year:
					_year += '年'
				if _month:
					_month += '月'
				if _day:
					_day += '日'
				return ''.join(list(filter(bool, [_year, _month, _day])))


		# 中文日期规则
		cn_char_reg = '(一|二|三|四|五|六|七|八|九|零|十|〇|○|0)'

		# 阳历中文日期
		ymd_cn_reg = ''.join([
			'(([12]?\d{2,3})|', cn_char_reg, '{4})(\s)?(年)?(上|下)?((半)?年)?',  # 年
			'(', cn_char_reg, '{1,2})?(月(份)?)?'  # 月
			                  '(', cn_char_reg, '{1,3})?(日|号)?'  # 日
			])

		# 农历中文日期
		ymd_lu_reg = ''.join([
			'(((', cn_char_reg, '{4})[\s]?(年))[\s]?',  # 年
			'(((农|阴)?历)?[\s]?((元|正|腊)?月)|', cn_char_reg, '{1,2}(月|大年)?)[\s]?',  # 月
			'((初)?', cn_char_reg, '{1,3}[\s]?(日)?)?[\s]?)'
		])


		norm_dtime_str = ''
		_lu_datatime_str = re.search(ymd_lu_reg, strs, re.IGNORECASE)
		_cn_datetime_str = re.search(ymd_cn_reg, strs, re.IGNORECASE)

		if any([i in strs for i in ['正月', '元月', '腊月', '初', '大年', '农历', '阴历']]):
			# 农历年月日处理
			if _lu_datatime_str:
				_lu_datatime_str = _lu_datatime_str.group()
				_lu_datatime_str = _cn_preprocess(_lu_datatime_str, to_lunar=True)
				if _lu_datatime_str:
					norm_dtime_str = _lu_datatime_str

		elif _cn_datetime_str:
			_cn_datetime_str = _cn_datetime_str.group()
			_cn_datetime_str = _cn_preprocess(_cn_datetime_str, to_lunar=False)
			if _cn_datetime_str:
				norm_dtime_str = _cn_datetime_str

		del _lu_datatime_str, _cn_datetime_str

		return norm_dtime_str




	def numeric_dtime_preNormalization(self, strs):
		"""
		殊特型纯数值型殊特时间格式归一化处理:
		eg:
			1. '2019-06-09 15:00:50' 或 '2019/06/09 15:00:50';
			2. ‘17-03-21’，‘17.03.21’
			3. ‘2022 09 12’, ‘2022 09 ’, ' 2012 09', 不考虑‘22 09 12’的情况

		Args:
			strs:

		Returns:

		"""


		def _number_timestamp_preprocess(strs, ymd_reg):
			""" 时间戳格式处理, '2019-06-09 15:00:50' 或 '2019/06/09 15:00:50';
			"""
			_dt_datetime_str = ''
			_datetime_str = re.search(ymd_reg, strs)
			if _datetime_str:
				_datetime_str = _datetime_str.group().replace(' ', '')

				try:
					_dt_datetime_str = datetime.strptime(_datetime_str, '%Y-%m-%d%H:%M:%S').strftime('%Y-%m-%d')
				except:
					try:
						_dt_datetime_str = datetime.strptime(_datetime_str, '%Y/%m/%d%H:%M:%S').strftime('%Y-%m-%d')
					except:
						pass

				del _datetime_str

			return _dt_datetime_str


		def _number_sigin_preprocess(strs, ymd_reg):
			""" 短数字 + 分隔符格式日期 处理: ‘17-03-21’，‘17.03.21’
			"""

			_dt_datetime_str = ''

			_spliter = '-|/|\.'
			_datetime_str = re.search(ymd_reg, strs)

			if _datetime_str:
				strs = strs.replace(' ', '')
				_year = re.split(f'[{_spliter}]', strs)[0]
				_others = "-".join(re.split(f'[{_spliter}]', strs)[1:])

				if len(_year) == 2:
					if _year.startswith('0') or _year.startswith('1') or _year.startswith('2'):
						_year = '20' + _year
						_dt_datetime_str = '-'.join([_year, _others])

					elif _year.startswith('9') or _year.startswith('8') or _year.startswith('7') \
							or _year.startswith('6') or _year.startswith('5') or _year.startswith('4') \
							or _year.startswith('3'):
						_year = '19' + _year
						_dt_datetime_str = '-'.join([_year, _others])

			del _datetime_str

			return _dt_datetime_str


		def _number_blank_preprocess(strs, ymd_reg):
			"""
			数字 + 空格格式日期 处理: ‘2022 09 12’, ‘2022 09 ’, 不考虑‘22 09 12’的情况
			"""

			_dt_time_str = ''

			_num_blank_str = re.search(ymd_reg, strs)
			if _num_blank_str:
				_num_blank_str = _num_blank_str.group().split()

				if len(_num_blank_str[0]) == 4: # 年4位数字
					_year, _month, _day = '', '', ''

					if len(_num_blank_str) == 2:  # 年月
						_year = _num_blank_str[0]
						_month = _num_blank_str[1]
						_dt_time_str = f"{_year}年{_month}月"

					elif len(_num_blank_str) == 3:  # 年月日
						_year = _num_blank_str[0]
						_month = _num_blank_str[1]
						_day = _num_blank_str[2]
						_dt_time_str = f"{_year}年{_month}月{_day}日"

			del _num_blank_str

			return _dt_time_str


		### 特殊型纯数字日期
		# 时间戳日期规则及纯数值日期: '2019-06-09 15:00:50' 或 '2019/06/09 15:00:50'
		_num_char_reg1 = r'(([12]?\d{2,3})(\-|/)?([0]?\d|1[012])(\-|/)?([012]?\d|3[01])(\s)?([0-1]?[0-9]|2[0-3])(\:)([0-5][0-9])(\:)([0-5][0-9])[\s]?)$'
		# 短数字日期格式：‘17-03-21’，‘17.03.21’，
		# _num_char_reg2 = r'(([12]?\d{2,3})(\s)?(\s|-|/)?([0]?\d|1[012])?(\s)?(\s|-|/)?([012]?\d|3[01])?(\s)?)'
		_num_char_reg2 = r'(^(\d{2})(\s)?(-|/|\.)([0]?\d|1[012])?(\s)?(-|/|\.)([012]?\d|3[01])?(\s)?)$'
		# 仅包括空格的纯数字日期：‘2022 09 12’, ‘2022 09 ’, ' 2012 09', 不考虑‘22 09 12’的情况
		_num_char_reg3 = r'(^([\s]?[12]?\d{3})[\s](([0]?\d|1[012])[\s])(([012]?\d|3[01])[\s]?)?)$'
		_num_char_reg3 += '|(^([\s]([12]?\d{3})[\s])(([0]?\d|1[012])[\s]?))$'

		ymd_num_reg = '|'.join([_num_char_reg1, _num_char_reg2, _num_char_reg3])
		_dt_datetime_str = re.search(ymd_num_reg, strs, re.IGNORECASE)

		norm_dtime_str = ''
		if _dt_datetime_str:
			_numstamp_match_str = _number_timestamp_preprocess(strs, _num_char_reg1)
			_numsign_match_str = _number_sigin_preprocess(strs, _num_char_reg2)
			_numblank_match_str = _number_blank_preprocess(strs, _num_char_reg3)

			if _numstamp_match_str:
				norm_dtime_str = _numstamp_match_str
			elif _numsign_match_str:
				norm_dtime_str = _numsign_match_str
			elif _numblank_match_str:
				norm_dtime_str = _numblank_match_str

			del _numstamp_match_str, _numsign_match_str, _numblank_match_str

		return norm_dtime_str



	def chinese_numeric_preNormalization(self, strs):
		"""
		特殊型中文+数字组合型日期归一化：
		eg:
			1. 06年, '09年4月', 09年度4月4号'
			2. '2020年下半年', '2022上半年', 22年上半年', '2022年度下半年', '2022年年末', '22年初'
			3. '1980年代'

		Args:
			strs:

		Returns:

		"""


		# 1. 06年, '09年4月', 09年度4月4号'
		reg1 = '(^(\d{2})[\s]?(年(度)?)[\s]?(([0]?\d|1[012])(月(份)?))?[\s]?(([012]?\d|3[01])(日|号))?[\s]?)$'

		# 2. '2020年下半年', '2022上半年', 22年上半年', '2022年度下半年', '2022年年末', '22年初'
		# reg2 = '(^([12]?\d{2,3})[\s]?((年(度)?)?(上|下)半年)[\s]?)$'
		reg2 = '(^([12]?\d{2,3})[\s]?(((年(度)?)?((上|下)半年))|((年)?年(末|中|终|初)))[\s]?)$'

		# 3. '1980年代'
		reg3 = '(^([12]?\d{2,3})[\s]?(年代)[\s]?)$'



		_dt_match_str1 = re.search(reg1, strs)
		_dt_match_str2 = re.search(reg2, strs)
		_dt_match_str3 = re.search(reg3, strs)

		norm_dtime_str = ''
		if _dt_match_str1:
			_dt_match_str = _dt_match_str1.group().replace(" ", '')

			if ('年度' in _dt_match_str) or ('月份' in _dt_match_str) or ('号' in _dt_match_str):
				_dt_match_str = _dt_match_str.replace('年度', '年').replace('月份', '月').replace('号', '日')

			_year = _dt_match_str.split('年')[0]
			_others = _dt_match_str.split('年')[1]

			if len(_year) == 3:
				_year = ''
			elif len(_year) == 2:
				if _year.startswith('0') or _year.startswith('1') or _year.startswith('2'):
					_year = '20' + _year
				elif _year.startswith('9') or _year.startswith('8') or _year.startswith('7') \
						or _year.startswith('6') or _year.startswith('5') or _year.startswith('4') \
						or _year.startswith('3'):
					_year = '19' + _year

			if _year:
				norm_dtime_str = f"{_year}年{_others}" if _others else f"{_year}年"

			del _year, _others


		elif _dt_match_str2:
			_dt_match_str2 = _dt_match_str2.group().replace(" ", '')

			_year = re.findall('^([12]?\d{2,3})', _dt_match_str2)[0]
			if _year:
				if len(_year) == 3:
					_year = ''

				elif len(_year) == 2:
					if _year.startswith('0') or _year.startswith('1') or _year.startswith('2'):
						_year = '20' + _year

					elif _year.startswith('9') or _year.startswith('8') or _year.startswith('7') \
							or _year.startswith('6') or _year.startswith('5') or _year.startswith('4') \
							or _year.startswith('3'):
						_year = '19' + _year

			_month = ''
			if '上半年' in _dt_match_str2:
				_month = '6月'
			elif '下半年' in _dt_match_str2:
				_month = '12月'
			elif '年初' in _dt_match_str2:
				_month = '1月'
			elif '年中' in _dt_match_str2:
				_month = '6月'
			elif '年终' in _dt_match_str2:
				_month = '12月'
			elif '年末' in _dt_match_str2:
				_month = '12月'

			if _year and _month:
				norm_dtime_str = f"{_year}年{_month}"

			del _year, _month


		elif _dt_match_str3:
			_dt_match_str3 = _dt_match_str3.group().replace(" ", '')

			_year = re.findall('^([12]?\d{2,3})', _dt_match_str3)[0]
			if len(_year) == 4:
				norm_dtime_str = f"{_year}年"

		del _dt_match_str1, _dt_match_str2, _dt_match_str3

		return norm_dtime_str




	def  dtime_normalization(self, strs):
		"""
		通用日期归一化入口：
		eg:
			1. 标准格式：匹配‘2021年6月1日’，或‘2021年6月’，‘2021年’或‘2021’，‘20210601’，‘202106’
			2. 英文日月年或月年：匹配'12th SEPTEMBER 2015', 'SEPTEMBER 2015', '18 December 2022'
		Args:
			strs:

		Returns:

		"""

		def _std_time_normalize(strs: str) -> str:
			#  标准时间归一化处理
			ymd_reg = r'[\d]+'
			year, month, day = '', '', ''

			res = re.findall(ymd_reg, strs, re.IGNORECASE)
			if len(res) == 1:  # 纯数字，如20221201，202261
				res = res[0]
				year = res[:4]
				if len(res) > 4:
					if int(res[4:6]) <= 12:
						month = res[4:6]
						day = res[6:]
					else:
						month = res[4:5]
						day = res[5:]

			elif len(res) >= 2:  # 含有其他分割符
				year = res[0][:4]
				month = res[1]
				if len(res) == 2:
					if len(year) == 2:  # 22 09 等情况需要剔除
						year = ''
						month = ''

				elif len(res) > 2:
					day = res[-1]
					if len(year) == 2:  # 22 09 09 等情况需要剔除
						year = ''
						month = ''
						day = ''

			if year:
				year += '年'
			if month:
				month += '月'
			if day:
				day += '日'

			del res

			norm_dtime_str = ''.join(list(filter(bool, [year, month, day])))

			return _ymd_formator(norm_dtime_str)


		def _ymd_formator(strs: str):
			""" 转为公历日期标准格式, 如2021年2月6日
			"""


			if strs:
				res = re.split('[年|月|日]', strs)

				try:
					y, m, d = '', '', ''
					if len(res) == 4:
						y = str(int(res[0])) + '年'
						m = str(int(res[1])) + '月'
						d = str(int(res[2])) + '日'

					elif len(res) == 3:
						y = str(int(res[0])) + '年'
						m = str(int(res[1])) + '月'

					elif len(res) == 2:
						y = str(int(res[0])) + '年'

					return ''.join(list(filter(bool, [y, m, d])))

				except Exception as error:
					return strs

			else:
				return strs



		# 英文月份、日
		month_dict = self.month_dict
		day_dict = self.day_dict
		mo_ens = '|'.join(list(month_dict.keys()))
		da_ens = '|'.join(list(day_dict.keys()))

		# 校验规则：
		# 标准格式：匹配‘2021年6月1日’，或‘2021年6月’，‘2021年’或‘2021’，‘20210601’，‘202106’
		# standard_reg = r'(^(?:19|20)\d{2}(年(度)?|\.|-|/)?(([0]?\d|1[012])(月(份)?|\.|-|/)?)?(([012]?\d|3[01])(日|号)?)?)$'
		# standard_reg = r'(^(?:19|20)\d{2}(\s)?(年(度)?|\.|-|/)?(([0]?\d|1[012])(月(份)?|\.|-|/)?)?(([012]?\d|3[01])(日|号)?)?)$'
		standard_reg = r'(^[12]?\d{2,3}(\s)?(年(度)?|\.|-|/)?(([0]?\d|1[012])(月(份)?|\.|-|/)?)?(([012]?\d|3[01])(日|号)?)?)$'

		# 英文日月年或月年：匹配'12th SEPTEMBER 2015', 'SEPTEMBER 2015', '18 December 2022'
		dmy_en_reg = '((' + da_ens + ')?[\s]?(' + mo_ens + ')[\s]?(' + '\d{4})' + ')'
		# 英文年月日或年月：匹配'2015 SEPTEMBER 12th'，
		ymd_en_reg = '(' + '(\d{4})[\s]?(' + mo_ens + ')[\s]?(' + da_ens + ')?)'

		# 规格化处理
		norm_dtime_str = ''
		standard_res = re.search(standard_reg, strs, re.IGNORECASE)
		dmy_en_res = re.search(dmy_en_reg, strs)
		ymd_en_res = re.search(ymd_en_reg, strs)

		if standard_res:  # 标准年月日
			norm_dtime_str = _std_time_normalize(strs)
		else:
			if dmy_en_res:  # 英文日月年
				res = re.findall(dmy_en_reg, strs, re.IGNORECASE)
				if res:
					res = res[0][1:]
					_day = day_dict.get(res[0], '') if res[0] else ''
					_month = month_dict.get(res[1], '') if res[1] else ''
					_year = re.findall(r'\d{4}', strs)[0]
					en_date = '-'.join(list(filter(bool, [_year, _month, _day])))
					norm_dtime_str = _std_time_normalize(en_date)
					del _day, _month, _year

			elif ymd_en_res:  # 英文年月日
				res = re.findall(ymd_en_reg, strs, re.IGNORECASE)
				if res:
					res = res[0][1:]
					_year = re.findall(r'\d{4}', strs)[0]
					_month = month_dict.get(res[1], '') if res[1] else ''
					_day = day_dict.get(res[-1], '') if res[-1] else ''
					en_date = '-'.join(list(filter(bool, [_year, _month, _day])))
					norm_dtime_str = _std_time_normalize(en_date)
					del _day, _month, _year

		del standard_res, dmy_en_res, ymd_en_res

		return norm_dtime_str



	def process(self, strs):
		"""
		时间处理总入口
		Args:
			strs:

		Returns:

		"""

		# 1. 规则表达式
		# 英文月格式
		mo_ens = '|'.join(list(self.month_dict.keys()))

		# 年月日格式
		ye_n = '(([12]?\d{2,3})|(一|二|三|四|五|六|七|八|九|零|〇|○|0){4}?)'  # 年份数字格式
		mo_n = '([0]?\d|1[012])'  # 月份数字格式
		mo_c = '(元|正|腊|一|二|三|四|五|六|七|八|九|十(一|二)?)'  # 月份汉字格式
		da_n = '([012]?\d|3[01])(th|nd|st|rd)?'  # 日数字格式
		ymd_n = r'(^(?:17|18|19|20)\d{2}' + '(\d{1,2})?' + '(\d{1,2})?)'  # 纯数窜字年月日或年月(20221219, 2022)
		ymd_gap = '[\-\~— ～\.\/]{1,2}'  # 年跨度格式

		# 组合年月日规则
		ymd_pattern_1 = '(' + ye_n + '[\s]?((上|下)半)?年(初|底|末|度|代|(上|下)半年)?)((' + mo_n + '|' + mo_c + ')月(份|底|初)?)?(' + da_n + '[日号])?'  # 带中文格式的年月日
		# ymd_pattern_2 = '^(' + ye_n + ymd_gap + mo_n + '(' + ymd_gap + da_n + ')?)$' # 数值年月日格式或年月格式
		# ymd_pattern_2 = '^(' + ye_n + ymd_gap + mo_n + '(' + ymd_gap + da_n + ')?)$|(' + ymd_n + ')'  # 数值年月日格式或年月格式
		ymd_pattern_2 = '^(' + ye_n + ymd_gap + mo_n + '(' + ymd_gap + da_n + ')?)$'  # 数值年月日格式或年月格式
		# ymd_pattern_2 = '(' + ye_n + '(' + ymd_gap + ')?' + mo_n + '(' + '(' + ymd_gap + ')(' + da_n + ')?))|(' + ye_n + ')'  # 纯数值年月日格式或年月格式
		ymd_pattern_3 = '((' + da_n + '[\s])?(' + mo_ens + ')[\s](' + ye_n + '))$'  # 英文日月年格式，或月年格式
		# ymd_pattern_4 = '((' + ye_n + '[\s]?(Year)?(' +  mo_ens + ')[\s]?)(' + da_n + ')?)$' # 英文年月日格式，或年月格式
		ymd_pattern_4 = '((' + ye_n + '[\s]?(Year)?(' + mo_ens + ')[\s]?)(' + da_n + ')?)'  # 英文年月日格式，或年月格式
		ymd_pattern_5 = '(' + '(([12]?\d|(二)?十(一|二|三|四|五|六|七|八|九)?)世纪)?((\d0|(一|二|三|四|五|六|七|八|九)十)年代)?(初|末)?' + ')$'  # 世纪，年代
		season_pattern = '((春|夏|秋|冬){1,2}(季|天|日)|(第)?(一|二|三|四)(季度)(末)?)'

		# 各类型时间规则汇总
		reg = r'(' + '|'.join([ymd_pattern_1, ymd_pattern_2, ymd_pattern_3, ymd_pattern_4, ymd_pattern_5, ymd_n,
		                       season_pattern]) + ')'

		# 2. 特殊格式日期预处理： 纯中文
		if not re.findall(r'\d+', strs):
			# print("纯中文日期 .... ")
			special_cn_dtime_strs = self.chinese_dtime_preNormalization(strs)
			if special_cn_dtime_strs:
				strs = special_cn_dtime_strs


		# 3. 特殊格式日期预处理： 纯数字
		elif len(re.sub('\W', '', strs)) == len("".join(re.findall('\d+', strs))):
			# print("纯数字日期处理 ... ", strs)
			special_num_dtime_strs = self.numeric_dtime_preNormalization(strs)
			if special_num_dtime_strs:
				strs = special_num_dtime_strs


		# 4. 特殊格式日期预处理： 数值 + 汉字:
		# 如 06年, '09年4月', 09年度4月4号'，'2020年下半年', '2022上半年', 22年上半年', '2022年度下半年'
		else:
			special_others_dtime_strs = self.chinese_numeric_preNormalization(strs)
			if special_others_dtime_strs:
				strs = special_others_dtime_strs


		# 5. 通用格式化处理
		dtime_match_strs = re.search(reg, strs, re.IGNORECASE)

		datetime_strs = ''
		if dtime_match_strs:
			dtime_match_strs = dtime_match_strs.group()

			datetime_strs = self.dtime_normalization(dtime_match_strs)


		return datetime_strs


time_parser = date_parser()


if __name__ == '__main__':
	t = 'JUNE 2014'
	print(time_parser.process(t))
	t = '201402'
	print(time_parser.process(t))
	t = '2019-06-09 15:00:50'
	print(time_parser.process(t))

