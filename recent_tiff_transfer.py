import os
import io
from datetime import datetime
from dateutil.relativedelta import relativedelta

from google.cloud import storage
import logging
import rasterio


def scale_geotiff(request):
    """Cloud Function to scale a GeoTIFF in Cloud Storage and log events.
    Inputs: 
    request: None
    
    """

    # Set up logger
    logger = logging.getLogger('scale_geotiff')
    logger.setLevel(logging.INFO)

    # Bucket and scale factor
    bucket_name_1 = 'wwdt'
    bucket_name_2 = 'wwdt-recent-month'
    scale_factor = 1.8

    # Get date info
    last_month = datetime.now() - relativedelta(months=1)
    year = last_month.year
    month = last_month.month
    scheme_text = f'{year}_{month:02d}.tif'
   

    # Set up storage client
    storage_client = storage.Client(project='dri-wwdt')
    bucket_1 = storage_client.bucket(bucket_name_1)
    bucket_2 = storage_client.bucket(bucket_name_2)

    # Get list of blobs currently in bucket 2
    blobs_2 = storage_client.list_blobs(bucket_name_2)
    file_list_2 = [blob.name for blob in blobs_2 if scheme_text in blob.name]
    
    # Get month day for 
    if len(file_list_2) == 89:
        # bucket already has been processed
        return 'Success!'
    else:
        # Bcuket has old data in it
        clear_bucket('wwdt-recent-month')     

    # Continue to process data
    blobs_1 = storage_client.list_blobs(bucket_name_1)
    file_list = [blob.name for blob in blobs_1 if scheme_text in blob.name]
    
    # Move revent files to new bucket
    for file_name in file_list:
        print(file_name)
    
        # Read oiginal file blob
        blob_1 = bucket_1.blob(file_name)

        # Write source blob to new bucket as copy
        bucket_1.copy_blob(blob_1, bucket_2, file_name)
    
    return 'Success!'


def clear_bucket(bgt_nm):
    # Initialize a Cloud Storage client
    client = storage.Client()
    bucket = client.get_bucket(bgt_nm)

    # List and delete all files in the bucket
    blobs_bgt = bucket.list_blobs()
    for blob_bgt in blobs_bgt:
        blob_bgt.delete()
        # print(f"Deleted {blob.name}")
