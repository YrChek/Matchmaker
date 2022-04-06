from data.bot_is_working import Working
from data.insert_db import DB
from data.search_users import Search
from main import token_app, token_group, db, boss_list
from data.logfiles.logs import log

db = DB(token_group, token_app, db, boss_list)
letter = Working(token_group, token_app, db, boss_list)
found = Search(token_group, token_app, db, boss_list)


def check_age(idu, message, array, letter=letter):
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
            array[idu].append(msg)
            text = f'Пришлите название вашего города (населенного пункта)'

    letter.write_msg(idu, text)
    return True


def name_city(idu, message, array, letter=letter, found=found):
    """Проверка названия города"""
    print('начата проверка названия города')
    name = found.check_city(message)
    if name == 1:
        message = message.title()
        array[idu].append(message)
        text = 'Пришлите вашу половую принадлежность (муж/жен).'
    elif name == 2:
        text = 'Населенный пункт не распознан, либо отсутствуют данные. ' \
               'Проверте правильность написания названия населенного пункта и пришлите заново.'
    else:
        text = 'Техническая неисправность №3, приносим свои извинения! Скоро все заработает.'
    letter.write_msg(idu, text)
    return True


def final_question(idu, message, array, sent, db=db, letter=letter, found=found):
    """Проверка пола и отправка первой кандидатуры"""
    print('начата проверка пола клиента')
    sex = 0
    if 'муж' in message:
        sex += 2
    if 'жен' in message:
        sex += 1
    if sex not in (1, 2):
        text = 'Ответ не распознан, проверте правильность написания. Пришлите слово "муж" или "жен"'
        letter.write_msg(idu, text)
    else:
        text = 'Ваш запрос принят, начинаем поиск. Потребуется некоторое время'
        letter.write_msg(idu, text)
        if 'муж' in message:
            sex = 2
        else:
            sex = 1
        array[idu].append(sex)
        mark = db.insert_users(idu, array)
        if not mark:
            array[idu].pop()
            return False
        user_list = array[idu]
        finish_list = found.candidat_list(user_list[0], user_list[2], user_list[3], user_list[4])
        if finish_list == 'error':
            del array[idu]
            return False
        elif len(finish_list) == 0:
            text = 'К сожалению по вашим параметрам кандидатов нет. Вы пожете прислать "Отмена"' \
                   ' и попробовать поиск с другими параметрами'
        else:
            mark = db.insert_user_candidate(finish_list)
            if not mark:
                return False
            list_id = db.select_city(user_list[0], user_list[3])
            if not list_id:
                return False
            ids = list_id[1]
            sort_list = found.photo_user(ids)
            print(list_id)
            sent[list_id[0]] = [list_id[1], list_id[2]]

            letter.photos_message(idu, ids, sort_list)
            mark = db.delete_record(idu, ids)
            if not mark:
                text = 'Приносим извинения, технический сбой. Могут быть повторные предложения'
            else:
                text = 'Пришлите "далее", чтобы посмотреть следующую кандидатуру'
        letter.write_msg(idu, text)
    return True


def continue_selection(idu, message, array, sent, db=db, letter=letter, found=found):
    """Отправка следуещего кандидата"""

    print('запуск функции отправки очередного кандидата клиенту')
    if 'далее' not in message:
        text = 'Запрос не распознан. Проверте правильность написания.\n' \
               'Для нового поиска наберите "Далее" .\n' \
               'Для изменения параметров поиска, наберите "Отмена".'
        letter.write_msg(idu, text)
    else:
        user_list = array[idu]
        list_id = db.select_city(user_list[0], user_list[3])
        if list_id == False:
            return False
        if list_id is None:
            text = 'К сожалению, в вашем городе, закончились все кандидаты.\n ' \
                   'Наберите "Отмена" и попробуйте выбрать другой населенный пункт.'
        else:
            ids = list_id[1]
            sort_list = found.photo_user(ids)
            sent[list_id[0]] = [list_id[1], list_id[2]]

            letter.photos_message(idu, ids, sort_list)
            mark = db.delete_record(idu, ids)
            if not mark:
                text = 'Приносим извинения, технический сбой. Могут быть повторные предложения'
            else:
                text = 'Пришлите "далее", чтобы посмотреть следующую кандидатуру'
        letter.write_msg(idu, text)
    return True


def dialog_users(idu, message, cells, array, sent):
    print('запуск функции dialog_users')
    if cells == 2:
        check_age(idu, message, array)
    elif cells == 3:
        name_city(idu, message, array)
    elif cells == 4:
        mark = final_question(idu, message, array, sent)
        if not mark:
            text = 'Техническая неисправность, приносим свои извинения! Скоро все заработает.'
            letter.write_msg(idu, text)
    elif cells == 5:
        mark = continue_selection(idu, message, array, sent)
        if not mark:
            text = 'Техническая неисправность, приносим свои извинения! Скоро все заработает.'
            letter.write_msg(idu, text)
    else:
        log.error('Ошибка dialog_user')
        print('Ошибка dialog_user')
    return True


def favourites_del(idu, message, all_favour):
    """Удаление из избранного"""
    idu = int(idu)
    num = ''
    for i in message:
        if i in '0123456789':
            num += i

    if 'всех' in message:
        if idu in all_favour:
            deleting = db.delete_all_favourites(idu)
            if deleting:
                del all_favour[idu]
                text = 'Избранное очищено'
            else:
                text = 'Неудачная попытка удаления'
        else:
            text = 'У Вас нет избранного'
            letter.write_msg(idu, text)
        letter.write_msg(idu, text)

    elif len(num) != 0:
        if len(num) != 9:
            text = 'Неверный номер id пользователя'
        else:
            num = int(num)
            if num not in all_favour[idu]:
                text = 'Этот пользователь отсутствует в сохраненных'
            else:
                deleting = db.delete_favourite(idu, num)
                if deleting:
                    del all_favour[idu][num]
                    text = 'Пользователь удален из избранного'
                else:
                    text = 'Попытка удаления не удалась'
        letter.write_msg(idu, text)

    else:
        text = 'Для полного удаления избранного наберите "Удалить всех".\n ' \
               'Для удаления одного пользователя, наберите "Удалить *********", ' \
               'где вместо звездочек наберите номер id удаляемого пользователя.\n' \
               'Что бы посмотеть всех избранных, наберите "Показать"'
        letter.write_msg(idu, text)
    return True


def favourites_in(idu, sent, all_favour):
    """Добавление пользователя в избранное"""
    idu = int(idu)
    last = sent.copy()
    if idu in last:
        data = [idu]
        value = last[idu]
        data += value
        paste = db.insert_favourite(data)
        if paste:
            if idu in all_favour:
                ids_d = {value[0]: value[1]}
                all_favour[idu].update(ids_d)
            else:
                ids_d = {value[0]: value[1]}
                all_favour[idu] = ids_d
            text = f'Пользователь {value[1]} добавлен в избранное.\n' \
                   f'Вы можете удалить пользователя из сохраненных набрав команду "Удалить"\n' \
                   f'Что бы посмотеть всех избранных, наберите "Показать"'
        else:
            text = 'Неудачная попытка сохранения пользователя'
        letter.write_msg(idu, text)
    else:
        text = 'Ваша команда не распознана, проверьте правильность написания.\n ' \
               'Если вы желаете найти себе спутника, либо начать интересное общение, ' \
               'наберите "Поиск".'
        letter.write_msg(idu, text)
    return True


def favourites_com(idu, all_favour):
    """Показать избранное"""
    if idu in all_favour:
        text = 'Ваше избранное:\n'
        for ids in all_favour[idu]:
            text += f'{all_favour[idu][ids]} https://vk.com/{ids}\n'
    else:
        text = 'У Вас нет избранного'
    letter.write_msg(idu, text)
    return True


def dialog_favourites(idu, message, sent, all_favour):
    if 'сохран' in message:
        favourites_in(idu, sent, all_favour)
    elif 'удалить' in message:
        favourites_del(idu, message, all_favour)
    elif 'показать' in message:
        favourites_com(idu, all_favour)
    else:
        log.error('Ошибка dialog_favourites')
        print('Ошибка dialog_favourites')
    return True
