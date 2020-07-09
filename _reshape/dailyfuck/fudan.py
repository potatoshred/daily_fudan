# -*- coding:utf-8 -*-


"""
建立与复旦服务器的会话，执行登录/登出操作
"""
import sys

# ***Custom***
from .utils import simple_debug, justdoit
from . import LOG_LEVEL

# ***Third***
from lxml import etree
from requests import session

logger = simple_debug(level=LOG_LEVEL, namae=__file__)

class FudanIO:
    """
    建立与复旦服务器的会话，执行登录/登出操作
    """
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"

    def __init__(self, uid, psw,
                 url_login='https://uis.fudan.edu.cn/authserver/login'):
        """
        初始化session，及登录信息

        :param uid: 学号
        :param psw: 密码
        :param url_login: 登录页，默认为空服务
        """
        self.session = session()
        self.session.headers['User-Agent'] = self.UA
        self.url_login = url_login

        self.uid = uid
        self.psw = psw

    def _page_init(self) -> str:
        """
        检查是否能打开登录页面

        :return: 登录页page source
        """
        logger.debug("◉初始化……")
        try:
            page_login = self.session.get(self.url_login)
        except:
            print("\a", end="\r")
            logger.error("没网, 检查一下")
            import sys
            sys.exit(0)

        logger.debug("状态码返回: " + page_login.status_code.__str__())

        if page_login.status_code == 200:
            logger.debug("◉初始化完成")
            return page_login.text
        else:
            logger.debug("◉初始化失败")
            self.close()

    def login(self):
        """
        执行登录
        """
        page_login = self._page_init()

        logger.debug("解析页面")
        html = etree.HTML(page_login, etree.HTMLParser())

        logger.debug("解析令牌")
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

        logger.debug("◉登陆中")
        post = self.session.post(
                self.url_login,
                data=data,
                headers=headers,
                allow_redirects=False)

        logger.debug("状态码返回: " + post.status_code.__str__())

        if post.status_code == 302:
            pass
            logger.debug("◉登录成功")
        else:
            logger.info("◉登录失败，请检查账号信息，删除account文件")
            self.close()

    def logout(self):
        """
        执行登出
        """
        exit_url = 'https://uis.fudan.edu.cn/authserver/logout?service=/authserver/login'
        expire = self.session.get(exit_url).headers.get('Set-Cookie')

        if '01-Jan-1970' in expire:
            logger.debug("◉登出完毕")
        else:
            logger.debug("◉登出异常")

    def close(self):
        """
        执行登出并关闭会话
        """
        self.logout()
        self.session.close()
        logger.info("◉会话关闭")
        sys.exit(1)

if __name__ == '__main__':
    test = FudanIO("s", "b")
    test.login()

    @justdoit("sdfg")
    def svddg():
        print("FUCKOFF", sdfd="")

    svddg()
