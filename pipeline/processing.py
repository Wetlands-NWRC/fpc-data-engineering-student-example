from typing import List

import ee

from inputs import Sentinel1


def batch_generate_samples(data: Sentinel1):

   for image in data.images:
        date = image.date().format('YYYY-MM-dd')

        sample = image.sampleRegions(**{
            'collection': data.training_data,
            'tileScale': 16,
            'scale': 10
        })\
            .set('date', date)
        data.samples.append(sample)
   return data


def batch_despckle(data: Sentinel1, filter_size: int = 1) -> None:
    if filter_size > 3 or filter_size < 1:
        raise Exception("Filter Size is to Large: needs to be between 1 and 3")

    boxcar = ee.Kernel.square(filter_size)
    for idx, image in enumerate(data.images):
        data.images[idx] = image.convolve(boxcar).set('despkle', 'BoxCar')
    return None


def batch_register(data: Sentinel1) -> None:
    ref = data.images.pop(0).set('register', 'reference')

    tool_cfg = {
        'referenceImage': ref,
        'maxOffset': 1
    }

    for idx, image in enumerate(data.images):
        data.images[idx] = image.register(**tool_cfg).set('register', 'target')
    data.images.insert(0, ref)
    return None
