#!/usr/bin/python
#-*-coding: utf-8 -*-
"""
给自己发送短信提醒~~~~先尝试使用微信→_→毕竟免费哇，如若失败则使用nexmo
nexmo假定是可信的，so只要正常发送了请求就假定是短信发送成功
"""
from __future__ import unicode_literals
import requests
import platform
import json

with open(r'./cfg.json', 'r') as f:
    cfg = json.load(f)
_session = requests.Session()
#给飞信准备的
_session.headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cache-Control': 'no-cache',
    'Accept': '*/*',
    'Connection': 'close'
})

###Fetion API
_fetion_user = cfg["fetion"]["user"]
_fetion_pwd = cfg["fetion"]["password"]

###nexmo API
_nexmo_KEY = cfg["nexmo"]["KEY"]
_nexmo_SECERT = cfg["nexmo"]["SECERT"]
_nexmo_my_phone_number = cfg["nexmo"]["my_phone_number"]

###pushbullet
_pushbullet = cfg["pushbullet"]

if platform.system() != "Windows":
    requests.packages.urllib3.disable_warnings()

def pushbullet(title,sms):
    headers = {"Content-Type": "application/json"}
    post_data = {
        "type": "note",
        "title": title,
        "body": sms
    }
    a = _session.post("https://api.pushbullet.com/v2/pushes",
                      auth =(_pushbullet,""),
                      headers=headers,
                      data=json.dumps(post_data))
    if "error" in a.text:
        return False
    return True

def fetion(title,msg):
    url_space_login = 'http://f.10086.cn/huc/user/space/login.do'
    url_login = 'http://f.10086.cn/im/login/cklogin.action'
    url_sendmsg = 'http://f.10086.cn/im/user/sendMsgToMyselfs.action'
    post_data = {
        'mobilenum': _fetion_user,
        'password': _fetion_pwd,
        "m": "submit",
        "fr": "space",
        "backurl": "http://f.10086.cn/"
    }
    _session.post(url_space_login, data=post_data)
    _session.get(url_login)
    send = _session.post(url_sendmsg, data={'msg': title + " " + msg})
    if u"成功" in send.text:
        return True
    return False


def nexmo(title,message):
    baseurl = "https://rest.nexmo.com/sms/json"
    balance = _session.get("https://rest.nexmo.com/account/get-balance", params={
        "api_key": _nexmo_KEY,
        "api_secret": _nexmo_SECERT,
    }).json()["value"]
    info = _session.get(baseurl, params={
        "api_key": _nexmo_KEY,
        "api_secret": _nexmo_SECERT,
        "from": "xxxx",
        "type": "unicode",
        "to": _nexmo_my_phone_number,
        "text": u'{} nexmo余额为{}, {}'.format(title, balance, unicode(message, 'UTF-8'))})
    return info.status_code == 200


def sendMsg(title, msg):
    title, msg = unicode(title), unicode(msg)
    try:
        if pushbullet(title, msg):
            return True
    except Exception as e:
        print str(e)
    try:
        if fetion(title, msg):
            return True
    except Exception as e:
        print str(e)
    try:
        if nexmo(title, msg):
            return True
    except Exception as e:
        print str(e)
    return False


if __name__ == '__main__':
    print fetion("飞信","测试")
    # print nexmo("nexmo"."测试")
    for i in range(1):
        print i, sendMsg("测试", str(i))

