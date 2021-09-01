# -*- coding: utf-8 -*-
# @Time    : 2021/8/30 19:51
# @Author  : yuban10703
import json
import re
import time

from models import ChaoxingAPI


class PassVideo:
    def __init__(self, chaoxingAPI: ChaoxingAPI):
        self.chaoxing = chaoxingAPI

    def print_progress_bar(self, one, all_count, width=30):
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

    def process_course(self, course_data):
        backData = []
        for course in course_data:
            if course.get('cataName') != '课程' or type(course.get('key')) != int:
                print(course)
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

    def main(self):
        if not self.chaoxing.login():
            print('登录失败')
            return
        if all_course := chaoxing.get_course():
            course_all_id_data = self.process_course(all_course['channelList'])
            for i in range(len(course_all_id_data)):
                print(f"| {i} | {course_all_id_data[i]['name']} \r\n")
        else:
            print('未获取到课程数据')
            return
        while input_ids := input('请选择需要的课程序号(多个序号用空格隔开):'):
            course_index = input_ids.split(' ')
            if all(e.isdigit() for e in course_index):
                break
        for index_id in course_index:
            course_data = self.chaoxing.get_course_data(course_all_id_data[int(index_id)]['clazzid'])
            for knowledge_id_data in course_data['data'][0]['course']['data'][0]['knowledge']['data']:
                time.sleep(0.5)
                # print(knowledge_id_data)
                knowledge_card_web_text = self.chaoxing.get_knowledge_card(
                    course_all_id_data[int(index_id)]['clazzid'],
                    course_all_id_data[int(index_id)]['courseid'],
                    knowledge_id_data['id'])
                # print(knowledge_card_web_text)
                # print(knowledge_id_data['id'])
                attachments = self.get_attachments(knowledge_card_web_text)
                if attachments:
                    # print(attachments)
                    if attachments['attachments'] == []:
                        continue
                    if attachments['attachments'][0].get('objectId') == None:
                        # print(attachments)
                        continue
                    print(f'当前视频:{knowledge_id_data["label"]}:{knowledge_id_data["name"]}')
                    if attachments['attachments']:
                        video_info = self.chaoxing.get_d_token(
                            attachments['attachments'][0].get('objectId'),
                            attachments['defaults']['fid'])
                        # print(video_info)
                        playingTime = 0
                        sec = 58
                        for i in range(video_info['duration']):
                            if sec == 58:
                                sec = 0
                                res = self.chaoxing.pass_video(
                                    attachments['defaults']['cpi'],
                                    video_info['dtoken'],
                                    attachments['attachments'][0]['otherInfo'],
                                    playingTime,
                                    course_all_id_data[int(index_id)]['clazzid'],
                                    video_info['duration'],
                                    attachments['attachments'][0]['jobid'],
                                    video_info['objectid']
                                )
                                playingTime += 58
                                if res['isPassed']:
                                    self.print_progress_bar(video_info['duration'], video_info['duration'])
                                    print(f'  已完成          ')
                                    break
                            self.print_progress_bar(i, video_info['duration'])
                            sec += 1
                            time.sleep(1)


if __name__ == '__main__':
    username = input('请输入超星手机号: ')
    password = input('请输入密码: ')
    chaoxing = ChaoxingAPI(username, password)
    PassVideo(chaoxing).main()
