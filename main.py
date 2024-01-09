import requests
import json
import os
from tqdm import tqdm
from time import sleep

# OAUTH_BASE_URL = 'https://oauth.vk.com/authorize'
# params = {
#     'client_id': '51826793',
#     'redirect_uri': 'https://oauth.vk.com/blank.html',
#     'display': 'page',
#     'scope': 'photos',
#     'response_type': 'token',
#     'v': '5.131',
#     'state': '123456'
# }
# oauth_url = f'{OAUTH_BASE_URL}?{urlencode(params)}'
# print(oauth_url)

vk_token = ('vk1.a.7ePWBuj64ndCTEv8T8vEVe64HvrJ6_pD0S3DpJs4SX56VOme7TyplFEAp9DE1qB2CynGL1j_hHPCdwPxEGEr-RJx3iArdu_'
            'GgDZto1hMzGFVMAWFXuxSLuc0Cb2Xgdkm_H0bJ3alQwKfoWqwcj3Q7FOm064Ku2xdeasOnDiqHtSDYJyaSd8mC6FuwxOrJrqi')


class PhotosLoad:
    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_profile_photos(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.user_id,
                  'album_id': 'profile',
                  'access_token': self.token,
                  'v': '5.199',
                  'extended': '1',
                  'photo_sizes': '1',
                  'count': 5
                  }
        response = requests.get(url=url, params=params)
        return response.json()

    def maxsize_photo(self):
        profile_list = self.get_profile_photos()
        photo_count = profile_list['response']['count']
        i = 0
        photos_load = []  # Список всех загруженных фото
        max_size_photo = {}  # Словарь с парой название фото - URL фото максимального разрешения

        # Создаём папку на компьютере для скачивания фотографий
        if not os.path.exists('vk_backup'):
            os.mkdir('vk_backup')

        while i <= photo_count:
            if i != 0:
                profile_list = self.get_profile_photos()

            # Проходимся по всем фотографиям
            for photo in tqdm(profile_list['response']['items']):
                sleep(0.25)
                max_size = 0
                photos_info = {}
                # Выбираем фото максимального разрешения и добавляем в словарь max_size_photo
                for size in photo['sizes']:
                    if size['height'] >= max_size:
                        max_size = size['height']
                if photo['likes']['count'] not in max_size_photo.keys():
                    max_size_photo[photo['likes']['count']] = size['url']
                    photos_info['file_name'] = f"{photo['likes']['count']}.jpg"
                else:
                    max_size_photo[f"{photo['likes']['count']} + {photo['date']}"] = size['url']
                    photos_info['file_name'] = f"{photo['likes']['count']} + {photo['date']}.jpg"

                # Формируем список всех фотографий для дальнейшей упаковки в .json

                photos_info['size'] = size['type']
                photos_load.append(photos_info)

            # Скачиваем фотографии
            for photo_name, photo_url in max_size_photo.items():
                with open('vk_backup/%s' % f'{photo_name}.jpg', 'wb') as file:
                    img = requests.get(photo_url)
                    file.write(img.content)

        # Записываем данные о всех скачанных фоторафиях в файл .json
                with open('photos_load.json', 'w') as file:
                    json.dump(photos_load, file)



ya_token = 'y0_AgAAAAATWKIRAADLWwAAAAD3in6EUUDUhptRTm-GBy7bgIk5-4NmoJc'
url = 'https://cloud-api.yandex.net'

class PhotosUpload:
    def __init__(self, token):
        self.token = token

    def ya_folder_create(self):
        url_create_folder = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': 'image_backup_vk'
                  }
        headers = {'Authorization': f'OAuth {ya_token}'
                   }
        response = requests.put(url=url_create_folder, headers=headers, params=params)
        return response.json()


    def upload_vk_image(self, file_path: str):
        url_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {'Authorization': f'OAuth {ya_token}'
                   }
        params = {'path': 'image_backup_vk/image'
                  }

        # Получение ссылки на загрузку
        response = requests.get(url=url_upload, headers=headers, params=params)
        link_upload = response.json().get('href')

        # Загрузка файла
        with open('vk_backup/img', 'rb') as file:
            response = requests.put(link_upload, files={'file': file})
            return response.json()
#
#
#
# if __name__ == '__main__':
#     vk_client = PhotosLoad(vk_token, 815560160)
#     photos_info = vk_client.get_profile_photos()
#     print(photos_info)
#     max_size_photo = vk_client.maxsize_photo()
#     print(max_size_photo)
