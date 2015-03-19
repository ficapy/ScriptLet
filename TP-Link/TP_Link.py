#!/usr/bin/env python
# coding:utf-8

import requests
from base64 import b64encode
from urllib2 import quote
import re
import time
import traceback
from sys import argv

PWD = "密码---"
login_url = 'http://192.168.1.1'

# 登陆
# function Win(buttonId)
# {
# var auth;
# 	password = document.getElementById("password").value;
# 	auth = "Basic "+Base64Encoding("admin:"+password);
# 	document.cookie = "Authorization="+escape(auth);
# 	document.cookie = "subType="+buttonId;
# 	getCookie();
#     location.reload();
#
# }


class Failed(Exception):
    def __init__(self, msg, r):
        self.msg = msg
        self.r = r


s = requests.Session()


def login():
    a = s.get(login_url, cookies={
        "Authorization": quote("Basic " + b64encode("admin:" + PWD)),
        "subType": "pcSub",
        "TPLoginTimes": "1"
    })
    if 5000 > len(a.text) > 3000:
        # 返回csrf
        return re.search("csrf_token.{3}\"(\d+)\"", a.text).group(1)
    else:
        raise Failed(u"login error\n", a.text)


def control(tp, csrf):
    # 获取13位时间戳
    # time_now = ''.join(map(lambda x:x.ljust(3,'0'),str(time.time()).split('.')))
    time_now = ('%13.3f' % time.time()).replace('.', '')
    b = s.get(
        "http://192.168.1.1/cgi-bin/linkstatus.cgi?type={}&time={}&CSRFToken={}".format('%1d' % tp, time_now, csrf),
        cookies={
            "Authorization": quote("Basic " + b64encode("admin:" + PWD)),
            "subType": "pcSub",
            "TPLoginTimes": "1"
        })
    if len(b.text) == 0:
        return True
    else:
        raise Failed(u"unknow error\n", b.text)


def main(tp):
    try:
        csrf = login()
        control(tp, csrf)
    except Failed as e:
        print e.msg, e.r
        print traceback.print_exc()


if __name__ == "__main__":
    # 1为连接，0为断开
    if not raw_input("pls type enter if you want connect,or type others"):
        main(1)
        print "connect succeed"
    else:
        main(0)
        print "close complete"
