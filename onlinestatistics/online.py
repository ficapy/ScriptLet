# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Create on:2015.2.2
#GB18030

from __future__ import unicode_literals
import requests
from collections import deque
from pyquery import PyQuery as pq
import platform
import json
import time
import math
from sms import sendMsg
from db import insert
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

s = requests.Session()

log = logging.getLogger(__name__)
#log默认等级为warning
log.setLevel(logging.DEBUG)
format = "%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(format, datefmt=datefmt)

filelog = logging.FileHandler(r'./v2exonlinelog.txt')
filelog.setLevel(logging.INFO)
filelog.setFormatter(formatter)
log.addHandler(filelog)

console_log = logging.StreamHandler()
console_log.setFormatter(formatter)
console_log.setLevel(logging.DEBUG)
log.addHandler(console_log)

init = deque([1] * int(36 * 3600 / 600), maxlen=int(36 * 3600 / 600))


def avg(num=True):
    global init
    init.append(num)
    return sum(init)


def fetch(html):
    d = pq(html)
    num = d(".item_title").length
    #标题
    title = [d(".item_title").eq(i).text() for i in range(num)]
    #提问人→_→此处发现pyquery有bug
    people = [d(".small.fade").eq(i).find("strong:first").text().split()[0] for i in range(num)]
    #当前回复数
    reply = [d(".cell.item").eq(i).find("td:last").text() for i in range(num)]
    #当前在线人数
    if d("#Bottom .inner strong").text().split().__len__() > 1:
        online = d("#Bottom .inner strong").text().split()[-2]
    else:
        online = 0
    return int(online), \
           json.dumps({"content": [{"title": title,
                                    "questioner": questioner,
                                    "replynum": (replynum or 0)} for title, questioner, replynum in
                                   zip(title, people, reply)]
           })


@sched.scheduled_job('interval', minutes=10)
def grabnumber():
    try:
        requests.packages.urllib3.disable_warnings()
        params = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "www.v2ex.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0"
        }
        for i in xrange(3):
            web = s.get("http://www.v2ex.com/?tab=r2", timeout=60, verify=False, params=params)
            if 199 < web.status_code < 300 and all(fetch(web.text)):
                log.debug("返回码为{},当前在线人数为{}".format(int(web.status_code),fetch(web.text)[0]))
                avg()
                break
            time.sleep(math.pow(2, i+1))
        else:
            #36小时内正常抓取没有达到80%则发送短信提醒
            log.error("错误码为{}".format(int(web.status_code)))
            false = avg(False)
            if false < int(36 * 3600 / 600 * 0.8):
                sendMsg("v2ex", "V2EXonline脚本36小时内正常返回不足80%,请检查")
        info = fetch(web.text)
        insert(content=info[-1], online=info[0], status_code=int(web.status_code))
    except Exception as e:
        logging.exception(e)
        log.warning(str(e))
    return

# grabnumber()
sched.start()

