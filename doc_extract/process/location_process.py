#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import json
import collections
import jieba
import jieba.posseg as pseg
from os.path import abspath, join, dirname

def china_location_loader():
    " 加载中国行政区域信息 "

    cur_province = None
    cur_city = None
    cur_county = None
    cur_town = None
    cur_village = None
    location_dict = dict()

    location_file = abspath(join(dirname(__file__), 'china_location.txt'))
    china_location = [x.strip("\n") for x in open(location_file, 'r', encoding='utf-8').readlines()]
    for item in china_location:
        if not item.startswith('\t'):  # 省
            if len(item.strip().split('\t')) != 3:
                continue
            province, admin_code, alias_name = item.strip().split('\t')
            cur_province = province
            location_dict.update(
                {cur_province: {'_full_name': province,
                                '_alias': alias_name,
                                '_admin_code': admin_code}})

        elif item.startswith('\t\t\t\t'):  # 村、社区

            cur_village = item.strip()
            location_dict[cur_province][cur_city][cur_county][cur_town].update(
                {cur_village: None})

        elif item.startswith('\t\t\t'):  # 乡镇、街道

            cur_town = item.strip()
            location_dict[cur_province][cur_city][cur_county].update(
                {cur_town: dict()})

        elif item.startswith('\t\t'):  # 县、区
            if len(item.strip().split('\t')) != 3:
                continue
            county, admin_code, alias_name = item.strip().split('\t')
            cur_county = county
            location_dict[cur_province][cur_city].update(
                {cur_county: {'_full_name': county,
                              '_alias': alias_name,
                              '_admin_code': admin_code}})

        else:  # 市
            if len(item.strip().split('\t')) != 3:
                continue
            city, admin_code, alias_name = item.strip().split('\t')
            cur_city = city
            location_dict[cur_province].update(
                {cur_city: {'_full_name': city,
                            '_alias': alias_name,
                            '_admin_code': admin_code}})
    return location_dict



def china_location_change_loader():
    " 加载中国行政区域变更信息 "

    change_file = abspath(join(dirname(__file__), 'china_location_change.txt'))
    location_change_list = list()
    location_change = [x.strip("\n") for x in open(change_file, 'r', encoding='utf-8').readlines()]

    for line in location_change:
        location_change_dict = dict()
        line_seg = line.split('=>')
        orig_line_seg = line_seg[0].split('\t')
        new_line_seg = line_seg[1].split('\t')
        location_change_dict.update(
            {'date': orig_line_seg[0], 'department': orig_line_seg[1],
             'old_loc': [orig_line_seg[2: 4], orig_line_seg[4: 6], orig_line_seg[6: 8]],
             'new_loc': new_line_seg})
        location_change_list.append(location_change_dict)

    del location_change
    return location_change_list


def world_location_loader():
    """ 加载世界地名词典 world_location.txt """

    # file_path = './world_location.txt'
    file_path = abspath(join(dirname(__file__), 'world_location.txt'))
    content = [x.strip('\n') for x in open(file_path, 'r', encoding='utf-8').readlines()]
    result = dict()
    cur_continent = None

    for line in content:
        if '洲:' in line:
            cur_continent = line.replace(':', '')
            result.update({cur_continent: dict()})
            continue

        item_tup = line.split('\t')
        item_length = len(item_tup)
        if item_length == 3:
            result[cur_continent].update(
                {item_tup[0]: {'full_name': item_tup[1],
                               'capital': item_tup[2]}})

        if item_length == 4:
            result[cur_continent].update(
                {item_tup[0]: {'full_name': item_tup[1],
                               'capital': item_tup[2],
                               'main_city': item_tup[3].split('/')}})
        else:
            pass

    return result


def worldLocationparser(strs: str):
    """ 国外地址匹配处理  """

    def _mapping_world_location(world_loc):
        # 整理国外行政区划映射表
        world_administrative_map_list = list()
        for continent in world_loc:
            for country in world_loc[continent]:
                cities = [world_loc[continent][country]['capital']]
                if 'main_city' in world_loc[continent][country]:
                    cities.extend(world_loc[continent][country]['main_city'])
                world_administrative_map_list.append(
                    [[country, world_loc[continent][country]['full_name']],
                     None])
                for city in cities:
                    world_administrative_map_list.append(
                        [[country, world_loc[continent][country]['full_name']],
                         city])

        return world_administrative_map_list


    def _combine_world_locations(world_combine_list, cur_location):

        if len(world_combine_list) == 0:
            cur_location.append(True)
            world_combine_list.append(cur_location)
            return world_combine_list

        combine_flag = False
        for item in world_combine_list:
            cur_combine_flag = True
            if item[0]['country'] is not None and cur_location[0]['country'] is not None:
                if item[0]['country'] != cur_location[0]['country']:
                    cur_combine_flag = False
            if item[0]['city'] is not None and cur_location[0]['city'] is not None:
                if item[0]['city'] != cur_location[0]['city']:
                    cur_combine_flag = False

            if cur_combine_flag:
                # 可以合并了，因为都一样的公共部分
                # 将较短的一个地名设置为 False，频次取两者最大值
                none_num = len([i for i in list(item[0].values()) if i is None])
                cur_none_num = len([i for i in list(cur_location[0].values()) if i is None])
                if none_num < cur_none_num:  # 当前进入的地址较短，不作为最终结果
                    item[1] = item[1] + cur_location[1]
                    cur_location.append(False)
                    combine_flag = True  # 在计算最末将该地址添加进去

                else:  # 替换掉该条较短的地址，作为最终结果
                    item[2] = False
                    cur_location[1] = item[1] + cur_location[1]
                    cur_location.append(True)

                    combine_flag = True

        if combine_flag:
            world_combine_list.append(cur_location)
        else:  # 并无合并，但是仍需加在所有结果的末尾
            cur_location.append(True)
            world_combine_list.append(cur_location)

        return world_combine_list

    def get_world_candidates(location):

        world_loc = world_location_loader()
        world_administrative_map_list = _mapping_world_location(world_loc)

        level_list = ['country', 'city']
        candidate_admin_list = list()  # 候选列表
        for admin_item in world_administrative_map_list:
            count = 0
            for idx, name_item in enumerate(admin_item):
                match_flag = False
                if idx == 0:  # 国家名
                    for name in name_item:  # 别名与全名任意匹配一个
                        if name is not None and name == location:
                            match_flag = True
                            break
                elif idx == 1:  # 城市名
                    if name_item is not None:
                        if name_item in [location, location.replace('市', '')]:
                            # 兼顾到国外地名未提各类别名的情况
                            match_flag = True
                else:
                    raise ValueError

                if match_flag:
                    count += 1
                    # offset 中的每一个元素，分别指示国家、城市是否被匹配
                    offset_list = [1 if i <= idx else 0 for i in range(2)]

            if count > 0:
                cur_item = dict()
                for level, offset, name in zip(level_list, offset_list, admin_item):
                    if offset == 1:
                        if type(name) is list:

                            cur_item.update({level: name[0]})
                        elif type(name) is str:
                            cur_item.update({level: name})
                    else:
                        cur_item.update({level: None})
                if cur_item not in candidate_admin_list:
                    candidate_admin_list.append(cur_item)

        return candidate_admin_list

    final_res = {'foreign': None}
    text_pos_seg = pseg.cut(strs)
    text_location = [w for w, f in text_pos_seg if f == 'ns']
    if len(text_location) == 0:
        return {'foreign': None}

    location_count = dict(collections.Counter(text_location).most_common())
    not_matched_list = copy.deepcopy(location_count)  # 统计未匹配地址

    world_combine_list = list()  # 将若干世界地名合并
    for location, count in location_count.items():
        world_candidates = get_world_candidates(location)
        if len(world_candidates) > 0:  # 匹配到地址
            if location in not_matched_list:
                not_matched_list.pop(location)  # 从未匹配词典中删除

            for world_candidate in world_candidates:
                world_combine_list = _combine_world_locations(
                    world_combine_list, [world_candidate, count])

    foreign_locations = sorted(
        [item[:2] for item in world_combine_list if item[-1]],
        key=lambda i: i[1], reverse=True)

    if len(foreign_locations) > 0:
        final_res['foreign'] = foreign_locations[:3]


    return final_res



class LocationParser(object):

    def __init__(self):
        self.administrative_map_list = None
        self.town_village = False
        self.town_village_dict = dict()

    def _mapping(self, china_loc, china_change_loc):
        # 整理行政区划码映射表
        self.administrative_map_list = list()  # 地址别称

        for prov in china_loc:
            if prov.startswith('_'):
                continue
            if china_loc[prov]['_alias'] in self.municipalities_cities:
                pass
                # 去除直辖市仅包含省级的信息，因为直辖市一定将匹配至市一级。
            else:
                self.administrative_map_list.append(
                    [china_loc[prov]['_admin_code'],
                     [prov, china_loc[prov]['_alias']],
                     [None, None],
                     [None, None], True])  # True 表示数据为最新地名，反之为旧地名

            for city in china_loc[prov]:
                if city.startswith('_'):
                    continue
                self.administrative_map_list.append(
                    [china_loc[prov][city]['_admin_code'],
                     [prov, china_loc[prov]['_alias']],
                     [city, china_loc[prov][city]['_alias']],
                     [None, None], True])

                for county in china_loc[prov][city]:
                    if county.startswith('_'):
                        continue
                    self.administrative_map_list.append(
                        [china_loc[prov][city][county]['_admin_code'],
                         [prov, china_loc[prov]['_alias']],
                         [city, china_loc[prov][city]['_alias']],
                         [county, china_loc[prov][city][county]['_alias']],
                         True])

                    if self.town_village:  # 补充 self.town_village_list

                        key_name = prov + city + county
                        value_dict = china_loc[prov][city][county]
                        self.town_village_dict.update({key_name: value_dict})

        # 将旧有的地名融入 self.administrative_map_list，并建立映射表
        self.old2new_loc_map = dict()

        for item in china_change_loc:
            self.administrative_map_list.append(
                ['000000', item['old_loc'][0], item['old_loc'][1],
                 item['old_loc'][2], False])
            self.old2new_loc_map.update(
                {''.join([i[0] for i in item['old_loc']]): item['new_loc']})

    def _prepare(self):
        self.municipalities_cities = set([
            '北京', '上海', '天津', '重庆', '香港', '澳门'])

        # 添加中国区划词典
        china_loc = china_location_loader()
        china_change_loc = china_location_change_loader()
        self._mapping(china_loc, china_change_loc)

        self.loc_level_key_list = ['省', '市', '县']
        if self.town_village:
            self.loc_level_key_list.extend(['乡', '村'])
        self.loc_level_key_dict = dict(
            [(loc_level, None) for loc_level in self.loc_level_key_list])

    def get_candidates(self, location_text):
        """ 从地址中获取所有可能涉及到的候选地址 """

        if self.administrative_map_list is None:
            self._prepare()

        candidate_admin_list = list()  # 候选列表
        for admin_item in self.administrative_map_list:
            count = 0  # 匹配个数
            offset_list = [[-1, -1], [-1, -1], [-1, -1]]

            for idx, name_item in enumerate(admin_item[1: -1]):
                match_flag = False
                cur_name = None
                cur_alias = None
                for alias_idx, name in enumerate(name_item):  # 别名与全名任意匹配一个
                    if name is not None and name in location_text:
                        match_flag = True
                        cur_name = name
                        cur_alias = alias_idx
                        break
                if match_flag:
                    count += 1
                    offset_list[idx][0] = location_text.index(cur_name)
                    offset_list[idx][1] = cur_alias

            if count > 0:

                cur_item = copy.deepcopy(admin_item)
                if admin_item[2][1] in self.municipalities_cities:
                    count -= 1
                cur_item.extend([count, offset_list])
                candidate_admin_list.append(cur_item)

        return candidate_admin_list

    def chinacall(self, location_text,  change2new=True):

        if self.administrative_map_list is None:
            self._prepare()


        # 获取文本中的省、市、县三级行政区划
        # step 1: 命中匹配别名或全名，统计命中量，并假设省市县分别位于靠前的位置且依次排开
        candidate_admin_list = self.get_candidates(location_text)

        if len(candidate_admin_list) == 0:
            result = {'province': None,
                      'city': None,
                      'county': None,
                      'full_location': location_text,
                      }

            return result

        # step 2: 寻找匹配最多的候选地址，然后寻找匹配最靠前的候选地址，作为最终的省市县的判断结果
        # 2.1 找出文本中匹配数量最多的
        max_matched_num = max([item[-2] for item in candidate_admin_list])
        candidate_admin_list = [item for item in candidate_admin_list
                                if item[-2] == max_matched_num]

        # 2.2 找出匹配位置最靠前的
        candidate_admin_list = sorted(candidate_admin_list, key=lambda i: sum([j[0] for j in i[-1]]))

        # 对于有些 地市名 和 县级名简称相同的，需要进行过滤，根据被匹配的 offset 进行确定。
        # 直辖市除外
        new_candidate_admin_list = []
        for item in candidate_admin_list:
            if item[1][1] in self.municipalities_cities:
                new_candidate_admin_list.append(item)
            else:
                if -1 not in [item[-1][0][0], item[-1][1][0], item[-1][2][0]]:
                    # 省、市、县全都匹配到
                    if (item[-1][0][0] < item[-1][1][0]) and (item[-1][1][0] < item[-1][2][0]):
                        # 必须按照 省、市、县的顺序进行匹配
                        new_candidate_admin_list.append(item)
                else:
                    new_candidate_admin_list.append(item)

        candidate_admin_list = new_candidate_admin_list
        if len(candidate_admin_list) == 0:
            result = {'province': None,
                      'city': None,
                      'county': None,
                      'full_location': location_text}
            return result

        min_matched_offset = sum([j[0] for j in candidate_admin_list[0][-1]])
        candidate_admin_list = [item for item in candidate_admin_list
                                if sum([j[0] for j in item[-1]]) == min_matched_offset]

        # 2.3 优先匹配包含全面的，其次匹配别名，此处将别名的过滤掉
        full_alias_list = [min([j[1] for j in item[-1] if j[1] > -1]) for item in candidate_admin_list]
        full_alias_min = min(full_alias_list)
        candidate_admin_list = [item for val, item in zip(full_alias_list, candidate_admin_list) if
                                val == full_alias_min]

        # step 3: 县级存在重复名称，计算候选列表中可能重复的县名
        county_dup_list = [item[3][item[-1][-1][1]] for item in candidate_admin_list]
        county_dup_list = collections.Counter(county_dup_list).most_common()
        county_dup_list = [item[0] for item in county_dup_list if item[1] > 1]

        final_admin = candidate_admin_list[0]  # 是所求结果

        # step 4: 根据已有的省市县，确定剩余部分为详细地址
        detail_idx = 0

        final_prov = None
        final_city = None
        final_county = None
        for admin_idx, i in enumerate(final_admin[-1]):
            if i[0] != -1:
                detail_idx = i[0] + len(final_admin[admin_idx + 1][i[1]])
                # rule: 全国地址省市无重复命名，而县级有，如鼓楼区、高新区等
                if admin_idx >= 0 and final_admin[admin_idx + 1][i[1]] not in county_dup_list:
                    final_prov = final_admin[1][0]
                if admin_idx >= 1 and final_admin[admin_idx + 1][i[1]] not in county_dup_list:
                    final_city = final_admin[2][0]
                if admin_idx >= 2 and final_admin[admin_idx + 1][i[1]] not in county_dup_list:
                    final_county = final_admin[3][0]
                else:
                    final_county = final_admin[3][i[1]]

        # step 5: 将旧地址根据映射转换为新地址
        if change2new:
            tmp_key = ''.join([final_prov if final_prov else '',
                               final_city if final_city else '',
                               final_county if final_county else ''])
            if tmp_key in self.old2new_loc_map:
                final_prov, final_city, final_county = self.old2new_loc_map[tmp_key]

        # step 6: 获取详细地址部分
        detail_part = location_text[detail_idx:]
        if len(detail_part) == 0:
            pass
        elif detail_part[0] in '县':
            detail_part = detail_part[1:]

        # step 7: 将地址中的 省直辖、市直辖，去掉
        if final_city is not None and '直辖' in final_city:
            final_city = None
        if final_county is not None and '直辖' in final_county:
            final_county = None

        # step 8: 获取省市区行政区划部分
        admin_part = ''
        if final_prov is not None:
            admin_part = final_prov
        if final_city is not None:
            match_muni_flag = False
            for muni_city in self.municipalities_cities:
                if muni_city in final_city:
                    match_muni_flag = True
                    break
            if not match_muni_flag:
                admin_part += final_city
        if final_county is not None:
            admin_part += final_county

        result = {'province': final_prov,
                  'city': final_city,
                  'county': final_county,
                  'full_location': admin_part + detail_part
                  }


        return result


    def __call__(self, location_text):
        info = ''
        res = self.chinacall(location_text)
        if res['province'] is None or res['city'] is None:
            res = worldLocationparser(location_text)
            if res["foreign"]:
                res = res["foreign"][0][0]
                # print(res)
                info = "".join([v for k, v in res.items() if k and v ])

        else:
            # print(res)
            # info = ''.join([v for k,v in res.items() if k in ['province', 'city' 'county'] and v])
            info = ''.join([res.get(k) for k in ['province', 'city', 'county'] if res.get(k)])

        return info


location = LocationParser()


if __name__ == '__main__':

    loc  = '太仓'
    loc = '成都'
    loc = '上海'
    loc = '庐山'
    # loc = '巴黎'
    loc = '兴化2'
    # res = location(loc)
    # print(res)

    loc = '华盛顿'
    loc = '巴黎'
    loc = '辽源'
    loc = '巴西'
    print(location(loc))

