import os
from typing import List

import ee

from inputs import Sentinel1


def table_cloud_task(data: Sentinel1, bucket: str = None):
    tasks = []
    bucket = os.environ.get('BUCKET') if bucket is None else bucket
    file_name_prefix = '{year}/training_data/{table_name}'
    for idx, table in enumerate(data.samples, start= 1):
        name = f'training_data_{idx}_of_{len(data.samples)}_{data.year}'
        file_name_prefix.format(table_name=name, year=data.year)

        task = ee.batch.Export.table.toCloudStorage(
            collection=table,
            description=name,
            fileNamePrefix=file_name_prefix,
            fileFormat='GeoJSON',
            bucket=bucket,
        )
        tasks.append(task)
    return tasks


def image_cloud_task(data: Sentinel1, bucket: str = None) -> List[ee.batch.Task]:
    tasks = []
    bucket = os.environ.get('BUCKET') if bucket is None else bucket
    for image in data.images:
        export_name = image.get('export_name').getInfo()
        file_name_prefix = f'{data.year}/img/{export_name}/{export_name}'
        data.viewport = data.training_data.geometry().bounds() if data.viewport is None else data.viewport
        task = ee.batch.Export.image.toCloudStorage(
            image=image,
            description=export_name,
            bucket=bucket,
            scale=10,
            crs='EPSG:4326',
            maxPixels=1e13,
            region=data.viewport,
            shardSize=64,
            fileDimensions=[64, 64]
        )
        tasks.append(task)
    return tasks


def export_tasks(tasks: List[ee.batch.Task]) -> None:
    [ _.start() for _ in tasks]
    return None