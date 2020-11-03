from Fudan import Zlapp

class User:
    '''
    user 
    '''
    def __init__(self,user_data):
        self.uid = user_data[0]
        self.psw = user_data[1]
        self.name = user_data[2].upper()
        zlapp_login = 'https://uis.fudan.edu.cn/authserver/login?' \
                  'service=https://zlapp.fudan.edu.cn/site/ncov/fudanDaily'
        self.connect = Zlapp(self.uid, self.psw, url_login=zlapp_login)

    
    

