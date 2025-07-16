from fastapi import FastAPI, UploadFile, File,BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil, tempfile
from pathlib import Path
import uuid
import os

from transformations import dwg_to_dxf,dxf_to_geojson,set_geojson_colors,dwg_to_geojson,change_geojson_timezone,add_bounding_box_to_geojson
from colors import get_layers_color

app = FastAPI(title="DWG converter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
async def test():
    return {"message":"OK"}

@app.post("/convert")
async def upload_dwg(background_tasks: BackgroundTasks,file: UploadFile = File(...)):
    try:
        suffix = Path(file.filename).suffix or ".dwg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        file.file.close()
    try:
        uuidName = uuid.uuid4()
        dxf_path = Path(f'./upload/{uuidName}.dxf')
        geojson_path = Path(f'./upload/{uuidName}.geojson')
        geojson_converted_path = Path(f'./upload/converted_{uuidName}.geojson')

        dwg_to_dxf(tmp_path,dxf_path)
        dwg_to_geojson(tmp_path,geojson_path)
        add_bounding_box_to_geojson(geojson_path,dxf_path)
        change_geojson_timezone(geojson_path,geojson_converted_path,"EPSG:31982","EPSG:4326")
        df = get_layers_color(dxf_path)
        set_geojson_colors(geojson_converted_path,df)

        background_tasks.add_task(remove_files,[dxf_path,geojson_path,geojson_converted_path])

        return FileResponse(str(geojson_converted_path)) 
    finally:
        tmp_path.unlink(missing_ok=True)

def remove_files(paths:list[Path]):
    try:
        for path in paths:
            if os.path.exists(path):
                os.remove(path)
    except Exception as e:
        print("Erro ao remover arquivos")
        print(e)