from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from auth import get_current_active_user, get_password_hash
from config import settings
from database import SessionLocal, create_tables, database
from models.user import User

app = FastAPI(title='MealCloud API', version='1.0.0')

cors_origins = [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(',') if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

static_dir = Path(__file__).resolve().parent / 'static'
static_dir.mkdir(parents=True, exist_ok=True)
app.mount('/static', StaticFiles(directory=static_dir), name='static')


def ensure_default_admin() -> None:
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == 'admin').first()
        if admin:
            return

        if not settings.DEFAULT_ADMIN_PASSWORD:
            print('[WARN] DEFAULT_ADMIN_PASSWORD not configured. Skip creating default admin user.')
            return

        db.add(
            User(
                username='admin',
                email='admin@mealcloud.local',
                full_name='System Admin',
                hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                is_active=True,
                is_admin=True,
            )
        )
        db.commit()
    finally:
        db.close()


@app.on_event('startup')
async def startup():
    await database.connect()
    create_tables()
    ensure_default_admin()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()


from routers import areas, auth, categories, dishes, orders, tables, users

app.include_router(auth.router, prefix='/api/v1', tags=['auth'])
app.include_router(users.router, prefix='/api/v1', tags=['users'])
app.include_router(dishes.router, prefix='/api/v1', tags=['dishes'])
app.include_router(orders.router, prefix='/api/v1', tags=['orders'])
app.include_router(tables.router, prefix='/api/v1', tags=['tables'])
app.include_router(areas.router, prefix='/api/v1', tags=['areas'])
app.include_router(categories.router, prefix='/api/v1', tags=['categories'])


@app.get('/')
async def read_root():
    return {'message': 'MealCloud API is running'}


@app.get('/health')
async def health_check():
    return {'status': 'healthy', 'message': 'MealCloud API is healthy'}


@app.get('/api/v1/status')
async def read_status(current_user: User = Depends(get_current_active_user)):
    return {'status': 'authenticated', 'user': current_user.username}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8008, reload=True)
