import requests
import json
import os
from tqdm import tqdm
from time import sleep


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
        photos_load = []
        max_size_photo = {}

        if not os.path.exists('vk_backup'):
            os.mkdir('vk_backup')

        while i <= photo_count:
            if i != 0:
                profile_list = self.get_profile_photos()

            for photo in tqdm(profile_list['response']['items']):
                sleep(0.25)
                max_size = 0
                photos_info = {}
                for size in photo['sizes']:
                    if size['height'] >= max_size:
                        max_size = size['height']
                if photo['likes']['count'] not in max_size_photo.keys():
                    max_size_photo[photo['likes']['count']] = size['url']
                    photos_info['file_name'] = f"{photo['likes']['count']}.jpg"
                else:
                    max_size_photo[f"{photo['likes']['count']} + {photo['date']}"] = size['url']
                    photos_info['file_name'] = f"{photo['likes']['count']} + {photo['date']}.jpg"

                photos_info['size'] = size['type']
                photos_load.append(photos_info)

            for photo_name, photo_url in max_size_photo.items():
                with open('vk_backup/%s' % f'{photo_name}.jpg', 'wb') as file:
                    img = requests.get(photo_url)
                    file.write(img.content)

                with open('photos_load.json', 'w') as file:
                    json.dump(photos_load, file)


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

    def upload_vk_image(self):
        url_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {'Authorization': f'OAuth {ya_token}'
                   }
        params = {'path': 'image_backup_vk/image'
                  }
        response = requests.get(url=url_upload, headers=headers, params=params)
        link_upload = response.json().get('href')

        with open('vk_backup/img', 'rb') as file:
            response = requests.put(link_upload, files={'file': file})
            return response.json()
