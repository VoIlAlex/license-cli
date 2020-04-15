import click
import os
from license.manager import LicenseManager
from appdata import AppDataPaths
from loguru import logger

@click.command()
@click.argument('license-name')
@click.option('-p', '--print', 'print_', is_flag=True)
def cli(license_name, print_):
    app_data_paths = AppDataPaths(
        app_name='license', 
        root_appdata='.opensource', 
        with_dot=False
    )
    if app_data_paths.require_setup():
        app_data_paths.setup()

    licenses_folder = app_data_paths.join('licenses')
    if not os.path.exists(licenses_folder):
        os.makedirs(licenses_folder)

    manager = LicenseManager(
        licenses_folder=licenses_folder
    )
    try:
        license_content = manager.get(license_name)
    except FileNotFoundError:
        logger.error('Cannot find the specified license.')
        exit(-1)
    if print_:
        print(license_content)
    else:
        with open('./LICENSE.md', 'w+') as f:
            f.write(license_content)
