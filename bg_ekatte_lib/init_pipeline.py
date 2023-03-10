import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box


def get_bbox_polygon(row):
    return box(row['minx'], row['miny'], row['maxx'], row['maxy'])


def plot_map(gdf: gpd, to_file: str):
    gdf.plot(figsize=(12, 12), facecolor="none", edgecolor='red', lw=0.3)
    plt.savefig(to_file)


def drop_fields(df, columns: List) -> Any:
    for col in columns:
        try:
            del df[col]
        except Exception as ex:
            print(ex)
    return df


def get_ekatte_df(base_path: str) -> List:

    df = pd.read_json(os.path.join(base_path, 'ek_atte.json'))

    generation_field = "Дата и час на изготвяне на справката"
    release_field = "Данните са актуални към"

    release_date = list(df[df[release_field].notna()][release_field].values)[0]
    generation_date = list(df[df[generation_field].notna()][generation_field].values)[0]

    df = drop_fields(df, [generation_field, release_field])
    df = df.drop_duplicates()
    df = df.dropna(how='all')
    df.to_parquet('../data/processed/v20230131/ekatte.pq', index=False)
    return [df, generation_date, release_date]


def get_ekatte_bbox(base_shape_path: str) -> List:
    gdf = gpd.read_file(base_shape_path)
    gdf.rename(columns={'EKATTE_1': 'ekatte'}, inplace=True)

    plot_map(gdf=gdf, to_file="../data/processed/v20230131/srs_ekatte.png")

    gdf_wgs84 = gdf.to_crs("EPSG:4326")
    plot_map(gdf=gdf_wgs84, to_file="../data/processed/v20230131/wgs84_ekatte.png")

    gdf_wgs84 = pd.concat([gdf_wgs84, gdf_wgs84.bounds], axis=1)
    gdf_wgs84['ext_geometry'] = gdf_wgs84.apply(lambda row: get_bbox_polygon(row), axis=1)
    gdf_wgs84.rename(columns={'geometry': 'srs_geometry', 'ext_geometry': 'geometry'}, inplace=True)
    gdf_wgs84 = drop_fields(df=gdf_wgs84, columns=["srs_geometry", "minx", "miny", "maxx", "maxy"])
    gdf_wgs84.set_crs("EPSG:4326", inplace=True)

    gdf_wgs84.to_feather("../data/processed/v20230131/ekatte_geo.feather")

    gdf_3857 = gdf_wgs84.to_crs("EPSG:3857")
    plot_map(gdf=gdf_3857, to_file="../data/processed/v20230131/wgs84_ekatte_ext.png")

    return []


if __name__ == "__main__":

    Path('/mapsapps/projects/bg-ekatte-lib/data/processed').mkdir(parents=True, exist_ok=True)
    Path('/mapsapps/projects/bg-ekatte-lib/data/processed/v20230131/').mkdir(parents=True, exist_ok=True)

    BASE_PATH = "/mapsapps/projects/bg-ekatte-lib/data/source_data/v_202212_202301/Ekatte_json/"
    df_ekatte = get_ekatte_df(base_path=BASE_PATH)

    BG_ZEMS = '/mapsdata/sources/ekatte_shapefile/ekatte.shp'
    df_ekatte_geom = get_ekatte_bbox(base_shape_path=BG_ZEMS)
