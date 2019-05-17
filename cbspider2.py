#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-05-06
# @Author  : young
# @Version : 0.1
# @Thank   : kangvcar

import ssl
from selenium import webdriver
from email import encoders
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr
import smtplib
import datetime
import os
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

# 集思录爬虫类


class JSL:
    # 初始化变量
    # 传入url
    # 传入filename文件名
    # 传入is_ssl的值,1为使用ssl认证,0为禁用ssl认证
    # 传入single_line的值,1为获取单行数据,2为获取双行数据,默认为0获取所有数据
    # 传入premium_rate,溢价率,默认为8
    # 传入rateofreturn,到期税前收益率，默认为2
    def __init__(self, url, filename, is_ssl, single_line=0, premium_rate=8.00, rateofreturn=2.00):
        # 爬虫的url
        self.url = url
        # 保存内容的文件名
        self.filename = filename
        # 设置是否启用ssl
        self.ssl = is_ssl
        # 设置获取哪些行
        self.single_line = single_line
        # 设置预设筛选条件：溢价率和税前收益率
        self.premium_rate = premium_rate
        self.rateofreturn = rateofreturn
        # 定义xpath
        #self.xpath = '//*[@id="flex_cb"]'
        self.xpath = '/html/body/div[3]/div[1]/div[1]/table/tbody/tr'
        # Email地址和口令:
        self.from_addr = 'hellowhu@163.com'
        self.password = 'jslspider163'
        # SMTP服务器地址:
        self.smtp_server = 'smtp.163.com'
        # 收件人地址:
        self.to_addr = 'hellowhu@qq.com'
        # 调用setSsl方法
        self.setSsl()

    # 定义ssl方法
    def setSsl(self):
        if self.ssl == 0:
            ssl._create_default_https_context = ssl._create_unverified_context()
        elif self.ssl == 1:
            pass
        else:
            return None

    # 设置浏览器驱动方法
    def setWebdrive(self):
        browser = webdriver.Chrome('/Users/young/chromedriver')
        return browser

    # 传入浏览器驱动和url,返回网页源码
    def getPageSource(self, browser, url):
        # page = browser.get(url)
        browser.get(url)
        browser.implicitly_wait(3)
        return browser

    # 传入网页源码，获取匹配的内容，然后写入contents并返回
    def getContent(self, browser):
        contents = []  # 定义list,用于存储匹配的数据
        for tr in browser.find_elements_by_xpath(self.xpath):
            content = tr.text.encode('utf-8')
            contents.append(content)
        return contents

    # 传入获取匹配的内容，把所需数据写入文件的方法
    def writeData(self, contents):
        file = open(self.filename, 'a')
        if self.single_line == 1:
            for index, content in enumerate(contents):
                if index % 2 == 0:
                    file.write(content + '\n')
        elif self.single_line == 2:
            for index, content in enumerate(contents):
                if index % 2 == 1:
                    file.write(content + '\n')
        else:
            for content in contents:
                file.write(content + '\n')
        file.close()

    # 发送邮件方法
    def sendEmail(self, notice_contents):
        # 函数_format_addr()用来格式化一个邮件地址
        def _format_addr(s):
            name, addr = parseaddr(s)
            return formataddr((
                Header(name, 'utf-8').encode(),
                addr.encode('utf-8') if isinstance(addr, unicode) else addr))
        # Email地址和口令:
        from_addr = self.from_addr
        password = self.password
        # SMTP服务器地址:
        smtp_server = self.smtp_server
        # 收件人地址:
        to_addr = self.to_addr
        # 构造邮件
        msgtext = "\n".join(notice_contents)
        msg = MIMEText(msgtext, 'plain', 'utf-8')
        msg['From'] = _format_addr(u'Spider_jisilu_4爬虫通知<%s>' % from_addr)
        msg['To'] = _format_addr(u'管理员<%s>' % to_addr)
        msg['Subject'] = Header(u'Hi...如下内容符合筛选条件:'
                                +u'溢价率小于'+ str(self.premium_rate)+'%'+u',收益率大于'+str(self.rateofreturn)+'%', 'utf-8').encode()

        server = smtplib.SMTP_SSL(smtp_server, 465)  # 启用SSL发信, 端口一般是465
        # server = smtplib.SMTP(smtp_server, 25) 	# SMTP协议默认端口是25
        # server.set_debuglevel(1)		#可以打印出和SMTP服务器交互的所有信息
        server.login(from_addr, password)  # 登录SMTP服务器
        server.sendmail(from_addr, to_addr, msg.as_string())  # 发邮件
        server.quit()

    # 根据溢价率和税前收益率进行筛选 局部变量rate1、2分别为溢价率和税前收益率
    def myScreening(self, contents):
        notice_contents = []  # 定义list,用于存储大于预设阈值的数据
        for i, line in enumerate(contents):
            if line.split()[2] == "!":
                rate1 = float(line.split()[11][:-1])  # 溢价率，取出百分号的数字,并转成float类型
                rate2 = float(line.split()[21][:-1])  # 税前收益率，取出百分号的数字,并转成float类型
                price = float(line.split()[3]) #当前价格
            else:
                rate1 = float(line.split()[10][:-1])  # 溢价率，取出百分号的数字,并转成float类型
                rate2 = float(line.split()[20][:-1])  # 税前收益率，取出百分号的数字,并转成float类型
                price = float(line.split()[2])  # 当前价格
            if rate1 < self.premium_rate and rate2 > self.rateofreturn:  # 根据预设条件进行筛选
                notice_content = line.split()[0] + line.split()[1] \
                                 +' 当前价格'+str(price)+ ' 溢价率为' + str(rate1)+'%' +' 税前收益率为'+ str(rate2)+'%' +"\n"
                notice_contents.append(notice_content)
        return notice_contents

    # 开始方法
    def start(self):
        browser = self.setWebdrive()
        page = self.getPageSource(browser, self.url)
        contents = self.getContent(page)
        if not contents:
            print u"获取内容失败,请确认URL是否正确"
            return
        else:
            notice_contents = self.myScreening(contents)
            if notice_contents:
                self.sendEmail(notice_contents)
                print u"已发送邮件通知，请查收！"
            self.writeData(contents)
            print "内容已写入" + self.filename




# 实例化对象jsl
# 传入url
# 传入filename文件名
# 传入is_ssl的值,1为使用ssl认证,0为禁用ssl认证
# 传入single_line的值,1为获取单行数据,2为获取双行数据,默认为0获取所有数据
#(url, filename, is_ssl, write_in=0, premium_rate=8.00, rateofreturn=2.00)
jsl = JSL("https://www.jisilu.cn/data/cbnew/#cb", 'cb201905.txt', 0, 2, 8, 2)
# jsl = JSL("https://www.jisilu.cn/data/cf/#stock",'kkk2.txt', 0, 0)
# jsl = JSL("https://www.jisilu.cn/data/sfnew/#tlink_3",'kkk2.txt', 0, 0)	#更改xpath为//*[@id="flex3"]/tbody/tr
# 调用start方法
jsl.start()
