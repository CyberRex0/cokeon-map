from typing import Dict, List, Optional
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import config
import databases
import datetime
import pymysql
import sqlalchemy

pymysql.install_as_MySQLdb()

database = databases.Database(config.DATABASE_URL)

metadata = sqlalchemy.MetaData()

markers = sqlalchemy.Table(
    'markers',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('lat', sqlalchemy.String(64)),
    sqlalchemy.Column('lng', sqlalchemy.String(64)),
    sqlalchemy.Column('memo', sqlalchemy.String(300)),
    sqlalchemy.Column('createdAt', sqlalchemy.DateTime)
)

engine = sqlalchemy.create_engine(
    config.DATABASE_URL
)
metadata.create_all(engine)

class Marker(BaseModel):
    id: int = None
    lat: str
    lng: str
    memo: Optional[str]
    createdAt: datetime.datetime = None

class MarkerIn(BaseModel):
    lat: str
    lng: str

class MarkerOut(BaseModel):
    latlng: List[str]
    label: str = ''

class MarkerDeleteParam(BaseModel):
    id: int

class MarkerUpdateParam(BaseModel):
    id: int
    memo: str

app = FastAPI()
api = FastAPI()
app.mount('/api', api)
app.mount('/', StaticFiles(directory='dist', html=True), name='static')

@app.on_event('startup')
async def on_startup():
    await database.connect()

@app.on_event('shutdown')
async def on_shutdown():
    await database.disconnect()

@api.get('/v1/markers/list', response_model=List[Marker])
async def api_get_v1_markers_list():
    q = markers.select()
    mkrs = await database.fetch_all(q)
    #data = []
    #for mkr in mkrs:
    #    mkr: Marker
    #    data.append({
    #        'latlng': [mkr.lat, mkr.lng],
    #        'label': 'Label'
    #    })
    return mkrs

@api.post('/v1/markers/create', response_model=Marker)
async def api_post_v1_markers_create(m: MarkerIn):
    print(m)
    q = markers.insert().values(lat=m.lat, lng=m.lng, createdAt=datetime.datetime.now())
    r = await database.execute(q)
    q2 = markers.select().where(markers.c.id == r)
    r2 = await database.fetch_one(q2)
    return r2

@api.post('/v1/markers/delete')
async def api_post_v1_markers_delete(m: MarkerDeleteParam):
    q = markers.delete().where(markers.c.id == m.id)
    r = await database.execute(q)

@api.post('/v1/markers/update')
async def api_post_v1_markers_update(m: MarkerUpdateParam):
    q = markers.update().values(memo=m.memo).where(markers.c.id == m.id)
    r = await database.execute(q)