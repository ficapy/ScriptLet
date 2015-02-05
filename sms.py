#!/usr/bin/python
#-*-coding: utf-8 -*-
"""
给自己发送短信提醒~~~~先尝试使用飞信→_→毕竟免费哇，如若失败则使用nexmo
nexmo假定是可信的，so只要正常发送了请求就假定是短信发送成功
"""
import requests
import platform
import json

with open(r'./smscfg.json', 'r') as f:
    cfg = json.load(f)
_session = requests.Session()

###Fetion API
_fetion_user = cfg["fetion"]["user"]
_fetion_pwd = cfg["fetion"]["password"]

###nexmo API
_nexmo_KEY = cfg["nexmo"]["KEY"]
_nexmo_SECERT = cfg["nexmo"]["SECERT"]
_nexmo_my_phone_number = cfg["nexmo"]["my_phone_number"]

if platform.system() != "Windows":
    requests.packages.urllib3.disable_warnings()

def fetion(msg):
    url_space_login = 'http://f.10086.cn/huc/user/space/login.do?m=submit&fr=space'
    url_login = 'http://f.10086.cn/im/login/cklogin.action'
    url_sendmsg = 'http://f.10086.cn/im/user/sendMsgToMyselfs.action'
    parameter = {'mobilenum': _fetion_user, 'password': _fetion_pwd}
    _session.post(url_space_login, data=parameter)
    _session.get(url_login)
    send = _session.post(url_sendmsg, data={'msg': msg})
    if u"成功" in send.text:
        return True
    return False


def nexmo(message):
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
        "text": u'nexmo余额为{}, {}'.format(balance, unicode(message, 'UTF-8'))})
    return info.status_code == 200


def sendMsg(msg):
    if not fetion(msg):
        if not nexmo(msg):
            return False
    return True


if __name__ == '__main__':
    for i in range(3):
        print i,sendMsg(str(i))