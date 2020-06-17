import requests
import json
import os.path
import os
import sys
from lxml import etree
from datetime import datetime


class Zlapp:

    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"
    login_url = r"https://uis.fudan.edu.cn/authserver/login?service=https%3A%2F%2Fzlapp.fudan.edu.cn%2Fa_fudanzlapp%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fzlapp.fudan.edu.cn%252Fsite%252Fncov%252FfudanDaily%253Ffrom%253Dhistory%26from%3Dwap"

    def __init__(self, uid, psw):
        print("start session\n")
        self.zlapp_sess = requests.session()
        self.zlapp_sess.headers['User-Agent'] = self.UA
        self.uid = uid
        self.psw = psw

    def _start(self):
        print("◉Initiating Login Page")
        start = self.zlapp_sess.get(self.login_url)
        print("return status code", start.status_code)
        if start.status_code == 200:
            print("◉Initiated")
            return start
        else:
            print("Fail to open Login Page, Check your Internet connection\n")
            self.close()

    def login(self):
        start = self._start()

        print("parsing Login page")
        html = etree.HTML(start.text, etree.HTMLParser())

        print("getting tokens")
        parms = {
            "username": self.uid,
            "password": self.psw,
            "lt": "",
            "dllt": "userNamePasswordLogin",
            "execution": "",
            "service": "https://zlapp.fudan.edu.cn/a_fudanzlapp/api/sso/index?redirect=https%3A%2F%2Fzlapp.fudan.edu.cn%2Fsite%2Fncov%2FfudanDaily%3Ffrom%3Dhistory&from=wap",
            "_eventId": "submit",
            "rmShown": "1"
        }

        tokens = html.xpath("/html/body/form/input/@value")
        parms["lt"] = tokens[0]
        parms["execution"] = tokens[2]

        headers = {
            "Host": "uis.fudan.edu.cn",
            "Origin": "https://uis.fudan.edu.cn",
            "Referer": "https://uis.fudan.edu.cn/authserver/login?service=https%3A%2F%2Fzlapp.fudan.edu.cn%2Fa_fudanzlapp%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fzlapp.fudan.edu.cn%252Fsite%252Fncov%252FfudanDaily%253Ffrom%253Dhistory%26from%3Dwap",
            "User-Agent": self.UA
        }

        print("◉Login ing")
        post = self.zlapp_sess.post(
            self.login_url, data=parms, headers=headers, allow_redirects=False)

        print("return status code", post.status_code)

        if post.status_code == 302:
            print("◉登录成功")
        else:
            print("◉登录失败，请检查account.txt中账号信息")
            self.close()

    def check(self):
        print("◉检测是否已提交")
        get_info = self.zlapp_sess.get(
            'https://zlapp.fudan.edu.cn/ncov/wap/fudan/get-info')
        last_info = json.loads(get_info.text)

        print("◉上一次提交日期为", last_info["d"]["info"]["date"])
        if last_info["d"]["info"]["date"] == self.date():
            print("\n\n*******今日已提交*******\n")
            self.close()

        print("\n\n*******未提交*******")
        self.last_info = last_info["d"]["info"]

    def checkin(self):
        headers = {
            "Host": "zlapp.fudan.edu.cn",
            "Referer": "https://zlapp.fudan.edu.cn/site/ncov/fudanDaily?from=history",
            "DNT": "1",
            "TE": "Trailers",
            "User-Agent": self.UA
        }

        print("\n\n◉◉提交中\n\n")
        save = self.zlapp_sess.post(
            'https://zlapp.fudan.edu.cn/ncov/wap/fudan/save', data=self.last_info, headers=headers, allow_redirects=False)

        save_msg = json.loads(save.text)["m"]

        if "已经" in save_msg:
            print("********提交成功*******")
            self.close()

        else:
            print("*****返回信息异常， 检查中*******\n\n")
            self.check()

    def close(self):
        self._logout()
        self.zlapp_sess.close()
        print("\nsession closed")
        input("\n\n回车键退出")
        sys.exit(1)

    def _logout(self):
        exit_url = 'https://uis.fudan.edu.cn/authserver/logout?service=/authserver/login'
        expire = self.zlapp_sess.get(exit_url).headers.get('Set-Cookie')
        if '01-Jan-1970' in expire:
            print("\n\n◉登出完毕")
        else:
            print("\n\n◉登出异常")

    @staticmethod
    def date():
        now = datetime.now()
        return "%d%02d%02d" % (now.year, now.month, now.day)


if __name__ == "__main__":

    print("\n\n请仔细阅读以下日志！！\n请仔细阅读以下日志！！！！\n请仔细阅读以下日志！！！！！！\n\n")
    if os.path.exists("account.txt"):
        print("读取账号缓存中")
        with open("account.txt", "r") as old:
            raw = old.readlines()
        if (raw[0][:3]!="uid") or (len(raw[0])<10):
            print("account.txt 内容无效, 请手动修改内容")
            sys.exit()
        uid = (raw[0].split(":"))[1].strip()
        psw = (raw[1].split(":"))[1].strip()

        
    else:
        print("未找到account.txt, 判断为首次运行, 请接下来依次输入学号密码")
        uid = input("学号：")
        psw = input("密码：")
        with open("account.txt", "w") as new:
            tmp = "uid:"+uid+"\npsw:"+psw+"\n\n\n以上两行冒号后分别写上学号密码，不要加空格/换行，谢谢\n\n请注意文件安全，不要放在明显位置\n\n可以从dailyFudan.exe创建快捷方式到桌面"
            new.write(tmp)
        print("账号已保存在目录下account.txt，请注意文件安全，不要放在明显位置\n\n建议从dailyFudan.exe创建快捷方式到桌面")



    daily_fudan = Zlapp(uid, psw)
    daily_fudan.login()
    daily_fudan.check()
    daily_fudan.checkin()

    daily_fudan.close()
