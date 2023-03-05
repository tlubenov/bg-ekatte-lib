import os
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box


def get_bbox_polygon(row):
    return box(row['minx'], row['miny'], row['maxx'], row['maxy'])


def get_ekatte_df(base_path: str) -> List:

    df = pd.read_json(os.path.join(base_path, 'ek_atte.json'))

    generation_field = "Дата и час на изготвяне на справката"
    release_field = "Данните са актуални към"

    release_date = list(df[df[release_field].notna()][release_field].values)[0]
    generation_date = list(df[df[generation_field].notna()][generation_field].values)[0]

    del df[generation_field]
    del df[release_field]

    df = df.drop_duplicates()
    df = df.dropna(how='all')
    df.to_parquet('../data/processed/v20230131/ekatte.pq', index=False)
    return [df, generation_date, release_date]


def get_ekatte_bbox(base_shape_path: str) -> List:

    gdf = gpd.read_file(base_shape_path)
    gdf.rename(columns={'EKATTE_1': 'ekatte'}, inplace=True)

    gdf.plot(figsize=(12, 12), facecolor="none", edgecolor='red', lw=0.9)
    plt.savefig('../data/processed/v20230131/srs_ekatte.png')

    gdf_wgs84 = gdf.to_crs("EPSG:4326")
    gdf_wgs84.plot(figsize=(12, 12), facecolor="none", edgecolor='red', lw=0.9)
    plt.savefig('../data/processed/v20230131/wgs84_ekatte.png')

    gdf_wgs84 = pd.concat([gdf_wgs84, gdf_wgs84.bounds], axis=1)
    gdf_wgs84['ext_geometry'] = gdf_wgs84.apply(lambda row: get_bbox_polygon(row), axis=1)

    gdf_wgs84.rename(columns={'geometry': 'srs_geometry', 'ext_geometry': 'geometry'}, inplace=True)

    gdf_wgs84.plot(figsize=(12, 12), facecolor="none", edgecolor='red', lw=0.9)
    plt.savefig('../data/processed/v20230131/wgs84_ekatte_ext.png')

    del gdf_wgs84["srs_geometry"]
    del gdf_wgs84["minx"]
    del gdf_wgs84["miny"]
    del gdf_wgs84["maxx"]
    del gdf_wgs84["maxy"]

    gdf_wgs84.to_feather("../data/processed/v20230131/ekatte_geo.feather")
    return []


if __name__ == "__main__":

    Path('/mapsapps/projects/bg-ekatte-lib/data/processed').mkdir(parents=True, exist_ok=True)
    Path('/mapsapps/projects/bg-ekatte-lib/data/processed/v20230131/').mkdir(parents=True, exist_ok=True)


    BASE_PATH = "/mapsapps/projects/bg-ekatte-lib/data/source_data/v_202212_202301/Ekatte_json/"
    df_ekatte = get_ekatte_df(base_path=BASE_PATH)

    BG_ZEMS = '/mapsdata/sources/ekatte_shapefile/ekatte.shp'
    df_ekatte_geom = get_ekatte_bbox(base_shape_path=BG_ZEMS)


