from User import User
import sqlite3 as sql

def add_user_data():
    con = sql.connect("database.db")
    c = con.cursor()
    uid = input("请输入学号: ")
    psw = input("请输入密码: ")
    name = input("请输入姓名（仅用作标识，未必是全名）: ")
    data = (uid,psw,name)
    c.execute('insert into user (uid, psw, name) values(?,?,?)',data)
    con.commit()
    con.close()

def print_all_users():
    con = sql.connect("database.db")
    c = con.cursor()
    data = c.execute('select * from user;')
    print(data.fetchall())
    con.close()

def dailyFudan():
    con = sql.connect("database.db")
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
                print("Error: ", e)
                print("User " + u.name + " failed to submit")
                continue
            u.connect.close()
            print("User " + u.name + "submitted successfully")
    con.close()

if __name__ == "__main__":
    while True:
        print("1.填写平安复旦")
        print("2.增加用户")
        print("0.退出")
        key = input("")
        try:
            key = int(key)
        except ValueError:
            print("You've got the wrong door!")
        if key == 1:
            dailyFudan()
        elif key == 2:
            add_user_data()
        elif key == 0:
            break
        else:
            print("You've got the wrong door!")
