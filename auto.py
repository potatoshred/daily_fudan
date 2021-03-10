from api import run
import MySQLdb as sql
import secret

if not secret.pafd_password: print('环境变量设置错误，密码不存在')

con = sql.connect(host='101.32.219.129',port=3306,user='pafd',passwd=secret.pafd_password,db='django',charset='utf8mb4')
c = con.cursor()
c.execute('select school_id, password, name from pafd_student')
for datum in c.fetchall():
    print(datum[2], end='  ')
    # print(run(datum[0],datum[1]))
con.close()