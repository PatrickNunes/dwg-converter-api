from fastapi import FastAPI, UploadFile, File,BackgroundTasks
from fastapi.responses import FileResponse
import shutil, tempfile
from pathlib import Path
import uuid
import os

from transformations import dwg_to_dxf,dxf_to_geojson,set_geojson_colors
from colors import get_layers_color

app = FastAPI(title="DWG converter")

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
        dxfPath = Path(f'./upload/{uuidName}.dxf')
        geojsonPath = Path(f'./upload/{uuidName}.geojson')

        dwg_to_dxf(tmp_path,dxfPath)
        dxf_to_geojson(dxfPath,geojsonPath)
        df = get_layers_color(dxfPath)
        set_geojson_colors(geojsonPath,df)

        background_tasks.add_task(remove_files,[dxfPath,geojsonPath])

        return FileResponse(str(geojsonPath)) 
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