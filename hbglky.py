#!/bin/env/python
#encoding=utf-8
#Create On: 2015-1-30

"""
需要提前订好班车票哇,出票时间不固定,觉得挺简单就写了这个，可以买票的时候即刻提醒
→→→昨天凌晨收到短信~~~刚才订票了 嗯 还是有点效果的 因为提示只有18张票了
"""

import requests
import random
from datetime import date, timedelta, datetime
from pyquery import PyQuery as pq
from sms import sendMsg
import platform
import os
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

baseurl = "http://hbglky.com/bccx.asp"
_session = requests.Session()

if platform.system() != "Windows":
    requests.packages.urllib3.disable_warnings()


@sched.scheduled_job('interval', hours=1)
def check(year=2015, month=2, day=14, future=True):
    if date(year, month, day) - timedelta(days=3 if future else 0) < date.today():
        print "丫是不是输错时间了~~~~~~~"
        sendMsg("目测超过设定时间还没有发现可购买的票")
        #以下兼容windows低版本python
        os.kill(os.getpid(), 15)
    params = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Host": "hbglky.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0"
    }
    _session.get("http://hbglky.com/service/default.shtml",params=params)
    info = _session.post(baseurl, data={"Input.x": random.randint(1,40),
                                        "Input.y": random.randint(1,20),
                                        "Terminal": "地点信息".decode("UTF-8").encode("GBK"),
                                        "search_source": 0,
                                        "Search_Days": (date(year, month, day) - date.today()).days
    },params=params.update({"Referer":"http://hbglky.com/service/default.shtml"}))
    info.encoding = "gb2312"
    d = pq(info.text)
    #车次数由HTML源码JS而来，TABLE的行数
    #0表示无，-1表示返回了错误的网页
    times = d("#a tr").length - 1
    nobuy = info.text.count(u'nobuy.gif') - 1
    e = zip(d("#a tr:first").text().split(),d("#a tr").eq(1).text().split())
    if times > 1 and times > nobuy:
        sendMsg(u"有{}趟汽车票可以购买,信息如下~~{}".format(times - nobuy,"  ".join(":".join(x) for x in e)))
        os.kill(os.getpid(), 15)
    elif times == -1:
        sendMsg("汽车票查询程序出现异常")
        os.kill(os.getpid(), 15)
    else:
        print str(datetime.today()) + " 没有票"

#check(2015,1,3)  #测试,记住先更改地点信息
sched.start()