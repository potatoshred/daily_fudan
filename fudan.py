from lxml import etree
from requests import session
import time, json
import logging, sys

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

    def _page_init(self):
        """
        检查是否能打开登录页面
        :return: 登录页page source
        """
        page_login = self.session.get(self.url_login)

        if page_login.status_code == 200:
            return page_login.text
        else:
            raise Exception("无法打开页面，请检查网络连接")
            
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

        #logging.info("Login, status code = {}".format(post.status_code))

        if post.status_code == 302:
            return {'status': 0, 'message': '登录成功'}
        else:
            raise Exception("登录失败，请检查账号信息，状态码 {}".format(post.status_code))

    def logout(self,url='https://uis.fudan.edu.cn/authserver/logout?service=/authserver/login'):
        """
        执行登出
        """
        expire = self.session.get(url).headers.get('Set-Cookie')
        # print(expire)

        if '01-Jan-1970' in expire:
            return {'status': 0, 'message': '登出成功'}
        else:
            raise Exception('登出异常')

    def close(self):
        """
        执行登出并关闭会话
        """
        self.logout()
        self.session.close()

class Zlapp(Fudan):
    '''
    检查是否已提交平安复旦的信息，并根据上一次填写的地理位置填报
    '''

    def __init__(self, uid, psw, url_login='https://uis.fudan.edu.cn/authserver/login', host='uis.fudan.edu.cn', origin='http://uis.fudan.edu.cn'):
        super().__init__(uid, psw, url_login=url_login, host=host, origin=origin)
        self.has_submitted = False

    def check(self):
        """
        检查今日是否已提交
        """
        last_info = self.session.get('https://zlapp.fudan.edu.cn/ncov/wap/fudan/get-info').json()["d"]["info"]

        date = last_info["date"]
        address = json.loads(last_info['geo_api_info'])['formattedAddress']

        today = time.strftime("%Y%m%d", time.localtime())
        message = "日期：{}，地址：{}".format(date, address)
        if date == today and self.has_submitted == False:
            return {'status': 2, 'message': "今日已提交 " + message}
        elif date == today and self.has_submitted == True:
            return {'status': 0, 'message': "提交成功" + message}
        else:
            return {'status': 1, 'message': '尚未提交', 'formdata': last_info}

    def checkin(self):
        """
        执行提交
        """
        check = self.check()
        if check['status'] != 1: return check
        formdata = check['formdata']

        headers = {
            "Host"      : "zlapp.fudan.edu.cn",
            "Referer"   : "https://zlapp.fudan.edu.cn/site/ncov/fudanDaily?from=history",
            "DNT"       : "1",
            "TE"        : "Trailers",
            "User-Agent": self.UA
        }
        
        address = formdata["geo_api_info"]["addressComponent"]
        province = address.get("province", "")
        city = address.get("city", "")
        if not city: city = province
        district = address.get("district", "")

        formdata.update({
            "tw"      : "13",
            "province": province,
            "city"    : city,
            "area"    : " ".join((province, city, district))
        })

        r = self.session.post(
            'https://zlapp.fudan.edu.cn/ncov/wap/fudan/save',
            data=formdata,
            headers=headers,
            allow_redirects=False
        )

        save_msg = json.loads(r.text)["m"]

        print(save_msg)

        if save_msg != '': raise Exception('提交失败 ' + save_msg)

        self.has_submitted = True
        return self.check()
        