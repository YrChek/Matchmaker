import vk_api
import time

token_app = ''


def search_users(token, city, sex):
    """Поиск всех пользователей в VK по городу и полу со статусом в активном поиске"""
    print(f'начат поиск кандидатов города {city}')
    vk = vk_api.VkApi(token=token)
    params = {'count': '200', 'fields': 'city,bdate,sex,relation',
              'hometown': city, 'sex': sex, 'status': '6', 'has_photo': '1', 'v': '5.131'}
    res = vk.method('users.search', params)
    count = len(res['items'])
    print(f'найдено {count} кандидатов')
    return res


def select_users(array, idu, user_date, user_sex):
    """Отбор пользователей с открытой страницей и полными основными данными"""
    print('начат отбор кандидатов по требованиям')
    names = []
    for data in array['items']:
        temp_names = []

        if data['is_closed']:
            continue
        temp_names.append(int(idu))

        if 'id' in data:
            ids = data['id']
        else:
            continue
        temp_names.append(int(ids))

        if 'first_name' in data:
            name = data['first_name']
            if 'last_name' in data:
                last = data['last_name']
                full_name = f'{name} {last}'
            else:
                full_name = name
            temp_names.append(full_name)
        else:
            continue

        if 'bdate' in data:
            bdate = data['bdate']
            if len(bdate) > 5:
                number = True
                for i in bdate[-4:]:
                    if i not in '0123456789':
                        number = False
                        break
                if number:
                    year = int(bdate[-4:])
                else:
                    continue
            else:
                continue
            current_year = time.localtime().tm_year
            user_date = int(user_date)
            if year > current_year - 18:
                continue
            if user_sex == 1:
                lower_age_limit = user_date + 2
            else:
                lower_age_limit = user_date + 7
            if year > lower_age_limit:
                continue
            temp_names.append(year)
        else:
            continue

        if 'city' in data:
            if 'title' in data['city']:
                city = data['city']['title']
                temp_names.append(city)
            else:
                continue
        else:
            continue

        if 'sex' not in data:
            continue
        temp_names.append(int(data['sex']))

        if 'relation' in data:
            if data['relation'] == 6:
                pass
            else:
                continue
        else:
            continue

        names.append(temp_names)
    count = len(names)
    print(f'отобрано {count} кандидатов')

    return names


def candidat_list(idu, user_date, city, user_sex, token=token_app):
    """Список отобранных кандидатов"""
    print('Запуск поиска кандидатов')
    sex = 3 - user_sex
    array = search_users(token, city, sex)
    finish_list = select_users(array, idu, user_date, user_sex)
    return finish_list


def photo_user(ids, token=token_app):
    """Выбор фотографий конкретного пользователя"""
    print(f'запуск функции выбора фотографий пользователя id{ids}')
    not_sorted_list = []
    vk = vk_api.VkApi(token=token)
    params = {'owner_id': ids, 'album_id': 'profile', 'rev': '1', 'extended': '1', 'count': '20'}
    photos = vk.method('photos.get', params)
    for data in photos['items']:
        rating = data['likes']['count'] + data['comments']['count']
        not_sorted_list += [[rating, data['sizes'][-1]['url']]]
    sort_list = sorted(not_sorted_list)
    if len(sort_list) > 3:
        print('отобрано 3 фотографии')
        return sort_list[-3:]
    else:
        print(f'отобрано фотографий: {len(sort_list)}')
        return sort_list


def check_city(city, token=token_app):
    """Проверка наличия города"""
    print(f'запуск проверки названия города {city}')
    vk = vk_api.VkApi(token=token)
    params = {'country_id': '1', 'q': city, 'count': '1'}
    response = vk.method('database.getCities', params)
    if response['count'] != 0:
        print('город найден')
        return True
    else:
        print('город не найден')
        return False
