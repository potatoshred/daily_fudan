from User import User
import sqlite3 as sql
import sys, getpass, logging

LOG_PATH = sys.path[0] + "/app.log"
DATABASE_PATH = sys.path[0] + "/database.db"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(filename=LOG_PATH,format=LOG_FORMAT,datefmt=DATE_FORMAT,level='INFO')


def add_user():
    print("新增用户数据")
    print("注意：输入密码无显示，请切换(shift)至英文输入法再输入密码，大写字母按shift输入，输入错误请按ctrl+c根据提示重新输入，姓名可使用中文")
    con = sql.connect(DATABASE_PATH)
    c = con.cursor()
    uid = input("请输入学号: ")
    psw = getpass.getpass("请输入密码: ")
    name = input("请输入姓名: ")
    data = (uid,psw,name)
    c.execute("CREATE TABLE IF NOT EXISTS user(uid text NOT NULL, psw text NOT NULL, name text NOT NULL);")
    c.execute('insert into user (uid, psw, name) values(?,?,?)',data)
    con.commit()
    con.close()

def edit_user():
    print("修改用户数据")
    print("注意：输入密码显示，请切换(shift)至英文输入法再输入密码，大写字母按shift输入，输入错误请按ctrl+c根据提示重新输入，姓名可使用中文")
    con = sql.connect(DATABASE_PATH)
    c = con.cursor()
    name = input("请输入要修改的姓名: ")
    uid = input("请输入学号: ")
    psw = input("请输入密码: ")
    if not psw:
        c.execute("UPDATE user SET uid = ? WHERE name = ?",
        (uid, name)
        )
    elif not uid:
        c.execute("UPDATE user SET psw = ? WHERE name = ?",
        (psw, name)
        )
    elif psw and uid:
        c.execute("UPDATE user SET psw = ?, uid = ? WHERE name = ?",
        (psw, uid, name)
        )
    else:
        print("error updating")
    con.commit()
    con.close()

def delete_user():
    print("删除用户数据")
    con = sql.connect(DATABASE_PATH)
    c = con.cursor()
    name = input("请输入要删除的用户的姓名：")
    c.execute("DELETE FROM user WHERE name = ?", (name,))
    con.commit()
    con.close()  

def print_all_users(show_passwords=False):
    con = sql.connect(DATABASE_PATH)
    c = con.cursor()
    data = c.execute('select * from user;').fetchall()

    print("\n共有{}名用户\n".format(len(data)))
    if show_passwords == True:
        for i in data:
            print("姓名：{}".format(i[2]))
            print("学号：{}".format(i[0]))
            print("密码：{}\n".format(i[1]))
    else:
        for i in data:
            print("姓名：{}".format(i[2]))
            print("学号：{}\n".format(i[0]))
    
    con.close()

def dailyFudan():

    con = sql.connect(DATABASE_PATH)
    c = con.cursor()
    data = c.execute('select * from user')

    while True:
        user_data = data.fetchone()
        if user_data is None:
            break
        else:
            u = User(user_data)
            try:
                u.connect.login()
                u.connect.check()
                u.connect.checkin()
                u.connect.check()
            except RuntimeError as e:
                print("FAIL: User {} failed to submit because of {}".format(u.name,e))
            except AssertionError as e:
                print("SUCCESS: User {} submitted successfully because of {}".format(u.name,e))
            else:
                print("SUCCESS: User {} submitted successfully".format(u.name))
            finally:
                u.connect.close()
    con.close()

def default():
    print("************************************************")
    print("*                                              *")
    print("*             一键平安复旦小脚本               *")
    print("*                                              *")
    print("************************************************")
    print("1.填写平安复旦")
    print("2.增加用户")
    print("3.修改用户")
    print("4.删除用户")
    print("5.列出所有用户")
    print("0.退出")
    print("************************************************")
    enter_note = True

    while True:
        if enter_note == True:
            key = input()
            enter_note = False
        else:
            key = input("回车键返回\n")
        if not key: 
            default()
        try:
            key = int(key)
        except ValueError:
            print("You've got the wrong door!")
        key_type(key)
    
def key_type(key):
    if key == 1:
        dailyFudan()
    elif key == 2:
        try:
            add_user()
        except KeyboardInterrupt:
            print("\n按2重新输入")
    elif key ==3:
        try:
            edit_user()
        except KeyboardInterrupt:
            print("\n按3重新输入")
    elif key == 4:
        delete_user()
    elif key == 5:
        print_all_users()
    elif key == 55:
        print_all_users(True)
    elif key == 0:
        print("退出程序")
        sys.exit()
    else:
        print("You've got the wrong door!")