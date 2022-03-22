import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange


token_group = ''
vk = vk_api.VkApi(token=token_group)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })
    print(f'отправлено текстовое сообщение: "{message}" пользователю id{user_id}')


def client_name(idu):
    """Поиск данных о клиенте"""
    print('запуск функции client_name')
    params_user = {'user_ids': idu, 'fields': 'city'}
    res = vk.method('users.get', params_user)[0]
    name = res['first_name']
    data_list = []
    idu = int(idu)
    data_list.append(idu)

    if 'last_name' in res and len(res['last_name']) != 0:
        full_name = f'{res["first_name"]} {res["last_name"]}'
    else:
        full_name = {res['first_name']}
    data_list.append(full_name)

    if 'city' in res:
        if 'title' in res['city'] and len(res['city']['title']) != 0:
            city = res['city']['title']
            data_list.append(city)
    else:
        city = ''
        data_list.append(city)

    data_list.append(name)

    print(f'результат функции client_name {data_list}')
    return data_list


longpoll = VkLongPoll(vk)
idu_list = []
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        idu = event.user_id

        if event.to_me:
            request = event.text.lower()
            data_user = client_name(idu)
            print(f'получено сообщение с текстом: {request} от пользователя id{idu}')

            if request in 'привет!привет.зравствуйте.здравствуйте!здрасте.здрасте!':
                text = f'{request.title()}, {data_user[-1]}!'
                write_msg(idu, text)

            elif request in 'пока.пока!досвидания.досвидания!':
                text = f'Всего хорошего, {data_user[-1]}!'
                write_msg(idu, text)

            elif request in 'спасибо.спасибо!':
                text = 'Всего доброго!'
                write_msg(idu, text)

            elif request in 'отмена.':
                from insert_db import user_presence, delete_data_user, clearing_search

                mark = user_presence(int(idu))
                if mark:
                    clearing_search(int(idu))
                    delete_data_user(int(idu))
                    text = 'Параметры удалены'
                else:
                    text = 'Данные отсутствуют'
                write_msg(idu, text)

            elif request in "поиск.":
                from dialog_user import dialog_users
                from insert_db import user_presence, insert_users

                mark = user_presence(int(idu))
                if mark:
                    dialog_users(int(idu), request)
                else:
                    insert_users(data_user[:2])
                    text = 'Пришлите год вашего рождения'
                    write_msg(idu, text)
            else:
                from insert_db import user_presence

                mark = user_presence(int(idu))
                if mark:
                    dialog_users(int(idu), request)
                else:
                    text = 'Команда не распознана. Вот список команд: '
                    write_msg(idu, text)
