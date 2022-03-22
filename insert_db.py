import sqlalchemy
from pprint import pprint

db = ''
engine = sqlalchemy.create_engine(db)
connection = engine.connect()


def insert_users(array):
    """Добавление клиента в таблицу Users"""
    print('Добавление клиента в таблицу Users')
    data = tuple(array)
    params = f'INSERT INTO Users (idu, full_name) VALUES{data} ON CONFLICT DO NOTHING;'
    connection.execute(params)
    print('клиент добавлен')


def insert_user_candidate(array):
    """Добавление кандидатов в таблицу User_Candidate"""
    print('добавление в таблицу результаты поиска кандидатов')
    pprint(array)
    params = str()
    for record in array:
        data = tuple(record)
        temp_params = f'INSERT INTO User_Candidate VALUES{data} ON CONFLICT DO NOTHING;'
        params += temp_params
    connection.execute(params)
    print('кандидаты добавлены')


def insert_user_b_year(idu, b_year):
    """Изменение значения ячейки года рождения"""
    print('запись года рождения в таблицу Users')
    line = f'UPDATE Users SET b_year = {b_year} ' \
           f'WHERE idu = {idu};'
    connection.execute(line)
    print('год рождения записан')


def insert_user_city(idu, city):
    """Изменение значения ячейки города поиска"""
    print('запись города в таблицу Users')
    line = f"UPDATE Users SET search_city = '{city}' " \
           f"WHERE idu = {idu};"
    connection.execute(line)
    print(f'город {city} добавлен')


def insert_user_sex(idu, sex):
    """Изменение значения ячейки года рождения"""
    print('запись значения пола клиента в таблицу Users')
    line = f'UPDATE Users SET gender = {sex} ' \
           f'WHERE idu = {idu};'
    connection.execute(line)
    print('идентификатор пола добавлен')


def user_presence(idu):
    """Проверка наличия записи в таблице Users по idu"""
    line = f'SELECT idu FROM Users WHERE idu = {idu};'
    idu = connection.execute(line).fetchone()
    if idu is None:
        return False
    else:
        return True


def select_users(idu):
    """Выбор записи Users по idu"""
    line = f'SELECT * FROM Users WHERE idu = {idu};'
    record = connection.execute(line).fetchone()
    return record


def select_sity(idu, sity):
    """Сортировка записей по названию города и дате рождения для idu"""
    print('Выбор ids для поиска фотографий из таблицы User_Candidate')
    lines = f"SELECT idu, ids FROM User_Candidate" \
            f" WHERE idu = {idu} AND city = '{sity}'" \
            f" ORDER BY b_year DESC;"
    ids = connection.execute(lines).fetchone()
    if ids is None:
        lines = f"SELECT idu, ids FROM User_Candidate" \
                f" WHERE idu = {idu}" \
                f" ORDER BY b_year DESC;"
        ids = connection.execute(lines).fetchone()
        print('ids выбран')
    return ids


def delete_record(idu, ids):
    """Удаление записи из таблицы User_Candidate по idu и ids"""
    print('удаление записи кандидата из таблицы User_Candidate')
    lines = f"DELETE FROM User_Candidate" \
            f" WHERE idu = {idu} AND ids = '{ids}';"
    connection.execute(lines)
    print('запись удалена')


def clearing_search(idu):
    """Удаление результата поиска клиента"""
    print('удаление результата поиска клиента из таблицы User_Candidate')
    lines = f"DELETE FROM User_Candidate" \
            f" WHERE idu = {idu};"
    connection.execute(lines)
    print('записи удалены')


def delete_data_user(idu):
    """Удаление всех данных клиента"""
    lines = f"DELETE FROM Users" \
            f" WHERE idu = {idu};"
    connection.execute(lines)


def not_empty_cells(idu):
    """Количество непустых ячеек в записи таблицы Users по idu"""
    line = f'SELECT * FROM Users WHERE idu = {idu};'
    table = connection.execute(line).fetchone()
    number = 0
    for i in table:
        if i is not None:
            number += 1
    return number
