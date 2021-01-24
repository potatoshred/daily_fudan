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
        print(message)
        result = {'status': False, 'message': message}
    except AssertionError as e:
        message = "提交成功 {}".format(e)
        print(message)
        result = {'status': True, 'message': message}
    else:
        print(message)
        result = {'status': True, 'message': message}
    finally:
        u.close()
    
    return result