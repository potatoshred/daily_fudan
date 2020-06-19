from requests import session
from lxml import etree
from sys import exit as sys_exit
from os import path as os_path
from json import loads as json_loads
import time

class Fudan:
    """
    建立与复旦服务器的会话，执行登录/登出操作
    """
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"

    # 初始化会话
    def __init__(self,
                 uid, psw,
                 url_login='https://uis.fudan.edu.cn/authserver/login'):
        """
        初始化一个session，及登录信息
        :param uid: 学号
        :param psw: 密码
        :param url_login: 登录页，默认服务为空
        """
        self.session = session()
        self.session.headers['User-Agent'] = self.UA
        self.url_login = url_login

        self.uid = uid
        self.psw = psw

    def _page_init(self):
        """
        检查是否能打开登录页面
        :return: 登录页page source
        """
        print("◉Initiating——", end='')
        page_login = self.session.get(self.url_login)

        print("return status code",
              page_login.status_code)

        if page_login.status_code == 200:
            print("◉Initiated——", end="")
            return page_login.text
        else:
            print("◉Fail to open Login Page, Check your Internet connection\n")
            self.close()

    def login(self):
        """
        执行登录
        """
        page_login = self._page_init()

        print("parsing Login page——", end="")
        html = etree.HTML(page_login, etree.HTMLParser())

        print("getting tokens")
        data = {
            "username": self.uid,
            "password": self.psw,
            "service" : "https://zlapp.fudan.edu.cn/site/ncov/fudanDaily"
        }

        # 获取登录页上的令牌
        data.update(
                zip(
                        html.xpath("/html/body/form/input/@name"),
                        html.xpath("/html/body/form/input/@value")
                )
        )

        headers = {
            "Host"      : "uis.fudan.edu.cn",
            "Origin"    : "https://uis.fudan.edu.cn",
            "Referer"   : self.url_login,
            "User-Agent": self.UA
        }

        print("◉Login ing——", end="")
        post = self.session.post(
                self.url_login,
                data=data,
                headers=headers,
                allow_redirects=False)

        print("return status code", post.status_code)

        if post.status_code == 302:
            print("\n***********************"
                  "\n◉登录成功"
                  "\n***********************\n")
        else:
            print("◉登录失败，请检查账号信息")
            self.close()

    def logout(self):
        """
        执行登出
        """
        exit_url = 'https://uis.fudan.edu.cn/authserver/logout?service=/authserver/login'
        expire = self.session.get(exit_url).headers.get('Set-Cookie')
        # print(expire)

        if '01-Jan-1970' in expire:
            print("◉登出完毕")
        else:
            print("◉登出异常")

    def close(self):
        """
        执行登出并关闭会话
        """
        self.logout()
        self.session.close()
        print("◉关闭会话")
        print("************************")
        input("回车键退出")
        sys_exit()

class Zlapp(Fudan):
    last_info = ''

    def check(self):
        """
        检查
        """
        print("◉检测是否已提交")
        get_info = self.session.get(
                'https://zlapp.fudan.edu.cn/ncov/wap/fudan/get-info')
        last_info = json_loads(get_info.text)

        print("◉上一次提交日期为:", last_info["d"]["info"]["date"])

        position = last_info["d"]["info"]['geo_api_info']
        position = json_loads(position)

        print("◉上一次提交地址为:", position['formattedAddress'])
        # print("◉上一次提交GPS为", position["position"])

        today = time.strftime("%Y%m%d", time.localtime())
        if last_info["d"]["info"]["date"] == today:
            print("\n*******今日已提交*******")
            self.close()
        else:
            print("\n\n*******未提交*******")
            self.last_info = last_info["d"]["info"]

    def checkin(self):
        """
        提交
        """
        headers = {
            "Host"      : "zlapp.fudan.edu.cn",
            "Referer"   : "https://zlapp.fudan.edu.cn/site/ncov/fudanDaily?from=history",
            "DNT"       : "1",
            "TE"        : "Trailers",
            "User-Agent": self.UA
        }

        print("\n\n◉◉提交中")
        save = self.session.post(
                'https://zlapp.fudan.edu.cn/ncov/wap/fudan/save',
                data=self.last_info,
                headers=headers,
                allow_redirects=False)

        save_msg = json_loads(save.text)["m"]
        print(save_msg,'\n\n')

        # 再检查一遍
        self.check()


def get_account():
    """
    获取账号信息
    """
    print("\n\n请仔细阅读以下日志！！\n请仔细阅读以下日志！！！！\n请仔细阅读以下日志！！！！！！\n\n")
    if os_path.exists("account.txt"):
        print("读取账号中……")
        with open("account.txt", "r") as old:
            raw = old.readlines()
        if (raw[0][:3] != "uid") or (len(raw[0]) < 10):
            print("account.txt 内容无效, 请手动修改内容")
            sys_exit()
        uid = (raw[0].split(":"))[1].strip()
        psw = (raw[1].split(":"))[1].strip()

    else:
        print("未找到account.txt, 判断为首次运行, 请接下来依次输入学号密码")
        uid = input("学号：")
        psw = input("密码：")
        with open("account.txt", "w") as new:
            tmp = "uid:" + uid + "\npsw:" + psw + "\n\n\n以上两行冒号后分别写上学号密码，不要加空格/换行，谢谢\n\n请注意文件安全，不要放在明显位置\n\n可以从dailyFudan.exe创建快捷方式到桌面"
            new.write(tmp)
        print("账号已保存在目录下account.txt，请注意文件安全，不要放在明显位置\n\n建议拉个快捷方式到桌面")

    return uid, psw
if __name__ == '__main__':
    uid, psw = get_account()
    # print(uid, psw)
    zlapp_login = 'https://uis.fudan.edu.cn/authserver/login?' \
                  'service=https://zlapp.fudan.edu.cn/site/ncov/fudanDaily'
    daily_fudan = Zlapp(uid, psw, url_login=zlapp_login)
    daily_fudan.login()
    daily_fudan.check()
    daily_fudan.checkin()

    daily_fudan.close()
