# Bismillah

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from sqlmodel import select, Session, or_
from ..schemas.models import User, Land, LandIn, LandOut, LandOutWithUsers, LandUpdate, Image, ImagesUpdate, ImageOut 
from ..schemas.enums import RoleEnum
from ..database import get_session
from ..utils.logic import save_images, delete_image
from ..utils.security import (
			get_password_hash,
			get_current_active_user,
			authorize_user
)

router = APIRouter(
    prefix='/lands'
)

@router.post('/', status_code=201, dependencies=[Depends(authorize_user([RoleEnum.admin]))])
async def register_land(*,
	land: Land,
	session: Annotated[Session, Depends(get_session)]
):
	db_land = session.exec(
		select(Land).where(Land.name == land.name)
	).first()
	if db_land:
		raise HTTPException(status_code=404, detail='Land already registered, if not consider changing the name')

	session.add(land)
	session.commit()

@router.get('/',
	dependencies=[
		Depends(
			authorize_user(
				[RoleEnum.normal_user,
				RoleEnum.security,
				RoleEnum.staff]
			)
		)
	],
	response_model=list[LandOutWithUsers]
)
async def fetch_land_info(*,
	skip: int = 0,
	limit: int = 100,
	address: str | None = None,
	location: str | None = None,
	size_lesser: int | None = None,
	size_greater: int | None = None,
	description: str | None = None,
	session: Annotated[Session, Depends(get_session)],
):

	stmt = select(Land)

	if address:
		stmt = stmt.where(Land.address == address)
	if description:
		stmt = stmt.where(Land.description == description)
	if location:
		stmt = stmt.where(Land.location == location)
	if size_lesser:
		stmt = stmt.where(Land.size_lesser < size_lesser)
	if size_greater:
		stmt = stmt.where(size_greater > size_greater)
	
	lands = session.exec(
		stmt.offset(skip).limit(limit)
	).all()

	if not lands:
		raise HTTPException(status_code=404, detail='No Found!. Refresh the filter and reload')

	return lands

@router.patch(
	'/',
	dependencies=[Depends(authorize_user(RoleEnum.admin))],
	response_model=LandOut
)
async def update_land_info(land_id:int, update_data: LandUpdate, session: Annotated[Session, Depends(get_session)]):
	land = session.get(Land, land_id)

	if not land:
		raise HTTPException(status_code=404, detail='Land not Found.')
	
	update_data = Land.model_dump(update_data, exclude_unset=True)

	land.sqlmodel_update(update_data)

	session.add(land)
	session.commit()
	
	session.refresh(land)

	return land

@router.delete('/{land_id}')
async def delete_land_info(
	land_id: int,
	user: Annotated[User, Depends(authorize_user(RoleEnum.admin))],
	session: Annotated[Session, Depends(get_session)]
):
	land = session.get(Land, land_id)
	if not land:
		raise HTTPException(status_code=404, detail='Land not found.')

	session.delete(land)
	session.commit()

	return {'msg': 'Land info successfully deleted!.', 'ok': True}


################
## land images
################

@router.post(
	'/{land_id}/images/',
	dependencies=[Depends(authorize_user([RoleEnum.admin]))],
	response_model=dict[str, str | bool]
)
async def register_images(
	land_id: int,
	images: Annotated[list[UploadFile], File()],
	session: Annotated[Session, Depends(get_session)]
):
    db_land = session.get(Land, land_id)
    if not db_land:
        raise HTTPException(status_code=404, detail=f'Land with id={land_id}')

    image_exists = session.exec(
        select(Image).where(Image.label in [image.filename for image in images]) ### reconsider
    ).first()
    if image_exists:
        raise HTTPException(status_code=404, detail='Image already exists. If not try changing the lable.')

    await save_images(images, land_id)

    return {'msg': 'Images added successfully.', 'ok': True}

@router.patch(
    '/{land_id}/images/{image_id}',
    response_model=ImageOut
)
async def update_land_image(
    image_id: int,
    land_id: int,
    image: ImagesUpdate,
    session: Annotated[Session, Depends(get_session)]
):
    db_image = session.exec(
        select(Image).where(Image.id == image_id, Image.land_id == land_id)
    ).first()

    if not db_image:
        raise HTTPException(status_code=404, detail=f'Image with id={image_id} and land_id={land_id}')
    
    db_image.label = image.label

    session.add(db_image)
    session.commit()
    session.refresh(db_image)

    return db_image

@router.delete(
    '/images/{image_id}',
    response_model=dict[str, str | bool]
)
async def delete_land_image(
    image_id: int,
    session: Annotated[Session, Depends(get_session)]
):
    image = session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f'Image with id={image_id} not found.')
    
    await delete_image(image.label)

    session.delete(image)
    session.commit()

    return {'msg': f'Deleted image {image.label}, successfully.', 'ok': True}