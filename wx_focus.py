import time
import subprocess
import urllib.request
import json

# 当关注的微信群触发关键字消息的时候发送桌面通知
# 仅支持MAC
# 先安装 https://github.com/MustangYM/WeChatExtension-ForMac

focus_title = ['软件', '软工']
keywords = ['签到', '打卡', '签']
BASE_URL = "http://127.0.0.1:52700/wechat-plugin/"


def get_body(url):
    with urllib.request.urlopen(url) as response:
        body = response.read()
    return json.loads(body)


def notify(title, text):
    CMD = '''
          on run argv
            display notification (item 2 of argv) with title (item 1 of argv)
          end run
          '''
    subprocess.call(['osascript', '-e', CMD, title, text])


user_info = get_body(BASE_URL + "user")

focus_room = [x['userId'] for x in user_info if any(i in x['title'] for i in focus_title)]

while True:
    for i in focus_room:
        x = get_body(BASE_URL + 'chatlog?userId={}&count=3'.format(i))
        for message in x:
            m = message['copyText']
            if any(i in m for i in keywords):
                notify(title='签到', text=m)
                time.sleep(10)
                break
        else:
            continue
        break
    print(time.strftime("%H:%M:%S"), "loop 10 seconds")
    time.sleep(10)
