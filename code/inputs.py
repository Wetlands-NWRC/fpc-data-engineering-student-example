import os

from typing import Dict, List

import ee
import geopandas as gpd

from ee import ImageCollection



class S1Collection:

    ASSET_ID = ""

    def __new__(cls, *args, **kwargs):
        instance: ImageCollection = ee.ImageCollection(cls.ASSET_ID)
        return instance


def filter_sentinel_1(dates: List[str], viewport: ee.Geometry, rel_obit: int) -> Dict[str, S1Collection]:
    return {date: S1Collection().filter(f'relativeOrbitNumber_start == {rel_obit}').filterBounds(viewport)\
        .filterDate(*date) for date in dates}


def load_training_data(filename: str, driver: str = None, layer: str = None) -> ee.FeatureCollection:
    driver = 'ESRI Shapefile' if driver is None else driver
    suffix = os.path.splitext(filename)

    if suffix in ['.geojson', '.shp']:
        pass


