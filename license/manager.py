import requests
import os
import datetime
import re
import getpass
from loguru import logger

BASE_URL = 'https://api.github.com/licenses'


def list_licenses():
    response = requests.get(BASE_URL)
    licenses = []
    for license_data in response.json():
        licenses.append(license_data['key'])
    return licenses


def fetch_license(license_name: str):
    response = requests.get(f'{BASE_URL}/{license_name}')
    return response.json()['body']


if __name__ == "__main__":
    print(fetch_license(list_licenses()[1]))


class LicenseManager:
    def __init__(self, licenses_folder: str = None):
        self.licenses_folder = licenses_folder

    def __add_format(self, license_content: str) -> str:
        license_content = license_content.replace('[yyyy]', '{year}')
        license_content = license_content.replace('[name of copyright owner]', '{name}')
        license_content = license_content.replace('[year]', '{year}')
        license_content = license_content.replace('[fullname]', '{name}')
        return license_content

    def update(self):
        if self.licenses_folder is None:
            logger.error('Failed to update. Licenses folder is not specified.')
            return
        for license_name in list_licenses():
            license_path = os.path.join(self.licenses_folder, license_name)
            with open(license_path, 'w+') as f:
                license_content = fetch_license(license_name)
                license_content = self.__add_format(license_content)
                f.write(license_content)
        
    def get(self, license_name: str, local_only: bool = False) -> str:
        if self.licenses_folder is None:
            if local_only:
                raise FileNotFoundError('License could not be found.')
            return fetch_license(license_name)
        else:
            license_path = os.path.join(self.licenses_folder, license_name)
            if os.path.exists(license_path):
                with open(license_path) as f:
                    license_content = ''.join(f.readlines())
                license_content = license_content.format(
                    year=datetime.date.today().year,
                    name=getpass.getuser(),
                )
                return license_content
            elif local_only:
                raise FileNotFoundError('License could not be found.')
            else:
                self.update()
                return self.get(license_name, local_only=True)
