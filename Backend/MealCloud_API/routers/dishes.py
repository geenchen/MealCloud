from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from auth import get_current_active_user
from database import get_db
from models.dish import Category as CategoryModel
from models.dish import Dish as DishModel
from models.user import User
from schemas.dish import Dish, DishCreate, DishUpdate

router = APIRouter()
UPLOAD_DIR = Path(__file__).resolve().parents[1] / 'static' / 'uploads' / 'dishes'
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


@router.post('/dishes/upload-image')
@router.post('/dishes/upload-image/', include_in_schema=False)
async def upload_dish_image(
    request: Request,
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
):
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail='Only JPG/PNG/WEBP images are supported')

    file_ext = Path(image.filename or '').suffix.lower()
    if file_ext not in {'.jpg', '.jpeg', '.png', '.webp'}:
        file_ext = '.jpg'

    content = await image.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail='Image size cannot exceed 5MB')

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f'dish_{uuid4().hex}{file_ext}'
    save_path = UPLOAD_DIR / filename
    save_path.write_bytes(content)

    relative_url = f'/static/uploads/dishes/{filename}'
    absolute_url = str(request.base_url).rstrip('/') + relative_url
    return {'image_url': relative_url, 'image_full_url': absolute_url}


@router.get('/dishes', response_model=list[Dish])
async def get_dishes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return db.query(DishModel).filter(DishModel.is_available == True).offset(skip).limit(limit).all()


@router.get('/dishes/search')
async def search_dishes(
    q: str | None = None,
    category_id: int | None = None,
    is_available: bool | None = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(DishModel)

    if q:
        query = query.filter(DishModel.name.contains(q))
    if category_id:
        query = query.filter(DishModel.category_id == category_id)
    if is_available is not None:
        query = query.filter(DishModel.is_available == is_available)

    return query.all()


@router.get('/dishes/category/{category_id:int}', response_model=list[Dish])
async def get_dishes_by_category(
    category_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(DishModel)
        .filter(DishModel.category_id == category_id, DishModel.is_available == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get('/dishes/{dish_id:int}', response_model=Dish)
async def get_dish(
    dish_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    dish = db.query(DishModel).filter(DishModel.id == dish_id).first()
    if dish is None or not dish.is_available:
        raise HTTPException(status_code=404, detail='Dish not found')
    return dish


@router.post('/dishes', response_model=Dish)
async def create_dish(
    dish: DishCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    category = db.query(CategoryModel).filter(CategoryModel.id == dish.category_id).first()
    if not category or not category.is_active:
        raise HTTPException(status_code=400, detail='Category not found')

    existing_dish = db.query(DishModel).filter(DishModel.name == dish.name).first()
    if existing_dish:
        raise HTTPException(status_code=400, detail='Dish name already exists')

    db_dish = DishModel(**dish.model_dump())
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish


@router.put('/dishes/{dish_id:int}', response_model=Dish)
async def update_dish(
    dish_id: int,
    dish_update: DishUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_dish = db.query(DishModel).filter(DishModel.id == dish_id).first()
    if db_dish is None:
        raise HTTPException(status_code=404, detail='Dish not found')

    if dish_update.category_id is not None:
        category = db.query(CategoryModel).filter(CategoryModel.id == dish_update.category_id).first()
        if not category or not category.is_active:
            raise HTTPException(status_code=400, detail='Category not found')

    update_data = dish_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_dish, field, value)

    db.commit()
    db.refresh(db_dish)
    return db_dish


@router.delete('/dishes/{dish_id:int}')
async def delete_dish(
    dish_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_dish = db.query(DishModel).filter(DishModel.id == dish_id).first()
    if db_dish is None:
        raise HTTPException(status_code=404, detail='Dish not found')

    db_dish.is_available = False
    db.commit()
    return {'message': 'Dish disabled'}
