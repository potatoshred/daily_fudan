import app_utils
import argparse

parser = argparse.ArgumentParser(description="Fudan Script")
parser.add_argument("-r","--run",action="store_true",help="Auto submit Daily Fudan")
parser.add_argument("-a","--add",action="store_true",help="Add a user")
parser.add_argument("-l","--list",action="store_true",help="List users")
args = parser.parse_args()

def main():
    if args.run:
        app_utils.dailyFudan()
    elif args.add:
        app_utils.add_user_data()
    elif args.list:
        app_utils.print_all_users()
    else:
        app_utils.default()


if __name__ == "__main__":
    main()