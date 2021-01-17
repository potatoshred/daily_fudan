
import logging, sys
from Fudan_test import Fudan

LOG_PATH = sys.path[0] + "/app.log"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(filename=LOG_PATH,format=LOG_FORMAT,datefmt=DATE_FORMAT,level='INFO')

username = "B2017000365"
password = "B2017000365"
host = "portal.shs.cn"
origin = "http://portal.shs.cn"
url = "http://portal.shs.cn/cas/login?service=http%3A%2F%2Fportal.shs.cn%2Fc%2Fportal%2Flogin%3Bjsessionid%3DC3ECB7AB450011ACB9E9A4416432F4DC%3Fredirect%3D%252F%26p_l_id%3D0"
service = "http://portal.shs.cn/c/portal/login"
#UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"

s = Fudan(username,password,url,host,origin)
s.login(service)

