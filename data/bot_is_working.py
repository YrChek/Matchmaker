import vk_api
import os
from data.tokkens import Tok_ken
from data.insert_db import DB
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.upload import VkUpload
from data.logfiles.logs import log
import requests
from io import BytesIO
from random import randrange


class Working(Tok_ken):

    def __init__(self, token_group, token_app, db, boss_list):
        super().__init__(token_group, token_app, db, boss_list)
        self.token_group = token_group
        self.data = DB(token_group, token_app, db, boss_list)

    def group_vk(self):
        vk = vk_api.VkApi(token=self.token_group)
        return vk

    def write_msg(self, user_id, message):
        """Отправка текстового сообщения"""
        vk = self.group_vk()
        vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })
        log.info(f'ответ пользователю id{user_id}:\n "{message}"')
        print(f'отправлено текстовое сообщение: "{message}" пользователю id{user_id}')

    def photos_message(self, idu, ids, array):
        """Зазгузка и отправка фотографий клиенту"""

        print('запуск функции photos_message')
        vk = self.group_vk()
        vk_upload = vk.get_api()
        upload = VkUpload(vk_upload)
        text = f'Ссылка на страницу в ВК: https://vk.com/id{ids}'
        self.write_msg(idu, text)
        for image_url in array:
            image_url = image_url[1]
            img = requests.get(image_url).content
            photo_bytes = BytesIO(img)
            try:
                image = upload.photo_messages(photo_bytes)[0]
            except Exception as error:
                log.error("Ошибка при скачивании фотографии", exc_info=True)
                print('Ошибка при скачивании фотографии\n', error)
                text = 'Техническая неисправность, приносим свои извинения! Скоро все заработает.'
                self.write_msg(idu, text)
                return False
            owner_id = image['owner_id']
            photo_id = image['id']
            peer_id = idu
            photo_bytes.close()
            print(f'фотография id{photo_id} скачана')

            text = f'Фотография из профиля'
            attachment = f'photo{str(owner_id)}_{str(photo_id)}'
            params = {'peer_id': peer_id, 'message': text, 'attachment': attachment, 'random_id': randrange(10 ** 7)}
            try:
                vk.method('messages.send', params)
            except Exception as error:
                log.error("Ошибка при отправке фотографии пользователю", exc_info=True)
                print('Ошибка при отправке фотографии\n', error)
                text = 'Техническая неисправность, приносим свои извинения! Скоро все заработает.'
                self.write_msg(idu, text)
                return False
            print(f'фотография id{photo_id} отправлена пользователю id{peer_id}')
        log.info(f'фотографии пользователю id{idu} отправлены"')
        return True

    def client_name(self, idu):
        """Поиск данных о клиенте"""
        print('запуск функции client_name')
        vk = self.group_vk()
        params_user = {'user_ids': idu, 'fields': 'city'}
        try:
            res = vk.method('users.get', params_user)[0]
        except Exception as error:
            log.error("Ошибка поиска данных о клиенте", exc_info=True)
            print('Ошибка поиска данных о клиенте\n', error)
            text = 'Ой, техническая неисправность, приносим свои извинения! Скоро все заработает.'
            self.write_msg(idu, text)
            return False
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

    def working_bot(self):
        vk = self.group_vk()
        user_dict = {}
        favourites_dict = {}
        last_sent = {}
        list_blocked = []
        attachment = False

        records = self.data.select_all_users()
        blocked = self.data.select_banned()
        favourites = self.data.select_all_favourites()
        print('start working_bot')
        log.info(f'запуск бота')

        if records == 'error':
            print('return working_bot')
            return
        else:
            if len(records) != 0:
                for rec in records:
                    user_dict[rec[0]] = list(rec)

        if blocked == 'error':
            log.warning('Ошибка чтения черного списка')
            print('работа бота без учета черного списка')
        else:
            if len(blocked) != 0:
                for block in blocked:
                    list_blocked.append(block[0])
                    owner_id = block[1]
                    photo_id = block[2]
                attachment = f'photo{str(owner_id)}_{str(photo_id)}'

        if favourites == 'error':
            log.warning('Ошибка чтения списка избранных')
            print('список избранных недоступен')
        else:
            if len(favourites) != 0:
                for usr in favourites:
                    value = {usr[1]: usr[2]}
                    if usr[0] in favourites_dict:
                        favourites_dict[usr[0]].update(value)
                    else:
                        favourites_dict[usr[0]] = value

        longpoll = VkLongPoll(vk)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                idu = event.user_id

                if event.to_me:
                    if idu in list_blocked:
                        pass
                    else:
                        request = event.text.lower()
                        data_user = self.client_name(idu)
                        full_name = data_user[1]
                        log.info(f'запрос от пользователя id{idu}:\n "{request}"')
                        print(f'получено сообщение с текстом: "{request}" от пользователя id{idu}')

                    if request in 'привет!привет.зравствуйте.здравствуйте!здрасте.здрасте!':
                        text = f'Здравствуйте, {data_user[-1]}!\n' \
                               f'Если вы желаете найти себе спутника, либо начать интересное общение, ' \
                               f'наберите "Поиск".\n' \
                               f'Если вы хотите продолжить поиск, наберите "Далее".'
                        self.write_msg(idu, text)

                    elif request in 'пока.пока!досвидания.досвидания!':
                        text = f'Всего хорошего, {data_user[-1]}!'
                        self.write_msg(idu, text)

                    elif request in 'спасибо.спасибо!':
                        text = 'Всего доброго!'
                        self.write_msg(idu, text)

                    elif request in 'отмена.':

                        idu = int(idu)
                        if idu not in user_dict:
                            mark = False
                        else:
                            mark = True
                        if mark:
                            clearing_search = self.data.clearing_search(idu)
                            delete_data_user = self.data.delete_data_user(idu)
                            if clearing_search and delete_data_user:
                                del user_dict[idu]
                                text = 'Параметры удалены'
                            else:
                                text = 'Техническая неисправность, приносим свои извенения! Скоро все заработает.'
                        else:
                            text = 'Данные отсутствуют'
                        self.write_msg(idu, text)

                    elif request in "поиск.":
                        from data.dialog_user import dialog_users
                        idu = int(idu)
                        if idu not in user_dict:
                            mark = False
                        else:
                            mark = True
                        if mark:
                            cells = len(user_dict[idu])
                            dialog_users(idu, request, cells, user_dict, last_sent)
                        else:
                            user_dict[idu] = [idu, full_name]
                            text = 'Пришлите год вашего рождения'
                            self.write_msg(idu, text)

                    elif 'unlock' in request:
                        boss = str(idu)
                        if boss in self.boss_list:
                            peer_id = ''
                            for i in request:
                                if i in '0123456789':
                                    peer_id += i
                            if len(peer_id) != 9:
                                text = 'некорректный номер id пользователя'
                            elif int(peer_id) not in list_blocked:
                                text = 'пользователь отсутствует в черном списке'
                            else:
                                ids = int(peer_id)
                                restore = self.data.clearing_banned(ids)
                                if restore:
                                    list_blocked.remove(ids)
                                    self.write_msg(ids, 'Вы снова можете пользоваться сервисом!')
                                    log.info(f'сообщение пользователю id{ids}:\n '
                                             f'"Вы снова можете пользоваться сервисом!"')
                                    text = 'пользователь удален из черного списка'
                                else:
                                    text = 'неудачная попытка удаления из черного списка'
                            self.write_msg(idu, text)
                        else:
                            text = 'У вас нет прав, для выполнения этого действия'
                            self.write_msg(idu, text)

                    elif 'lock' in request:
                        boss = str(idu)
                        if boss in self.boss_list:
                            peer_id = ''
                            for i in request:
                                if i in '0123456789':
                                    peer_id += i
                            if len(peer_id) != 9:
                                text = 'некорректный номер id пользователя'
                            else:
                                if attachment:
                                    peer_id = int(peer_id)
                                    data_list = [peer_id, owner_id, photo_id]
                                    work = self.data.insert_banned(data_list)
                                    if work:
                                        list_blocked.append(peer_id)
                                        params = {'peer_id': peer_id, 'attachment': attachment,
                                                  'random_id': randrange(10 ** 7)}
                                        vk.method('messages.send', params)
                                        log.info(f'Картинка пользователю id{peer_id}:\n '
                                                 f'"Вы добавлены в черный список"')
                                        text = 'Пользователь в черный список добавлен'
                                    else:
                                        text = 'неудачная попытка добавления в черный список'
                                else:
                                    peer_id = int(peer_id)
                                    vk_upload = vk.get_api()
                                    upload = VkUpload(vk_upload)
                                    path = os.getcwd()
                                    name_file = os.path.join(path, 'data', 'pictures', 'ban.png')
                                    try:
                                        photo = upload.photo_messages(name_file)[0]
                                    except Exception as error:
                                        photo = 'error'
                                        log.error("Ошибка скачивании фото с диска", exc_info=True)
                                        print('Ошибка скачивания фото с диска":\n', error)
                                    if photo != 'error':
                                        owner_id = photo['owner_id']
                                        photo_id = photo['id']
                                        data_list = [peer_id, int(owner_id), int(photo_id)]
                                        work = self.data.insert_banned(data_list)
                                        if work:
                                            list_blocked.append(peer_id)
                                            attachment = f'photo{owner_id}_{photo_id}'
                                            params = {'peer_id': peer_id, 'attachment': attachment,
                                                      'random_id': randrange(10 ** 7)}
                                            vk.method('messages.send', params)
                                            log.info(f'Картинка пользователю id{peer_id}:\n '
                                                     f'"Вы добавлены в черный список"')
                                            text = 'Пользователь добавлен в черный список'
                                        else:
                                            text = 'попытка добавления в черный список не удалась'
                                    else:
                                        text = 'в черный список не добавлено'

                            self.write_msg(idu, text)
                        else:
                            text = 'У вас нет прав, для выполнения этого действия'
                            self.write_msg(idu, text)

                    elif 'сохран' in request:
                        from data.dialog_user import dialog_favourites
                        dialog_favourites(idu, request, last_sent, favourites_dict)

                    elif 'удалить' in request:
                        from data.dialog_user import dialog_favourites
                        dialog_favourites(idu, request, last_sent, favourites_dict)

                    elif 'показать' in request:
                        from data.dialog_user import dialog_favourites
                        dialog_favourites(idu, request, last_sent, favourites_dict)

                    else:
                        from data.dialog_user import dialog_users
                        idu = int(idu)
                        if idu not in user_dict:
                            mark = False
                        else:
                            mark = True
                        if mark:
                            cells = len(user_dict[idu])
                            dialog_users(idu, request, cells, user_dict, last_sent)
                        else:
                            text = 'Ваша команда не распознана, проверьте правильность написания.\n ' \
                                   'Если вы желаете найти себе спутника, либо начать интересное общение, ' \
                                   'наберите "Поиск".'
                            self.write_msg(idu, text)
