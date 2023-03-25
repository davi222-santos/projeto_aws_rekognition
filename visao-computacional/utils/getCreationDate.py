import boto3
from datetime import datetime

# Fornece a data e o horário da imagem no bucket
def getCreationDate(bucket_name, object_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    creation_date = response['LastModified']
    return creation_date.strftime('%d-%m-%Y %H:%M:%S')