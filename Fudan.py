from lxml import etree
from requests import session
import time, json
import logging, sys
#from requests_html import HTMLSession

LOG_PATH = sys.path[0] + "/app.log"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(filename=LOG_PATH,format=LOG_FORMAT,datefmt=DATE_FORMAT,level='INFO')

class Fudan:
    """
    建立与复旦服务器的会话，执行登录/登出操作
    """
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"

    # 初始化会话
    def __init__(self,
                 uid, psw,
                 url_login='https://uis.fudan.edu.cn/authserver/login',
                 host='uis.fudan.edu.cn',
                 origin='http://uis.fudan.edu.cn'):
        """
        初始化一个session，及登录信息
        :param uid: 学号
        :param psw: 密码
        :param url_login: 登录页，默认服务为空
        """
        self.session = session()
        self.session.headers['User-Agent'] = self.UA
        self.url_login = url_login
        self.host = host
        self.origin = origin

        self.uid = uid
        self.psw = psw
        self.status = False  # whether have run the submit command

    def _page_init(self):
        """
        检查是否能打开登录页面
        :return: 登录页page source
        """
        page_login = self.session.get(self.url_login)
        logging.info("Connecting to Internet, status code = {}".format(page_login.status_code))

        if page_login.status_code == 200:
            logging.info("Connect successful")
            return page_login.text
        else:
            raise RuntimeError("Fail to open Login Page, Check your Internet connection")
            
    def login(self,service='https://zlapp.fudan.edu.cn/site/ncov/fudanDaily'):
        """
        执行登录
        """
        page_login = self._page_init()

        #print("parsing Login page——", end="")
        html = etree.HTML(page_login, etree.HTMLParser())

        #print("getting tokens")
        data = {
            "username": self.uid,
            "password": self.psw,
            "service" : service
        }

        # 获取登录页上的令牌
        data.update(
                zip(
                        html.xpath("/html/body/form/input/@name"),
                        html.xpath("/html/body/form/input/@value")
                )
        )

        headers = {
            "Host"      : self.host,
            "Origin"    : self.origin,
            "Referer"   : self.url_login,
            "User-Agent": self.UA
        }

        #print("◉Login ing——", end="")
        post = self.session.post(
                self.url_login,
                data=data,
                headers=headers,
                allow_redirects=False)

        logging.info("Login, status code = {}".format(post.status_code))

        if post.status_code == 302:
            logging.info("Login successful")
        else:
            raise RuntimeError("登录失败，请检查账号信息")

    def logout(self,url='https://uis.fudan.edu.cn/authserver/logout?service=/authserver/login'):
        """
        执行登出
        """
        expire = self.session.get(url).headers.get('Set-Cookie')
        # print(expire)

        if '01-Jan-1970' in expire:
            logging.info("登出完毕")
        else:
            logging.warning("登出异常")

    def close(self):
        """
        执行登出并关闭会话
        """
        self.logout()
        self.session.close()
        logging.info("关闭会话")

class Zlapp(Fudan):
    '''
    检查是否已提交平安复旦的信息，并根据上一次填写的地理位置填报
    '''

    last_info = ''

    def check(self):
        """
        check whether submitted today, log last submission date and address
        """
        #print("◉检测是否已提交")
        get_info = self.session.get(
                'https://zlapp.fudan.edu.cn/ncov/wap/fudan/get-info')
        last_info = get_info.json()

        logging.info("Last submission date: {}".format(last_info["d"]["info"]["date"]))

        position = last_info["d"]["info"]['geo_api_info']
        position = json.loads(position)

        logging.info("Last submission address: {}".format(position['formattedAddress']))
        # print("◉上一次提交GPS为", position["position"])

        today = time.strftime("%Y%m%d", time.localtime())

        if last_info["d"]["info"]["date"] == today and self.status == False:
            raise AssertionError("今日已提交")
        elif last_info["d"]["info"]["date"] == today and self.status == True:
            logging.info("Submission successful")
        else:
            logging.info("Haven't submitted today, starting submission")
            self.last_info = last_info["d"]["info"]

    def checkin(self):
        """
        submit, and log submission status
        """
        headers = {
            "Host"      : "zlapp.fudan.edu.cn",
            "Referer"   : "https://zlapp.fudan.edu.cn/site/ncov/fudanDaily?from=history",
            "DNT"       : "1",
            "TE"        : "Trailers",
            "User-Agent": self.UA
        }

        #print("\n\n◉◉提交中")

        geo_api_info = json.loads(self.last_info["geo_api_info"])
        province = geo_api_info["addressComponent"].get("province", "")
        city = geo_api_info["addressComponent"].get("city", "")
        district = geo_api_info["addressComponent"].get("district", "")
        self.last_info.update(
                {
                    "tw"      : "13",
                    "province": province,
                    "city"    : city,
                    "area"    : " ".join((province, city, district))
                }
        )
        # print(self.last_info)

        save = self.session.post(
                'https://zlapp.fudan.edu.cn/ncov/wap/fudan/save',
                data=self.last_info,
                headers=headers,
                allow_redirects=False)

        save_msg = json.loads(save.text)["m"]
        logging.info("".format(save_msg))
        self.status = True