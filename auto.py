import MySQLdb as sql
import sys
try:
    from api import run     
    from secret import *
except:
    with open('secret.py', 'w') as f:
        f.write(
'''
# single user or test settings
student_id = ''
password = ''

# database settings
host = '127.0.0.1'
port = 3306
user = ''
passwd = ''
db = ''
charset = 'utf8mb4'
'''
        )
    print('请在 secret.py 中手动填写相应配置，并重新运行程序')
    sys.exit()    

con = sql.connect(host=host,port=port,user=user,passwd=passwd,db=db,charset=charset)
c = con.cursor()
c.execute('select school_id, password, name from pafd_student')
for datum in c.fetchall():
    print(datum[2], end='  ')
    print(run(datum[0],datum[1]))
con.close()