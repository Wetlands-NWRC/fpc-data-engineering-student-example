import os
import re
from dataclasses import  dataclass, field, InitVar

from typing import Dict, List, Tuple, Union

import ee
import geopandas as gpd

from ee import ImageCollection


@dataclass
class Sentinel1:
    year: int
    training_data: ee.FeatureCollection
    viewport: ee.Geometry = field(init=False, default=None)
    images: List[ee.Image] = field(init=False, default_factory=lambda: [])
    samples: List[ee.FeatureCollection] = field(init=False, default_factory=lambda: [])


@dataclass()
class Config:
    years: InitVar[List[Union[str, int]]]
    start_mmdd: InitVar[str]
    end_mmdd: InitVar[str]
    relative_orbit: int
    assetid: str = field(default=None)
    filename: str = field(default=None)
    driver: str = field(default='ESRI Shapefile')
    layer: str = field(default=None)

    def __post_init__(self,years, start_mmdd, end_mmdd):
        self.dates = [(f'{year}-{start_mmdd}', f'{year}-{end_mmdd}') for year in years]


class S1Collection:

    ASSET_ID = "COPERNICUS/S1_GRD"

    def __new__(cls, *args, **kwargs):
        instance: ImageCollection = ee.ImageCollection(cls.ASSET_ID)
        return instance


def add_export_name(element: ee.Image):
    date = element.date().format('_YYYYMMdd_')
    mission = ee.String('S1')
    mode = ee.String('IW')
    name = mission.cat(date).cat(mode)
    return element.set('export_name', name)


def parse_sentinel_1(date: Tuple[str], viewport: ee.Geometry, rel_obit: int, dataobj: Sentinel1) -> None:
    col = S1Collection().filter(f'relativeOrbitNumber_start == {rel_obit}').filterBounds(viewport).filterDate(*date)
    sysids: List[str] = col.toList(col.size()).map(lambda x: ee.Image(x).get('system:index')).getInfo()
    for sysid in sysids:
        dataobj.images.append(add_export_name(ee.Image(f'{S1Collection.ASSET_ID}/{sysid}')))
    return None


def add_xy(element: ee.Feature) -> ee.Feature:
    coords: ee.List = element.geometry().coordinates()
    x,y = coords.get(0), coords.get(1)
    return element.set('x', x, 'y', y)


def load_training_data_from_file(filename: str, driver: str = None, layer: str = None) -> ee.FeatureCollection:
    driver = 'ESRI Shapefile' if driver is None else driver
    gdf = gpd.read_file(filename=filename, driver=driver, layer=layer)
    return ee.FeatureCollection(gdf.__geo_interface__).map(add_xy)


def loat_trianing_data_from_asset(assetid: str):
    return ee.FeatureCollection(assetid).map(add_xy)


def setup_inputs(cfg: Config) -> List[Sentinel1]:
    if cfg.assetid is not None:
        training_data = loat_trianing_data_from_asset(cfg.assetid)
    elif cfg.filename is not None:
        training_data = load_training_data_from_file(
            filename=cfg.filename,
            layer=cfg.layer,
            driver=cfg.driver
        )
    else:
        raise Exception("You need to spcify Asset id or File Name")

    search_geom = training_data.geometry()

    datas = []
    for date in cfg.dates:
        year = int(date[0].split("-")[0])
        data = Sentinel1(
            year=year,
            training_data=training_data
        )
        parse_sentinel_1(
            date=date,
            viewport=search_geom,
            rel_obit=cfg.relative_orbit,
            dataobj=data
        )

        datas.append(data)
    return datas

