from fudan import Zlapp

def run(uid, psw):
    zlapp_login = 'https://uis.fudan.edu.cn/authserver/login?' \
                  'service=https://zlapp.fudan.edu.cn/site/ncov/fudanDaily'
    u = Zlapp(uid, psw, url_login=zlapp_login)
    try:
        u.login()
        u.check()
        u.checkin()
        message = u.check()
    except RuntimeError as e:
        message = "提交失败 {}".format(e)
    except AssertionError as e:
        message = "提交成功 {}".format(e)
    finally:
        u.close()
    
    return message