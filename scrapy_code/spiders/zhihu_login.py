# -*- coding: utf-8 -*-
# @Time    : 2020/3/24 8:33 上午
# @Author  : Neehong
# @FileName: zhihu_login.py
# @Software: PyCharm
import hashlib
import hmac
import json
import time
from http import cookiejar

import requests

"""
在知乎登录页进行模拟请求登录之后，发现post提交的登录相关信息在Headers和Formdata,而且Formdata是进行了加密的
"""

HEADERS = {

}

LOGIN_URL = ''

LOGIN_API = ''

FORM_DATA = {

}


class ZhihuLogin(object):
    def __init__(self):
        self.login_url = LOGIN_URL
        self.login_api = LOGIN_API
        self.login_data = FORM_DATA
        self.session = requests.session()
        self.session.headers = HEADERS
        self.session.cookies = cookiejar.LWPCookieJar(filename='XXX.txt')

    def login(self, username=None, password=None, load_cookies=True):
        """
        模拟知乎登录
        :param username: 登录手机号
        :param password: 密码
        :param load_cookies: 是否读取上次保存的cookies
        :return: bool
        """

        # 如果需要加载cookies
        if load_cookies and self.load_cookies() and self.check_login():
            return True

        # 填写header
        headers = self.session.headers.copy()
        headers.update({
            'X-Xsrftoken': self.get_xsrf()
        })

        # 检测用户名和密码的输入,并填充用户名密码、验证码、时间戳、signature
        username, password = self.checkuser(username, password)
        timestamp = str(int(time.time()*1000))
        self.login_data.update({
            'username': username,
            'password': password,
            'captcha': self.get_captcha(XXX),
            'timestamp': timestamp,
            'signature': self.get_signature(timestamp)
        })

        # 检测响应结果
        response = self.session.post(self.login_api, data=self.login_data, headers=headers)
        if 'error' in response.text:
            print(json.loads(response.text)['error']['message'])
        elif self.check_login():
            return True
        print('登录失败')
        return False






    def load_cookies(self):
        """
        读取cookie文件加载到session
        :return: bool
        """

        try: #todo:是否需要文件名
            self.session.cookies.load(ignore_discard=True)
        except FileNotFoundError:
            return False

    def check_login(self):
        """
        检查登录状态
        如登录成功则保存当前cookies
        :return: bool
        """

        response = self.session.get(self.login_url, allow_redirect=False)
        if response.status.code == 302:
            self.session.cookies.save()
            print('登录成功')
            return True
        return False

    def get_xsrf(self):
        """
        从登录页面获取token
        """

        response = self.session.get(self.login_url)
        token = response.cookies['_xrsf']
        return token

    def get_captcha(self, lang, headers):
        """
        :param lang: 返回验证码的语言（en/cn)
        :param headers: 带授权信息的请求头部
        :return: 验证码的post参数
        """
        # if lang == 'cn':
        #
        #     api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=cn'
        #
        # else:
        #
        #     api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
        #
        # resp = self.session.get(api, headers=headers)
        #
        # show_captcha = re.search(r'true', resp.text)
        #
        # if show_captcha:
        #
        #     put_resp = self.session.put(api, headers=headers)
        #
        #     json_data = json.loads(put_resp.text)
        #
        #     img_base64 = json_data['img_base64'].replace(r'\n', '')
        #
        #     with open('./captcha.jpg', 'wb') as f:
        #
        #         f.write(base64.b64decode(img_base64))
        #
        #     img = Image.open('./captcha.jpg')
        #
        #     if lang == 'cn':
        #
        #         plt.imshow(img)
        #
        #         print('点击所有倒立的汉字，按回车提交')
        #
        #         points = plt.ginput(7)
        #
        #         capt = json.dumps({'img_size': [200, 44],
        #
        #                            'input_points': [[i[0] / 2, i[1] / 2] for i in points]})
        #
        #     else:
        #
        #         img.show()
        #
        #         capt = input('请输入图片里的验证码：')
        #
        #     # 这里必须先把参数 POST 验证码接口
        #
        #     self.session.post(api, data={'input_text': capt}, headers=headers)
        #
        #     return capt
        #
        # return ''

    def get_signature(self, timestamp):
        """
        通过Hmac算法计算返回签名
        实际是几个固定字符串加时间戳
        :param timestamp: 时间戳
        :return: 签名
        """

        # ha = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=hashlib.sha1)
        #
        # grant_type = self.login_data['grant_type']
        #
        # client_id = self.login_data['client_id']
        #
        # source = self.login_data['source']
        #
        # ha.update(bytes((grant_type + client_id + source + timestamp), 'utf-8'))
        #
        # return ha.hexdigest()

    def check_user(self, username, password):
        """
        检查用户名和密码是否已经输入，若无则手动输入
        """

        if username is None:
            username = self.login_data.get('username')
            if not username:
                username = input("请输入手机号")
        if '+86' not in username:
            username = '+86' + username

        if password is None:
            password = self.login_data.get('password')
            if not password:
                password = input('请输入密码')
        return username, password


