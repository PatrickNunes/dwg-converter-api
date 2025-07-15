import ezdxf
from ezdxf.colors import aci2rgb
from pathlib import Path
import pandas as pd

def safe_aci2rgb(aci):
    if 0 <= aci <= 255:
        return aci2rgb(aci)
    else:
        # Retorna preto ou cor padrão para valores inválidos
        return (0, 0, 0)

def get_layers_color(dxf_path:Path) -> pd.DataFrame:
    doc = ezdxf.readfile(str(dxf_path))
    data = []
    for e in doc.layers:
        try:
            layer = e.dxf.name
            color_index = e.dxf.color
            r,g,b = safe_aci2rgb(color_index)
            hex_color = "#{:02X}{:02X}{:02X}".format(r, g, b)
            data.append((layer,color_index,hex_color))
        except AttributeError:
            continue
    df = pd.DataFrame(data,columns=["Layer", "ColorACI", "HexColor"])
    return df
