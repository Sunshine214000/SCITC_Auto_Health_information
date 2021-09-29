# -*- coding: utf-8 -*-

"""
@author: Sunshine
@software: PyCharm
@file: main.py
@time: 2021/9/29 10:14
"""

import requests
import yaml
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header


class Qmsg:
    '''Qmsg酱通知类'''

    def __init__(self, key, qq, isGroup):
        # config={'key':'*****','qq':'*****','isgroup':0}
        self.key = key
        self.qq = qq
        self.isGroup = isGroup
        self.configIsCorrect = self.isCorrectConfig()

    def isCorrectConfig(self):
        # 简单检查key和qq是否合法
        for item in [self.key, self.qq]:
            if not type(item) == str:
                return 0
            if len(item) == 0:
                return 0
            if "*" in item:
                return 0
        return 1

    def send(self, msg):
        # msg：要发送的信息|消息推送函数
        msg = str(msg)
        # 简单检查配置
        if self.configIsCorrect:
            sendtype = 'group/' if self.isGroup else 'send/'
            res = requests.post(url='https://qmsg.zendee.cn/' + sendtype +
                                    self.key,
                                data={
                                    'msg': msg,
                                    'qq': self.qq
                                })
            return str(res)
            #    code = res.json()['code']
            #    print(code)
        else:
            print('Qmsg配置出错')
            return 'Qmsg配置出错'


class Smtp:
    '''邮箱推送类'''

    def __init__(self, host, user, key, sender, receivers):
        self.host = host
        self.user = user
        self.key = key
        self.sender = sender
        self.receivers = receivers
        self.configIsCorrect = self.isCorrectConfig()

    def isCorrectConfig(self):
        # 简单检查邮箱地址或API地址是否合法
        if type(self.receivers) != list:
            return 0
        for item in [self.host, self.user, self.key, self.sender
                     ] + self.receivers:
            if not type(item) == str:
                return 0
            if len(item) == 0:
                return 0
            if "*" in item:
                return 0
        return 1

    def sendmail(self, msg, title):
        if self.configIsCorrect:
            mail = MIMEText(msg, 'plain', 'utf-8')
            mail['Subject'] = Header(title, 'utf-8')

            smtpObj = smtplib.SMTP()
            smtpObj.connect(self.host, 587)
            smtpObj.login(self.user, self.key)
            smtpObj.sendmail(self.sender, self.receivers, mail.as_string())
            print("邮件发送成功")
        else:
            print('邮件配置出错')
            return '邮件配置出错'


def loadYml(ymlFileName='config.yml'):
    with open(ymlFileName, 'r', encoding="utf-8") as file:
        item = yaml.load(file, Loader=yaml.FullLoader)
        return item


def sign(user):
    url = 'http://zhcx.scitc.com.cn/weixin/HealthAdd.php?'
    headers = {
        'host': 'zhcx.scitc.com.cn',
        'Connection': 'keep-alive',
        'Accept': 'text/html, */*; q=0.01',
        'User-Agent':
            'Mozilla/5.0 (Linux; Android 10; ANA-AN00 Build/HUAWEIANA-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/3117 MMWEBSDK/20210601 Mobile Safari/537.36 MMWEBID/371 MicroMessenger/8.0.11.1960(0x28000B33) Process/toolsmp WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'http://zhcx.scitc.com.cn',
        'Referer': 'http://zhcx.scitc.com.cn/weixin/HealthAdd.php',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-CN;q=0.8,en-US;q=0.7,en;q=0.6',
        'Cookie': user['Cookie_openid'],  # 登录信息
    }
    IncomingValue = {
        'InSchoolYN': user['InSchool'],
        'GoOutYN': user['GoOutYN'],
        'Temperature': '36.6',
        'Info': '',
        'HealthAction': '正常　',
        'Other': '',
        'latitude': user['lat'],
        'longitude': user['lon'],
        'speed': '0.0',
        'accuracy': '15.0',
        'networkType': 'wifi',
        'action': 'save',
    }
    resp = requests.post(url, data=IncomingValue, headers=headers, stream=True)
    sendStr = '用户名：' + user['username'] + '\n' + '日期：' + time.strftime("%Y-%m-%d %H:%M:%S",
                                                                       time.localtime()) + '\n' + f'状态码：{resp.status_code}\n{resp.reason}\n{resp.text}'
    print(sendStr)

    Qmsg(user['qmsg_key'], user['qmsg_qq'], user['isGroup']).send('智慧川信公众号签到情况：' + '\n' + sendStr)
    Smtp('smtp.qq.com', '*****@qq.com', '**********', '*********@qq.com', [user['receiving_mailbox']]).sendmail(sendStr,
                                                                                                                '智慧川信公众号签到情况')
    resp.close()


def main():
    config = loadYml()
    print(config)
    for user in config['users']:
        sign(user)


def handler(event, context):
    main()


# 腾讯云的入口函数
def main_handler(event, context):
    main()
    return 'ok'


# 本地测试
if __name__ == '__main__':
    main()
