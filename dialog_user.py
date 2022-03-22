def check_age(idu, message):
    """Проверка правильности введенного года рождения"""
    print('начата проверка правильности введенного года рождения')
    text = str()
    message = str(message)
    if len(message) != 4:
        text = f'Некорректная дата (длина)'
    else:
        for n in message:
            if n not in '0123456789':
                text = f'Некорректная дата (цифры)'
                break
    if 'Некорректная дата' in text:
        pass
    else:
        import time
        msg = int(message)
        year = time.localtime().tm_year
        if msg >= year - 18:
            text = f'Сервисом могут пользоваться только лица, {year - 19} года рождения и старше'
        else:
            from insert_db import insert_user_b_year
            insert_user_b_year(idu, msg)
            text = f'Пришлите название вашего города (населенного пункта)'

    from reply_message import text_message
    text_message(idu, text)


def name_city(idu, message):
    """Проверка названия города"""
    print('начата проверка названия города')
    from search_users import check_city
    name = check_city(message)
    if name:
        message = message.title()
        from insert_db import insert_user_city
        insert_user_city(idu, message)
        text = 'Пришлите вашу половую принадлежность (муж/жен).'
    else:
        text = 'Населенный пункт не распознан, либо отсутствуют данные. ' \
               'Проверте правильность написания названия населенного пункта и пришлите заново.'
    from reply_message import text_message
    text_message(idu, text)


def final_question(idu, message):
    """Проверка пола и отправка первой кандидатуры"""
    print('начата проверка пола клиента')
    from reply_message import text_message, photos_message
    sex = 0
    if 'муж' in message:
        sex += 2
    if 'жен' in message:
        sex += 1
    if sex not in (1, 2):
        text = 'Ответ не распознан, проверте правильность написания. Пришлите слово "муж" или "жен"'
        text_message(idu, text)
    else:
        text = 'Ваш запрос принят, начинаем поиск'
        text_message(idu, text)
        if 'муж' in message:
            sex = 2
        else:
            sex = 1
        from insert_db import insert_user_candidate, select_sity, delete_record, insert_user_sex, select_users
        insert_user_sex(idu, sex)
        user_list = select_users(idu)
        from search_users import candidat_list, photo_user
        finish_list = candidat_list(user_list[0], user_list[2], user_list[3], user_list[4])

        insert_user_candidate(finish_list)
        list_id = select_sity(user_list[0], user_list[2])
        ids = list_id[1]
        sort_list = photo_user(ids)

        delete_record(idu, ids)

        photos_message(idu, ids, sort_list)

        text = 'Пришлите "далее", чтобы посмотреть следующую кандидатуру'
        text_message(idu, text)


def continue_selection(idu, message):
    """Отправка следуещего кандидата"""
    print('запуск функции отправки очередного кандидата клиенту')
    from reply_message import text_message, photos_message
    if 'далее' not in message:
        text = 'Запрос не распознан. Проверте правильность написания. Наберите "Далее", либо "Отмена"'
        text_message(idu, text)
    else:
        from insert_db import select_sity, delete_record, select_users
        from search_users import photo_user
        user_list = select_users(idu)
        list_id = select_sity(user_list[0], user_list[2])
        if list_id is None:
            text = 'К сожалению, в вашем городе, закончились все кандидаты.\n ' \
                   'Наберите "Отмена" и попробуйте выбрать другой населенный пункт.'
            text_message(idu, text)
        else:
            ids = list_id[1]
            sort_list = photo_user(ids)

            delete_record(idu, ids)

            photos_message(idu, ids, sort_list)

            text = 'Пришлите "далее", чтобы посмотреть следующую кандидатуру'
            text_message(idu, text)


def dialog_users(idu, message):
    print('запуск функции dialog_users')
    from insert_db import not_empty_cells
    cells = not_empty_cells(idu)
    cells = int(cells)
    if cells == 2:
        check_age(idu, message)
    elif cells == 3:
        name_city(idu, message)
    elif cells == 4:
        final_question(idu, message)
    elif cells == 5:
        continue_selection(idu, message)
    else:
        print('Ошибка dialog_user')
