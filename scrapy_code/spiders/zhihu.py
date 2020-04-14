# -*- coding: utf-8 -*-
import json
import re
import time

import scrapy


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://https://www.zhihu.com/']

    def parse(self, response):
        pass


    # 需要登录，重写scrapy.spider的start_requests方法
    def start_requests(self):
        return scrapy.Request('https://www.zhihu.com/signin?next=%2F', headers=self.headers, callback=self.login)

    # 获取xsrf和验证码
    def login(self, response):
        response_text = response.text
        match_re = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        xsrf = ''
        if match_re:
            xsrf = match_re.group(1)
        if xsrf:
            post_url = "https://www.zhihu.com/login/phone_num"
            post_data = {
                "_xsrf": xsrf,
                "phone_num": "",
                "password": "",
                "captcha": ""
            }

            t = str(int(time.time()*1000))
            captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
            # 获取验证码
            yield scrapy.Request(captcha_url, headers=self.headers, meta={'post_data': post_data}, callback=self.login_after_captcha)

    def login_after_captcha(self, response):
        with open("captcha.jpg", "wb") as f:
            f.write(response.body)
            f.close()

        from PIL import Image
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            pass

        captcha = input("输入验证码\n>")

        post_data = response.meta.get("post_data", {})
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data["captcha"] = captcha
        return [scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=self.headers,
            callback=self.check_login
        )]

    def check_login(self, response):
        #验证服务器的返回数据判断是否成功
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers) #没有callback的话默认走parse



