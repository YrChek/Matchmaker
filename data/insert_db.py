from data.tokkens import Tok_ken
from data.logfiles.logs import log
import sqlalchemy


class DB(Tok_ken):

    def connects(self):
        engine = sqlalchemy.create_engine(self.db)
        try:
            connection = engine.connect()
        except Exception as error:
            log.error("Ошибка подключения к базе данных", exc_info=True)
            print('Ошибка подключения к базе данных:\n', error)
            return False
        return connection

    def insert_users(self, idu, array):
        """Добавление клиента в таблицу Users"""
        connection = self.connects()
        if connection:
            print('Добавление клиента в таблицу Users')
            data = array[idu].copy()
            data = tuple(data)
            params = f'INSERT INTO Users VALUES{data} ON CONFLICT DO NOTHING;'
            try:
                connection.execute(params)
            except Exception as error:
                log.error("Ошибка при записи в таблицу Users", exc_info=True)
                print('Ошибка БД таблица "Users":\n', error)
                return False
            print('клиент добавлен')
            return True
        else:
            return False

    def insert_banned(self, array):
        """Добавление пользователя в черный список"""
        connection = self.connects()
        if connection:
            print('Добавление пользователя в черный список')
            data = array.copy()
            data = tuple(data)
            params = f'INSERT INTO Blacklist VALUES{data} ON CONFLICT DO NOTHING;'
            try:
                connection.execute(params)
            except Exception as error:
                log.error("Ошибка при записи в таблицу Blacklist", exc_info=True)
                print('Ошибка БД таблица "Blacklist":\n', error)
                return False
            print('пользователь добавлен в черный список')
            return True
        else:
            return False

    def insert_favourite(self, array):
        """Добавление пользователя в избранное"""
        connection = self.connects()
        if connection:
            print('Добавление пользователя в избранное')
            data = array.copy()
            data = tuple(data)
            params = f'INSERT INTO Favourites VALUES{data} ON CONFLICT DO NOTHING;'
            try:
                connection.execute(params)
            except Exception as error:
                log.error("Ошибка при записи в таблицу Favourites", exc_info=True)
                print('Ошибка БД таблица "Favourites":\n', error)
                return False
            print('пользователь добавлен в избранное')
            return True
        else:
            return False

    def insert_user_candidate(self, array):
        """Добавление кандидатов в таблицу User_Candidate"""
        connection = self.connects()
        if connection:
            print('добавление в таблицу результаты поиска кандидатов')
            params = str()
            for record in array:
                data = tuple(record)
                temp_params = f'INSERT INTO User_Candidate VALUES{data} ON CONFLICT DO NOTHING;'
                params += temp_params
            try:
                connection.execute(params)
            except Exception as error:
                log.error("Ошибка при записи в таблицу User_Candidate", exc_info=True)
                print('Ошибка БД таблица User_Candidate\n', error)
                return False
            print('кандидаты добавлены')
            return True
        else:
            return False

    def select_all_favourites(self):
        """выбор всех избранных"""
        connection = self.connects()
        if connection:
            line = f'SELECT * FROM Favourites;'
            try:
                records = connection.execute(line).fetchall()
            except Exception as error:
                log.error("Ошибка при чтении из таблицы Favourites", exc_info=True)
                print('Ошибка БД таблица "Favourites"\n', error)
                return 'error'
            return records
        else:
            return 'error'

    def user_presence(self, idu):
        """Проверка наличия записи в таблице Users по idu"""
        connection = self.connects()
        line = f'SELECT idu FROM Users WHERE idu = {idu};'
        idu = connection.execute(line).fetchone()
        if idu is None:
            return False
        else:
            return True

    def select_all_users(self):
        """Выбор записей всех клиентов"""
        connection = self.connects()
        if connection:
            line = f'SELECT * FROM Users;'
            try:
                records = connection.execute(line).fetchall()
            except Exception as error:
                log.error("Ошибка при чтении из таблицы Users", exc_info=True)
                print('Ошибка БД таблица "Users"\n', error)
                return 'error'
            return records
        else:
            return 'error'

    def select_banned(self):
        """Чтение черного списка"""
        connection = self.connects()
        if connection:
            line = f'SELECT * FROM Blacklist;'
            try:
                blocked = connection.execute(line).fetchall()
            except Exception as error:
                log.error("Ошибка при чтении из таблицы Blacklist", exc_info=True)
                print('Ошибка БД таблица "Blacklist"\n', error)
                return 'error'
            return blocked
        else:
            return 'error'

    def select_city(self, idu, city):
        """Сортировка записей по названию города и дате рождения для idu"""
        connection = self.connects()
        if connection:
            print('Выбор ids для поиска фотографий из таблицы User_Candidate')
            lines = f"SELECT * FROM User_Candidate" \
                    f" WHERE idu = {idu} AND city = '{city}'" \
                    f" ORDER BY b_year DESC;"
            try:
                ids = connection.execute(lines).fetchone()
            except Exception as error:
                log.error("Ошибка №1 при чтении из таблицы User_Candidate", exc_info=True)
                print('Ошибка БД таблица User_Candidate\n', error)
                return False
            text = 'ids по городу выбран'
            if ids is None:
                lines = f"SELECT * FROM User_Candidate" \
                        f" WHERE idu = {idu}" \
                        f" ORDER BY b_year DESC;"
                try:
                    ids = connection.execute(lines).fetchone()
                except Exception as error:
                    log.error("Ошибка №2 при чтении из таблицы User_Candidate", exc_info=True)
                    print('Ошибка БД таблица User_Candidate\n', error)
                    return False
                text = 'ids выбран без учета города'

            print(text)
            return ids
        else:
            return False

    def delete_record(self, idu, ids):
        """Удаление записи из таблицы User_Candidate по idu и ids"""
        connection = self.connects()
        if connection:
            print('удаление записи кандидата из таблицы User_Candidate')
            lines = f"DELETE FROM User_Candidate" \
                    f" WHERE idu = {idu} AND ids = {ids};"
            try:
                connection.execute(lines)
            except Exception as error:
                log.error("Ошибка при удалении одной записи из таблицы User_Candidate", exc_info=True)
                print('Ошибка БД таблица User_Candidate\n', error)
                return False
            print('запись удалена')
            return True
        else:
            return False

    def delete_favourite(self, idu, ids):
        """Удаление записи из таблицы Favourites по idu и ids"""
        connection = self.connects()
        if connection:
            print('удаление пользователя из таблицы Favourites')
            lines = f"DELETE FROM Favourites" \
                    f" WHERE idu = {idu} AND ids = {ids};"
            try:
                connection.execute(lines)
            except Exception as error:
                log.error("Ошибка при удалении одной записи из таблицы Favourites", exc_info=True)
                print('Ошибка БД таблица Favourites\n', error)
                return False
            print('запись удалена')
            return True
        else:
            return False

    def delete_all_favourites(self, idu):
        """Удаление всех избранных клиента по idu"""
        connection = self.connects()
        if connection:
            print('удаление избранных из таблицы Favourites')
            lines = f"DELETE FROM Favourites" \
                    f" WHERE idu = {idu};"
            try:
                connection.execute(lines)
            except Exception as error:
                log.error("Ошибка при удалении записей из таблицы Favourites", exc_info=True)
                print('Ошибка БД таблица Favourites\n', error)
                return False
            print('записи удалены')
            return True
        else:
            return False

    def clearing_search(self, idu):
        """Удаление всех результатов поиска клиента"""
        connection = self.connects()
        if connection:
            print('удаление результатов поиска клиента из таблицы User_Candidate')
            lines = f"DELETE FROM User_Candidate" \
                    f" WHERE idu = {idu};"
            try:
                connection.execute(lines)
            except Exception as error:
                log.error("Ошибка при удалении всех записей из таблицы User_Candidate", exc_info=True)
                print('Ошибка БД таблица User_Candidate\n', error)
                return False
            print('записи удалены')
            return True
        else:
            return False

    def clearing_banned(self, ids):
        """Удаление из черного списка"""
        connection = self.connects()
        if connection:
            print('удаление пользователя из черного списка')
            lines = f"DELETE FROM Blacklist" \
                    f" WHERE peer_id = {ids};"
            try:
                connection.execute(lines)
            except Exception as error:
                log.error("Ошибка при удалении записи из таблицы Blacklist", exc_info=True)
                print('Ошибка БД таблица Blacklist\n', error)
                return False
            print('запись удалена')
            return True
        else:
             return False

    def delete_data_user(self, idu):
        """Удаление всех данных клиента"""
        connection = self.connects()
        if connection:
            print('удаление личных данных клиента')
            lines = f"DELETE FROM Users" \
                    f" WHERE idu = {idu};"
            try:
                connection.execute(lines)
            except Exception as error:
                log.error("Ошибка при удалении данных клиента из таблицы Users", exc_info=True)
                print('Ошибка БД таблица Users\n', error)
                return False
            print('записи удалены')
            return True
        else:
            return False

    def create_table(self):
        """Создание таблиц в БД"""
        connection = self.connects()
        connection.execute("""CREATE TABLE if not exists Users(
        idu integer primary key,
        full_name text not null,
        b_year integer,
        search_city text,
        gender integer);

        CREATE TABLE if not exists User_Candidate(
        idu integer references Users (idu),
        ids integer not null,
        full_name text not null,
        b_year integer not null,
        city text not null,
        gender integer not null,
        primary key (ids, idu));
        
        CREATE TABLE if not exists Blacklist(
        peer_id integer primary key,
        owner_id integer not null,
        photo_id integer not null);
        
        CREATE TABLE if not exists Favourites(
        idu integer not null,
        ids integer not null,
        full_name text not null,
        primary key (ids, idu));""")
