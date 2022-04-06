from data.bot_is_working import Working
from data.insert_db import DB


token_app = ''
token_group = ''
db = 'postgresql:'
boss_list = [''] # id номера пользователей, имеющих право использовать черный список

if __name__ == '__main__':
    create_db = DB(token_group, token_app, db, boss_list)
    create_db.create_table()
    start = Working(token_group, token_app, db, boss_list)
    start.working_bot()
