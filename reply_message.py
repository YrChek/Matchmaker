import vk_api
from vk_api.upload import VkUpload
import requests
from io import BytesIO
from random import randrange

token_group = ''


def photos_message(idu, ids, array, token=token_group):
    """Зазгузка и отправка фотографий клиенту"""
    print('запуск функции photos_message')
    vk = vk_api.VkApi(token=token)
    vk_upload = vk.get_api()
    upload = VkUpload(vk_upload)
    text = f'Ссылка на страницу в ВК: https://vk.com/id{ids}'
    text_message(idu, text)
    for image_url in array:
        image_url = image_url[1]
        img = requests.get(image_url).content
        photo_bytes = BytesIO(img)
        image = upload.photo_messages(photo_bytes)[0]

        owner_id = image['owner_id']
        photo_id = image['id']
        peer_id = idu
        photo_bytes.close()  # ???
        print(f'фотография id{photo_id} скачана')

        text = f'Фотография из профиля'
        attachment = f'photo{str(owner_id)}_{str(photo_id)}'
        params = {'peer_id': peer_id, 'message': text, 'attachment': attachment, 'random_id': randrange(10 ** 7)}
        vk.method('messages.send', params)
        print(f'фотография id{photo_id} отправлена пользователю id{peer_id}')


def text_message(idu, text, token=token_group):
    """Отправка текстовых сообщение клиенту"""
    print('запуск функции text_massage')
    vk = vk_api.VkApi(token=token)
    vk.method('messages.send', {'user_id': idu, 'message': text, 'random_id': randrange(10 ** 7), })
    print(f'сообщение: "{text}" отправлено пользователю id{idu}')
