from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse,FileResponse
import shutil, tempfile
from pathlib import Path
import uuid

from transformations import dwg_to_dxf,dxf_to_geojson,set_geojson_colors
from colors import get_layers_color
app = FastAPI(title="DWG converter")

@app.get("/test")
async def test():
    return {"message":"OK"}

@app.post("/convert")
async def upload_dwg(file: UploadFile = File(...)):
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

        return FileResponse(str(geojsonPath))
    finally:
        tmp_path.unlink(missing_ok=True)