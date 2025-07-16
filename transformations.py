import subprocess
from pathlib import Path
import os
import pandas as pd
import json
import ezdxf
from ezdxf import bbox

def dwg_to_dxf(dwg_path: Path,dxf_path: Path):
    """
    Converte um DWG em DXF usando o dwgread (ou ODA Converter etc.)
    e devolve o caminho do DXF gerado.
    """
    cmd = ["dwgread", "-O", "dxf", "-o", str(dxf_path), str(dwg_path)]

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )
    # Se precisar logar:
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr)

def dxf_to_geojson(dxf_path:Path,geojson_path:Path):
    if not os.path.exists(dxf_path):
        raise FileNotFoundError(f"Arquivo DXF não encontrado: {dxf_path}")
    cmd = ['ogr2ogr', '-f' ,'GeoJSON', '-s_srs', 'EPSG:31982' ,'-t_srs', 'EPSG:4326', '--config', 'DXF_FEATURE_LIMIT_PER_BLOCK', '-1', str(geojson_path),str(dxf_path)]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr)

def dwg_to_geojson(dwg_path:Path,geojson_path:Path):
    if not os.path.exists(dwg_path):
        raise FileNotFoundError(f"Arquivo DXF não encontrado: {dwg_path}")
    cmd = ["dwgread", "-O", "Geojson", "-o", str(geojson_path), str(dwg_path)]

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr)

def change_geojson_timezone(geojson_path:Path,output_path:Path,input_timezone:str,output_timezone:str):
    if not os.path.exists(geojson_path):
        raise FileNotFoundError(f"Arquivo Geojson não encontrado: {geojson_path}")
    cmd = ["ogr2ogr", "-f", "GeoJSON", "-s_srs", input_timezone, "-t_srs", output_timezone, str(output_path) ,str(geojson_path)]
    
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr)

def set_geojson_colors(geojson_path:Path,df:pd.DataFrame):
    with open(str(geojson_path),'r',encoding='utf-8') as f:
        dados_geojson = json.load(f)
    mapa_cores = dict(zip(df["Layer"],df['HexColor']))
    for feature in dados_geojson["features"]:
        layer_name = feature['properties'].get('Layer','')
        color = mapa_cores.get(layer_name,'#000000')
        feature['properties']['color'] = color
    with open(str(geojson_path),'w',encoding='utf-8') as f:
        json.dump(dados_geojson,f,indent=None,ensure_ascii=False)
def add_bounding_box_to_geojson(geojson_path:Path,dxf_path:Path):
    doc = ezdxf.readfile(str(dxf_path))
    msp = doc.modelspace()

    box = bbox.extents(msp)
    vertices = box.rect_vertices()

    with open(str(geojson_path), 'r',encoding='utf-8') as f:
        json_data = json.load(f)
    
    path = [[v.x, v.y] for v in vertices]
    path.append(path[0])

    print(path)

    box_feature = {
        "type": "Feature",
        "properties":{
            "name": "Box ModelSpace",
            "isBoundingBox":"true"
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [path]
        }
    }

    json_data['features'].append(box_feature)

    with open(geojson_path, 'w',encoding='utf-8') as f:
        json.dump(json_data, f, indent=None)

