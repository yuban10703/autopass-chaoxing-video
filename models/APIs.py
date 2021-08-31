# -*- coding: utf-8 -*-
# @Time    : 2021/8/31 08:35
# @Author  : yuban10703

import hashlib
import random
import time

import httpx
from retrying import retry


class ChaoxingAPI:

    def __init__(self, username, password):
        self.client = httpx.Client(
            headers={
                'User-Agent': f'Dalvik/2.1.0 (Linux; U; Android {random.randint(8, 13)}.0.1; MI {random.randint(8, 13)} Build/Xiaomi) com.chaoxing.mobile/ChaoXingStudy_3_4.8_android_phone_598_56 (@Kalimdor)_fba947fbf9be488ab207b87e3780fc5d',
                'X-Requested-With': 'com.chaoxing.mobile'
            }
        )
        self.username = username
        self.password = password
        #####
        self.userid = None
        self.personid = None  # emmm,好像没用

    def login(self):
        url_1 = 'https://passport2-api.chaoxing.com/v11/loginregister?cx_xxt_passport=json'
        data_1 = {
            'uname': self.username,
            'code': self.password,
            'loginType': 1,
            'roleSelect': True
        }
        res_1 = self.client.post(url=url_1, data=data_1).json()
        if res_1.get('status'):
            print('获取cookie成功_1\r\n', res_1)
        else:
            return False
        url_2 = 'https://sso.chaoxing.com/apis/login/userLogin4Uname.do'
        res_2 = self.client.get(url_2).json()
        if res_2.get('result') == 1:
            print('获取cookie成功_2\r\n', res_2)
        else:
            return False
        self.userid = self.client.cookies['UID']
        return True

    def get_course(self):
        url = 'https://mooc1-api.chaoxing.com/mycourse/backclazzdata?view=json&mcode='
        res = self.client.get(url).json()
        if res.get('result') == 1:
            print('获取课程成功\r\n', res)
            # self.personid =
            return res

    @retry(stop_max_attempt_number=3)
    def get_course_id(self, courseid, clazzid):
        url = 'https://mooc1-api.chaoxing.com/gas/clazzperson'
        params = {
            'courseid': courseid,
            'clazzid': clazzid,
            'userid': self.userid,
            'personid': self.personid,
            'view': 'json',
            'fields': 'clazzid,popupagreement,personid,clazzname'
        }
        return self.client.get(url, params=params).json()

    @retry(stop_max_attempt_number=3)
    def get_course_data(self, clazzid):
        url = 'https://mooc1-api.chaoxing.com/gas/clazz'
        params = {
            'id': clazzid,
            'personid': self.personid,
            'fields': 'id,bbsid,classscore,isstart,allowdownload,chatid,name,state,isthirdaq,isfiled,information,discuss,visiblescore,begindate,coursesetting.fields(id,courseid,hiddencoursecover,hiddenwrongset,coursefacecheck),course.fields(id,name,infocontent,objectid,app,bulletformat,mappingcourseid,imageurl,teacherfactor,knowledge.fields(id,name,indexOrder,parentnodeid,status,layer,label,begintime,endtime,attachment.fields(id,type,objectid,extension).type(video)))',
            'view': 'json'
        }
        return self.client.get(url, params=params).json()

    # def get_nodes(self, clazzid):
    #     url = 'https://mooc1-api.chaoxing.com/gas/clazz'
    #     params = {
    #         'id': clazzid,
    #         'personid': self.personid,
    #         'fields': 'id,bbsid,classscore,isstart,allowdownload,chatid,name,state,isthirdaq,isfiled,information,discuss,visiblescore,begindate,coursesetting.fields(id,courseid,hiddencoursecover,hiddenwrongset,coursefacecheck),course.fields(id,name,infocontent,objectid,app,bulletformat,mappingcourseid,imageurl,teacherfactor,knowledge.fields(id,name,indexOrder,parentnodeid,status,layer,label,begintime,endtime,attachment.fields(id,type,objectid,extension).type(video)))',
    #         'view': 'json'
    #     }
    #     return self.client.get(url, params=params).json()
    @retry(stop_max_attempt_number=3)
    def get_jobs_nodes(self, courseid, clazzid, nodes):
        url = 'https://mooc1-api.chaoxing.com/job/myjobsnodesmap'
        data = {
            'courseid': courseid,
            'clazzid': clazzid,
            'cpi': self.personid,
            'nodes': nodes,
            'time': int(round(time.time() * 1000)),
            'userid': self.userid,
            'view': 'json'
        }
        return self.client.post(url, data=data).json()

    @retry(stop_max_attempt_number=3)  # 最大重试次数，超过后正常抛出异常
    def get_knowledge_card(self, clazzid, courseid, knowledgeid):
        url = 'https://mooc1-api.chaoxing.com/knowledge/cards'
        params = {
            'clazzid': clazzid,
            'courseid': courseid,
            'knowledgeid': knowledgeid,
            'num': 0,
            'isPhone': 1,
            'control': True,
            'cpi': self.personid
        }
        return self.client.get(url, params=params).text

    @retry(stop_max_attempt_number=3)
    def get_d_token(self, objectid, fid):
        url = 'https://mooc1-api.chaoxing.com/ananas/status/{}'.format(objectid)
        params = {
            'k': fid,
            'flag': 'normal',
            '_dc': int(round(time.time() * 1000))
        }
        return self.client.get(url, params=params).json()

    @retry(stop_max_attempt_number=3)
    def pass_video(self, personid, dtoken, otherInfo, playingTime, clazzId, duration, jobid, objectId):
        url = 'https://mooc1-api.chaoxing.com/multimedia/log/a/{}/{}'.format(personid, dtoken)
        # print(url)
        params = {
            'otherInfo': otherInfo,
            'playingTime': playingTime,
            'duration': duration,
            'akid': None,
            'jobid': jobid,
            'clipTime': '0_{}'.format(duration),
            'clazzId': clazzId,
            'objectId': objectId,
            'userid': self.userid,
            'isdrag': 0,
            'enc': self.get_enc(clazzId, jobid, objectId, playingTime, duration),
            'rt': '0.9',
            'dtype': 'Video',
            'view': 'json'
        }
        return self.client.get(url, params=params).json()

    def get_enc(self, clazzId, jobid, objectId, playingTime, duration):
        # https://github.com/ZhyMC/chaoxing-xuexitong-autoflush/blob/445c8d8a8cc63472dd90cdf2a6ab28542c56d93b/logger.js
        return hashlib.md5(
            f"[{clazzId}][{self.userid}][{jobid}][{objectId}][{playingTime * 1000}][d_yHJ!$pdA~5][{duration * 1000}][0_{duration}]".encode()).hexdigest()
