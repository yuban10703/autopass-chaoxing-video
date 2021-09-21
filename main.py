# -*- coding: utf-8 -*-
# @Time    : 2021/8/30 19:51
# @Author  : yuban10703
import json
import random
import re
import time

from natsort import natsorted

from models import ChaoxingAPI


class PassVideo:
    def __init__(self, chaoxingAPI: ChaoxingAPI):
        self.chaoxing = chaoxingAPI

    def print_progress_bar(self, one, all_count, width=30):
        """
        打印进度条
          💩
         💩💩
        💩💩💩
        """
        percent = int(one / all_count * 100)
        left = width * percent // 100
        right = width - left
        if one == all_count:
            symbol = '#'
        elif one % 2 == 0:
            symbol = '\\'
        else:
            symbol = '/'
        if one == all_count:
            mene = ''
        else:
            mene = '   少女折寿中' + '.' * (one % 3 + 1) + '      '
        print('\r[', '#' * left, symbol, ' ' * right, ']',
              f' {percent:.0f}%', mene,
              sep='', end='', flush=True)
        if one >= all_count:
            print(f'  已完成          ')

    def process_course(self, course_data):
        backData = []
        for course in course_data:
            if course.get('cataName') != '课程' or type(course.get('key')) != int:
                # print(course)
                continue
            backData.append({
                'name': course['content']['course']['data'][0]['name'],
                'clazzid': course['key'],
                'courseid': course['content']['course']['data'][0]['id']
            })
        return backData

    def get_attachments(self, text):
        if res := re.search(r'window\.AttachmentSetting =({\"attachments\":.*})', text):
            return json.loads(res[1])

    def knowledge_sort(self, all_knowledge):
        dict_all_knowledge = {}
        for knowledge in all_knowledge:
            dict_all_knowledge[knowledge['label']] = knowledge
        keys_sorted = natsorted(dict_all_knowledge.keys())
        return [dict_all_knowledge[k] for k in keys_sorted]

    def pass_video(self, video_duration, cpi, dtoken, otherInfo, clazzid, jobid, objectid):
        sec = 58
        for playingTime in range(video_duration + 120):
            if sec >= 58:
                sec = 0
                res = self.chaoxing.pass_video(
                    cpi,
                    dtoken,
                    otherInfo,
                    playingTime,
                    clazzid,
                    video_duration,
                    jobid,
                    objectid
                )
                # print(res)
                if res.get('isPassed'):
                    self.print_progress_bar(video_duration, video_duration)
                    break
                elif res.get('error'):
                    raise Exception('请联系作者')
                continue
            self.print_progress_bar(playingTime, video_duration)
            sec += 1
            time.sleep(1)

    def main(self):
        if not self.chaoxing.login():
            print('登录失败')
            return
        if all_course := chaoxing.get_course():
            course_all_id_data = self.process_course(all_course['channelList'])
            for index in range(len(course_all_id_data)):
                print(f"| {index} | {course_all_id_data[index]['name']} \r\n")
        else:
            print('未获取到课程数据')
            return
        while input_ids := input('请选择需要的课程序号(多个序号用空格隔开):'):
            course_index = input_ids.split(' ')
            if all(e.isdigit() for e in course_index):
                break
        for index_id in course_index:
            course_data = self.chaoxing.get_course_data(course_all_id_data[int(index_id)]['clazzid'])
            # print(course_data)
            for knowledge_id_data in self.knowledge_sort(
                    course_data['data'][0]['course']['data'][0]['knowledge']['data']):  # 遍历排序过的任务点
                # print(knowledge_id_data)
                knowledge_json = self.chaoxing.get_knowledge_json(
                    knowledge_id_data['id'],
                    course_all_id_data[int(index_id)]['clazzid']
                )
                # print(knowledge_json)
                tabs = len(knowledge_json['data'][0]['card']['data'])
                # print(tabs)
                for tab_index in range(tabs):
                    knowledge_card_web_text = self.chaoxing.get_knowledge_card(
                        course_all_id_data[int(index_id)]['clazzid'],
                        course_all_id_data[int(index_id)]['courseid'],
                        knowledge_id_data['id'],
                        tab_index
                    )
                    # print(knowledge_card_web_text)
                    # print(knowledge_id_data['id'])
                    attachments: dict = self.get_attachments(knowledge_card_web_text)
                    if not attachments:
                        continue
                    if not attachments.get('attachments'):
                        continue
                    print(f'当前章节:{knowledge_id_data["label"]}:{knowledge_id_data["name"]}')
                    for attachment in attachments['attachments']:  # 遍历任务点
                        # print(attachment)
                        if attachment.get('type') != 'video':  # 只刷视频
                            continue
                        print(f"当前视频:{attachment['property']['name']}")
                        if attachment.get('isPassed'):  # 跳过已完成的
                            self.print_progress_bar(1, 1)
                            continue
                        video_info = self.chaoxing.get_d_token(
                            attachment['objectId'],
                            attachments['defaults']['fid']
                        )
                        self.pass_video(
                            video_info['duration'],
                            attachments['defaults']['cpi'],
                            video_info['dtoken'],
                            attachments['attachments'][0]['otherInfo'],
                            course_all_id_data[int(index_id)]['clazzid'],
                            attachments['attachments'][0]['jobid'],
                            video_info['objectid']
                        )
                time.sleep(random.randint(1, 3))


if __name__ == '__main__':
    username = input('请输入超星手机号: ')
    password = input('请输入密码: ')
    chaoxing = ChaoxingAPI(username, password)
    # chaoxing = ChaoxingAPI("", "")
    PassVideo(chaoxing).main()
