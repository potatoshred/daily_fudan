# -*- coding:utf-8 -*-


# ***Custom***
from .fudan import FudanIO
from .utils import simple_debug, justdoit
from . import LOG_LEVEL
from ._get_account import get_account

# ***Builtin***
import json
import time

logger = simple_debug(level=LOG_LEVEL, namae=__file__)

class Zlapp(FudanIO):
    last_info = ''

    @justdoit("信息检查过程中发生错误, API可能已过期")
    def check(self):
        """
        检查
        """
        # logger.info("◉核查中")
        get_info = self.session.get(
                'https://zlapp.fudan.edu.cn/ncov/wap/fudan/get-info')
        last_info = get_info.json()

        logger.info("◉最近一次提交日期为: "+last_info["d"]["info"]["date"].__str__()[4:])

        position = last_info["d"]["info"]['geo_api_info']
        position = json.loads(position)

        logger.info("◉最近一次提交地址为: "+position['formattedAddress'].__str__())
        # logger.info("◉最近一次提交GPS为: "+position["position"].__str__())

        today = time.strftime("%Y%m%d", time.localtime())
        if last_info["d"]["info"]["date"] == today:
            logger.info("◉核查成功")
            return True
        else:
            logger.info("◉核查失败")

    @justdoit("信息提交过程中发生错误, API可能已过期")
    def checkin(self):
        """
        提交
        """
        get_info = self.session.get(
                'https://zlapp.fudan.edu.cn/ncov/wap/fudan/get-info').json()

        last_info = get_info["d"]["info"]

        headers = {
            "Host"      : "zlapp.fudan.edu.cn",
            "Referer"   : "https://zlapp.fudan.edu.cn/site/ncov/fudanDaily?from=history",
            "DNT"       : "1",
            "TE"        : "Trailers",
            "User-Agent": self.UA
        }

        logger.debug("◉提交中")
        save = self.session.post(
                'https://zlapp.fudan.edu.cn/ncov/wap/fudan/save',
                data=last_info,
                headers=headers,
                allow_redirects=False)

        save_msg = json.loads(save.text)["m"]

        logger.info("◉"+save_msg)


def task():
    test = Zlapp(*get_account())
    test.login()
    test.checkin()
    result = test.check()
    test.close()

    return result


