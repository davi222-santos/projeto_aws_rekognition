import boto3

# Carrega a imagem do S3
def loadImageS3(bucket, imageName):
    s3 = boto3.resource('s3')
    file_path = f'/tmp/{imageName}'
    s3.Bucket(bucket).download_file(imageName, file_path)
    return file_path
