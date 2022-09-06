#coding=UTF-8
import json
import re
import base64
import time
import datetime
from cookie_getter import CookieGetter
from captcha import read_captcha
from email_sender import sendEmail
from utils import *

_, URL_DICT = ReadNetWorkJson()

class CourseSearcher(CookieGetter):
    def __init__(self):
        super(CourseSearcher, self).__init__()
        now_timestamp = str(int(time.time()))

        self.mainUrl = URL_DICT['MAIN_PAGE']
        self.xkPageUrl = URL_DICT['NT_XK_PAGE'] + now_timestamp
        self.baseUrl = URL_DICT['BASE_URL']
        self.selCourseUrl = URL_DICT['SELECT_COURSE']
        self.captchaUrl = URL_DICT['CAPTCHA']
        self.NTslideUrl = URL_DICT['NT_SLIDE_QUERY']
        
        self.form_data = PayloadGetter('formData')
        self.main_page_data = PayloadGetter('mainPageData')
        self.lessonNO = ReadLessonJson()
        self.cookies = self.getCookies()
        self.have_post_try = False

        course_no, course_id, course_name = findClassList(res.text, lessonNo)
        self.course_id = course_id
        self.course_no = course_no
        self.course_name = course_name
        
    def RunScript(self):
        result = False
        while result == False:
            result = self.addCourse()
        
    def addCourse(self):
        res = self.searchCourse(self.lessonNO)
        if isCourseAvailable(res.text, self.course_no):
            info = "课程 [" + self.course_name + " " + self.course_id +"], 可选, 正在选课中"
            self.printK(info)
            #sendEmail(info)
            result = self.selCourse(course_no)
            return result
        else:
            info = "课程 [" + self.course_name + " " + self.course_id +"], 目前不可选"
            self.printK(info)
            return False
        
    def searchCourse(self, lessonNo):
        form = self.form_data
        form['lessonNo'] = lessonNo
        
        self.direct_to_selCoursePage() # 验证步骤，必须执行，不然会被服务器反制
        
        res = self.Post(
            url=self.baseUrl,
            cookies=self.cookies,
            data = form,
            ErrMsg="Serch Course Error (getCourseNoAndId)"
        )
        return res
    
    def direct_to_selCoursePage(self):
        self.Get(
            url=self.xkPageUrl,
            cookies=self.cookies,
            ErrMsg="Get Main Page Error (getCourseNoAndId) Get"
        )
        self.Post(
            url=self.mainUrl,
            cookies=self.cookies,
            data = self.main_page_data,
            ErrMsg="Into Xk Page Error (getCourseNoAndId) Post"
        )
                
    # 抢课（捡漏）
    def selCourse(self, course_no):
        form_data = {
            'optype': 'true',
            'operator0': course_no + ':true:0',
            'captcha_response': self.getCaptcha()
        }
        response = self.Post(
            url=self.selCourseUrl,
            cookies=self.cookies,
            data=form_data,
            ErrMsg="selCourse Error (selCourse)"
        )
        raw_str = response.content
        res = re.findall(r"成功", raw_str)
        if len(res):
            self.printK('{} 选课成功。'.format(self.LessonID))
            return True
        else:
            return False
        # print(response.content.decode(encoding='utf-8'))
  
    def getCaptcha(self):
        response = self.Get(
            url=self.captchaUrl,
            cookies=self.cookies,
            ErrMsg="Get Captcha Error (getCaptcha)"
        )
        captcha =  read_captcha(response.content)
        return captcha
    
    def printK(self, info):
        print('[{}] {}'.format(datetime.datetime(), info))
    

if __name__ == "__main__":
    launcher = CourseSearcher()
    launcher.RunScript()
            