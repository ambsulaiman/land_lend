from sqlmodel import Session
from fastapi import HTTPException
from ..database import engine
from ..schemas.models import ImageIn, Image

import os

LAND_LEND_IMAGES_DIR = os.getenv('LAND_LEND_IMAGES_DIR', os.path.join(os.environ['HOME'], 'images'))

DOMAIN_NAME = 'http://localhost:4545/' # image server domain name.

async def _save_image(image):
    try:
        file_path = os.path.join(LAND_LEND_IMAGES_DIR, image.filename)

        content = await image.read()
        with open(file_path, 'wb') as fp:
            try:
                fp.write(content)
            except OSError as e:
                print(f'Image write error: {e}')

    except OSError as e:
        print('File Error', e)

async def _save_image_db(image: ImageIn, land_id: int):
    url = DOMAIN_NAME + image.filename

    with Session(engine) as session:
        image_db = Image(label=image.filename, url=url, land_id=land_id)

        session.add(image_db)
        session.commit()

async def save_images(images: list[ImageIn], land_id):
    for image in images:
        if image.content_type.split('/')[-1] not in ['jpeg', 'JPEG', 'png', 'PNG']:
            raise HTTPException(status_code=400, detail='Invalid file type. File must be of type: jpeg or png.')

        await _save_image(image)
        await _save_image_db(image, land_id)

async def delete_image(image_label: str):
    try:
        file_path = os.path.join(LAND_LEND_IMAGES_DIR, image_label)
        try:
            os.remove(file_path)
        except OSError as e:
            print(f'Image Delete error: {e}')

    except OSError as e:
        print('File Error', e)