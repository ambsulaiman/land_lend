from sqlmodel import Session
from fastapi import HTTPException
from ..database import engine
from ..schemas.models import ImageIn, Image

import os
import string
import random

LAND_RENT_IMAGES_DIR = os.getenv('LAND_RENT_IMAGES_DIR', os.path.join(os.environ['HOME'], 'images'))

DOMAIN_NAME = 'http://localhost:4545/' # image server domain name.

def generate_random_name(file_extension, length=10):
    return ''.join(random.choice(string.ascii_letters) for i in range(length)) + '.' + file_extension

async def _save_image(image):
    global file_name

    file_name = generate_random_name(image.content_type.split('/')[-1])
    try:
        file_path = os.path.join(LAND_RENT_IMAGES_DIR, file_name)

        content = await image.read()
        with open(file_path, 'wb') as fp:
            try:
                fp.write(content)
            except OSError as e:
                print(f'Image write error: {e}') #

    except OSError as e:
        print('File Error', e) #

async def _save_image_db(land_id: int, update=False):
    url = DOMAIN_NAME + file_name

    if update:
        return

    with Session(engine) as session:
        image_db = Image(label=file_name, url=url, land_id=land_id)

        session.add(image_db)
        session.commit()

async def save_images(images: list[ImageIn], land_id, update=False):
    for image in images:
        if image.content_type.split('/')[-1] not in ['jpeg', 'JPEG', 'png', 'PNG']:
            raise HTTPException(status_code=400, detail='Invalid file type. File must be of type: jpeg or png.')

        await _save_image(image)
        await _save_image_db(land_id, update=update)

async def delete_image(image_label: str):
    try:
        file_path = os.path.join(LAND_RENT_IMAGES_DIR, image_label)
        try:
            os.remove(file_path)
        except OSError as e:
            print(f'Image Delete error: {e}') #

    except OSError as e:
        print('File Error', e) #