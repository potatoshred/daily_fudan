from api import run
import MySQLdb as sql

con = sql.connect(host='127.0.0.1',port=3306,user='pafd',passwd='123456',db='django',charset='utf8mb4')
c = con.cursor()
c.execute('select school_id, password, name from pafd_student')
for datum in c.fetchall():
    print(datum[2])
    run(datum[0],datum[1])
con.close()