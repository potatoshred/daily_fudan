import time
from json import loads as json_loads
from json import dumps as json_dumps
from os import path as os_path
from sys import exit as sys_exit
from sys import argv as sys_argv

from lxml import etree
from requests import session
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

# WeChat notice
#get token via http://iyuu.cn/
import requests
from captcha_break import DailyFDCaptcha
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
def iyuu(IYUU_TOKEN):
    url = f"https://iyuu.cn/{IYUU_TOKEN}.send"
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    def send(text, desp=""):
        Form = {'text': text, 'desp': desp}
        return requests.post(url, data=Form, headers=headers, verify=False)
    return send

# fix random area bug
def set_q(iterO):
    res = list()
    for item in iterO:
        if item not in res:
            res.append(item)
    return res



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
        logging.debug("Initiating——")
        page_login = self.session.get(self.url_login)

        logging.debug("return status code " + str(page_login.status_code))

        if page_login.status_code == 200:
            logging.debug("Initiated——")
            return page_login.text
        else:
            logging.debug("Fail to open Login Page, Check your Internet connection\n")
            self.close()

    def login(self):
        """
        执行登录
        """
        page_login = self._page_init()

        logging.debug("parsing Login page——")
        html = etree.HTML(page_login, etree.HTMLParser())

        logging.debug("getting tokens")
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

        logging.debug("Login ing——")
        post = self.session.post(
                self.url_login,
                data=data,
                headers=headers,
                allow_redirects=False)

        logging.debug("return status code %d" % post.status_code)

        if post.status_code == 302:
            logging.debug("登录成功")
            return True
        else:
            logging.debug("登录失败，请检查账号信息")
            self.close()
            return False

    def logout(self):
        """
        执行登出
        """
        exit_url = 'https://uis.fudan.edu.cn/authserver/logout?service=/authserver/login'
        expire = self.session.get(exit_url).headers.get('Set-Cookie')

        if '01-Jan-1970' in expire:
            logging.debug("登出完毕")
        else:
            logging.debug("登出异常")

    def close(self):
        """
        执行登出并关闭会话
        """
        self.logout()
        self.session.close()
        logging.debug("关闭会话")
        # sys_exit() 通知完成再退出 注释掉

class Zlapp(Fudan):
    last_info = ''

    def check(self):
        """
        检查
        """
        logging.debug("检测是否已提交")
        get_info = self.session.get(
                'https://zlapp.fudan.edu.cn/ncov/wap/fudan/get-info')
        last_info = get_info.json()

        logging.info("上一次提交日期为: %s " % last_info["d"]["info"]["date"])

        position = last_info["d"]["info"]['geo_api_info']
        position = json_loads(position)

        logging.info("上一次提交地址为: %s" % position['formattedAddress'])
        # logging.debug("上一次提交GPS为", position["position"])

        today = time.strftime("%Y%m%d", time.localtime())

        if last_info["d"]["info"]["date"] == today:
            logging.info("今日已提交")
            self.close()
            global gl_info
            gl_info = last_info
            geo_api_info = json_loads(last_info["d"]["info"]["geo_api_info"])
            province = geo_api_info["addressComponent"].get("province", "")
            city = geo_api_info["addressComponent"].get("city", "") or province
            district = geo_api_info["addressComponent"].get("district", "")
            gl_info['dailyFudan'] = " ".join(set_q((province, city, district)))
            gl_info = json_dumps(gl_info, indent=4, ensure_ascii=False)
            return True
        else:
            logging.info("未提交")
            self.last_info = last_info["d"]["info"]
            return False

    def checkin(self, captcha):
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

        logging.debug("提交中")

        geo_api_info = json_loads(self.last_info["geo_api_info"])
        province = geo_api_info["addressComponent"].get("province", "")
        city = geo_api_info["addressComponent"].get("city", "") or province
        district = geo_api_info["addressComponent"].get("district", "")
        self.last_info.update(
                {
                    "tw"      : "13",
                    "province": province,
                    "city"    : city,
                    "area"    : " ".join(set_q((province, city, district))),
                    "ismoved" : 0
                }
        )
        # logging.debug(self.last_info)
        for i in range(3):
            captcha_text = captcha()
            #captcha_text = 'abcd'
            self.last_info.update({
                'sfzx': 1,
                'code': captcha_text
            })
            save = self.session.post(
                    'https://zlapp.fudan.edu.cn/ncov/wap/fudan/save',
                    data=self.last_info,
                    headers=headers,
                    allow_redirects=False)

            save_msg = json_loads(save.text)["m"]
            logging.info(save_msg)
            if save_msg != '验证码错误':
                break
            else:
                captcha.reportError()
                print('captcha.reportError')

def get_account():
    """
    获取账号信息
    """
    uid, psw, *IYUU_TOKEN = sys_argv[1].strip().split(' ')
    return uid, psw, IYUU_TOKEN

gl_info = "快去手动填写！"
if __name__ == '__main__':
    uid, psw, IYUU_TOKE = get_account()
    if IYUU_TOKE: #有token则通知，无token不通知
        if len(IYUU_TOKE) != 3:
            logging.error("请正确配置微信通知功能和验证码打码功能～\n")
            sys_exit(1)
        uname = IYUU_TOKE[1]
        pwd = IYUU_TOKE[2]
        IYUU_TOKE = IYUU_TOKE[0]
        iy_info = iyuu(IYUU_TOKE)
    else:
        def iy_info(text, desp=""):
            pass
        logging.error("请按readme操作，以正确完成配置～\n")
        sys_exit(1)

    # logging.debug("ACCOUNT：" + uid + psw)
    zlapp_login = 'https://uis.fudan.edu.cn/authserver/login?' \
                  'service=https://zlapp.fudan.edu.cn/site/ncov/fudanDaily'
    daily_fudan = Zlapp(uid, psw, url_login=zlapp_login)
    if not daily_fudan.login():
        iy_info("平安复旦：登陆失败", gl_info)
        sys_exit()

    if daily_fudan.check():
        iy_info("平安复旦：今日已提交", gl_info)
        sys_exit()

    def captcha_info(message):
        iy_info(message, gl_info)
    captcha = DailyFDCaptcha(uname,pwd,daily_fudan,captcha_info)
    daily_fudan.checkin(captcha)

    # 再检查一遍
    if daily_fudan.check():
        iy_info("平安复旦：今日已提交", gl_info)
    else:
        iy_info("平安复旦：本次提交失败", gl_info)

    daily_fudan.close()
    sys_exit()