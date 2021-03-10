from fudan import Zlapp

def run(uid, psw):
    zlapp_login = 'https://uis.fudan.edu.cn/authserver/login?' \
                  'service=https://zlapp.fudan.edu.cn/site/ncov/fudanDaily'
    u = Zlapp(uid, psw, url_login=zlapp_login)
    try:
        u.login()
        result = u.checkin()
    except Exception as e:
        u.close()
        return {'status': -1, 'message': str(e)}
        # TO DO: NOTIFY
    else:
        u.close()
        return result['message']

