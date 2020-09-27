import time
import logging
import yagmail
from json import loads as json_loads
from os import path as os_path
from sys import exit as sys_exit

from lxml import etree
from requests import session

class Fudan:
    """
    建立与复旦服务器的会话，执行登录/登出操作
    """
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"

    # 初始化会话
    def __init__(self,
                 uid, psw, mail,
                 server, port, admin, creds, 
                 url_login='https://uis.fudan.edu.cn/authserver/login'):
        """
        初始化一个session，及登录信息
        :param uid: 学号
        :param psw: 密码
        :param mail: 收信邮箱
        :param server: 发信邮箱服务器
        :param port: 发信邮箱服务器端口号(一般为25或465)
        :param admin: 管理员邮箱账号(必须与发信邮箱同域名)
        :param creds: 管理员邮箱登录凭证(教育邮箱一般为密码，163或QQ为授权码)
        :param url_login: 登录页，默认服务为空
        """
        self.session = session()
        self.session.headers['User-Agent'] = self.UA
        self.url_login = url_login

        self.uid = uid
        self.psw = psw
        self.mail = mail
        self.content = "" #mail 发信内容

        self.server = server
        self.port = port
        self.admin = admin
        self.creds = creds

    def _page_init(self):
        """
        检查是否能打开登录页面
        :return: 登录页page source
        """
        #print("◉Initiating——", end='')
        page_login = self.session.get(self.url_login)

        #print("return status code",page_login.status_code)

        if page_login.status_code == 200:
            #print("◉Initiated——", end="")
            info_str = "Initial Sccuess! "
            self.content += info_str + '\n'
            logger.info("%s",info_str)
            return page_login.text
        else:
            info_str = "Fail to open Login Page, Check your Internet connection!"
            #print("◉Fail to open Login Page, Check your Internet connection\n")
            self.content += info_str + '\n'
            logger.error("%s",info_str)
            self.close()

    def login(self):
        """
        执行登录
        """

        card_info = "AutoCard for usr:" + self.uid
        self.content += card_info + '\n'
        page_login = self._page_init()

        #print("parsing Login page——", end="")
        html = etree.HTML(page_login, etree.HTMLParser())

        #print("getting tokens")
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

        #print("◉Login ing——", end="")
        post = self.session.post(
                self.url_login,
                data=data,
                headers=headers,
                allow_redirects=False)

        #print("return status code", post.status_code)

        if post.status_code == 302:
            #print("\n***********************"
            #      "\n◉登录成功"
            #      "\n***********************\n")
            info_str = "login success!" 
            self.content += info_str + '\n'
            logger.info("%s", info_str)
        else:
            #print("◉登录失败，请检查账号信息")
            info_str = "login failed, check your account info "
            self.content += info_str + '\n'
            logger.error("%s", info_str)
            self.close()

    def logout(self):
        """
        执行登出
        """
        exit_url = 'https://uis.fudan.edu.cn/authserver/logout?service=/authserver/login'
        expire = self.session.get(exit_url).headers.get('Set-Cookie')
        # print(expire)

        if '01-Jan-1970' in expire:
            #print("◉登出完毕")
            info_str = "logout and goodbye"
            self.content += info_str + '\n'
            logger.info("%s", info_str)
        else:
            #print("◉登出异常")
            info_str = "logout error"
            self.content += info_str + '\n'
            logger.error("%s", info_str)

    def close(self):
        """
        执行登出并关闭会话
        """
        self.logout()
        self.session.close()
        logger.info("session closed")
        #print("◉关闭会话")
        #print("************************")
        #input("回车键退出")
        #sys_exit()
    
    def sendmail(self):
        dailymail = yagmail.SMTP(user=self.admin,password=self.creds,host=self.server,smtp_ssl=True)
        #msg = MIMEText(self.content)
        #msg['From'] = self.admin
        #msg['Subject'] = "PingAnDan"
        to = [self.mail]
        mail_cont = [self.content]
        #s = smtplib.SMTP_SSL(self.server, self.port)
        #s.login(self.admin, self.creds)
        logger.info("Sending mail to usr %s",self.uid)
        #s.sendmail(self.admin, to, msg.as_string())
        dailymail.send( to=to, subject = "PingAnFuDan", contents = mail_cont)

class Zlapp(Fudan):
    last_info = ''

    def get_md5(self):
        '''
            获取用户信息
        '''
        get_info = self.session.get(
                'https://zlapp.fudan.edu.cn/ncov/wap/fudan/get-info')
        self.last_info = get_info.json()["d"]["info"]
        #return last_info
        

    def check(self):
        self.get_md5()
        position = self.last_info['geo_api_info']
        position = json_loads(position)
        last_info_str =  "Last Post record is " +  self.last_info["date"] + '\n' + \
            "Last Post place is " + position['formattedAddress']
        self.content += last_info_str + '\n'
        logger.info("%s",last_info_str)

        today = time.strftime("%Y%m%d", time.localtime())

        if self.last_info["date"] == today:
            info_str = "Have Posted info today!"
            self.content += info_str + '\n'
            logger.info("%s",info_str)
        else:
            info_str = "Not Post info today!"
            self.content += info_str + '\n'
            logger.info("%s \n",info_str)
            self.checkin()
            self.get_md5()
            cur_info_str = "Current Post record is " + self.last_info["date"]
            self.content += cur_info_str + '\n'
            logger.info("%s",cur_info_str)

   
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
        self.get_md5()
        #print("\n\n◉◉提交中")
        logger.info("Posting...")
        self.content += "Posting" + '\n'
        #print(self.last_info)
        geo_api_info = json_loads(self.last_info['geo_api_info'])
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
        #print(self.last_info)

        save = self.session.post(
                'https://zlapp.fudan.edu.cn/ncov/wap/fudan/save',
                data=self.last_info,
                headers=headers,
                allow_redirects=False)

        save_msg = json_loads(save.text)["m"]
        #print(save_msg, '\n\n')
        logger.info("%s",save_msg)
        self.content += save_msg + '\n'


def get_account():
    usr_info = []
    if os_path.exists("accounts.txt"):
        with open("accounts.txt","r") as old:
            lines = old.readlines()
            
            for line in lines:
                if len(line) < 10:
                    continue
                uid, psw, mail = line.split(":")[0].strip(), line.split(":")[1].strip(), line.split(":")[2].strip()
                if len(uid) < 11:
                    logger.error("invalid username!")
                usr_info.append((uid, psw, mail))
    else:
        print("accounts.txt NOT FOUND. Initialising for all users info") 
        cnt = input("number of users, uint type:")
        cnt = int(cnt)
        with open("accounts.txt","w") as new:
            for i in range(cnt):
                uid = input("username(fdu_school_num):")
                psw = input("passwd:")
                mail = input("complete_mail_address:")
                if len(uid) < 11:
                    logger.error("invalid username!")
                tmp_info = (uid, psw, mail)
                new.writelines(":".join(tmp_info))
                usr_info.append(tmp_info)
        print("all the users' info has been saved in accounts.txt in the current dir!")
    return usr_info

def set_mail_admin():
    if os_path.exists("admin.txt"):
        with open("admin.txt","r") as f:
            lines = f.readlines()
            for line in lines:
                if len(line) < 5:
                    continue
                line = line.strip()
                admin_info = line.split(':')
                server, port, admin, creds =  admin_info[0],  admin_info[1], admin_info[2], admin_info[3] 
                port = int(port)
                break
            mail_info = (server, port, admin, creds)
    else:
        print("admin.txt NOT FOUND. Initialising for admin info")
        server_s = input("mail server domain(fdu.edu.cn):")
        port_s = input("mail server sending port(25):")
        admin_s = input("admin mail username(xx.fdu.edu.cn):")
        creds_s = input("admin mail passwd or credential code(xxxxxx):")
        mail_info_str = (server_s, port_s, admin_s, creds_s)
        with open("admin.txt","w") as f:
            f.writelines(':'.join(mail_info_str))
        print("admin's info has been saved in admin.txt in the current dir!")
        
        port_s = int(port_s)
        mail_info = (server_s, port_s, admin_s, creds_s)
    return mail_info
if __name__ == '__main__':
    logging.basicConfig(filename = 'daily.log',level = logging.INFO, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    usr_info = get_account()
    #print(usr_info)
    mail_info = set_mail_admin()
    #print(mail_info)
    
    for usr in usr_info:
        uid, psw, mail = usr[0], usr[1], usr[2]
        server, port, admin, creds = mail_info[0], mail_info[1], mail_info[2], mail_info[3]
        zlapp_login = 'https://uis.fudan.edu.cn/authserver/login?' \
                  'service=https://zlapp.fudan.edu.cn/site/ncov/fudanDaily'
        daily_fudan = Zlapp(uid, psw, mail, server, port, admin, creds, url_login=zlapp_login)
        logger.info("PingAnFuDan for user: %s \n",uid)
        daily_fudan.login()
        daily_fudan.check()
        daily_fudan.close()
        daily_fudan.sendmail()
    