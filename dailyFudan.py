from User import User
import sqlite3 as sql
import logging, sys, getpass

def add_user_data():
    con = sql.connect(sys.path[0] + "/database.db")
    c = con.cursor()
    uid = input("请输入学号: ")
    psw = getpass.getpass("请输入密码（密码不显示）: ")
    name = input("请输入姓名（仅用作标识，字与字之间请空格）: ")
    data = (uid,psw,name)
    c.execute('insert into user (uid, psw, name) values(?,?,?)',data)
    con.commit()
    con.close()

def print_all_users():
    con = sql.connect(sys.path[0] + "/database.db")
    c = con.cursor()
    data = c.execute('select * from user;')
    print(data.fetchall())
    con.close()

def dailyFudan():

    con = sql.connect(sys.path[0] + "/database.db")
    c = con.cursor()
    data = c.execute('select * from user')
    result = ""

    while True:
        user_data = data.fetchone()
        if user_data is None:
            break
        else:
            u = User(user_data)
            logging.warning("Starting submission for user {}".format(u.name))
            try:
                u.connect.login()
                u.connect.check()
                u.connect.checkin()
                u.connect.check()
            except RuntimeError as e:
                logging.warning("User {} failed to submit because of {}".format(u.name,e))
                result = result + "\nFAIL: User {} failed to submit because of {}".format(u.name,e)
                continue
            u.connect.close()
            logging.warning("User {} submitted successfully".format(u.name))
            result = result + "\nSUCCESS: User {} submitted successfully".format(u.name)

    con.close()
    print(result)

if __name__ == "__main__":

    LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(filename='app.log',format=LOG_FORMAT,datefmt=DATE_FORMAT,level='INFO')

    while True:
        print("************************************************")
        print("1.填写平安复旦")
        print("2.增加用户")
        print("3.Print all users")
        print("0.退出")
        print("************************************************")
        key = input("")
        try:
            key = int(key)
        except ValueError:
            print("You've got the wrong door!")
        if key == 1:
            dailyFudan()
            break
        elif key == 2:
            add_user_data()
        elif key == 3:
            print_all_users()
        elif key == 0:
            break
        else:
            print("You've got the wrong door!")
