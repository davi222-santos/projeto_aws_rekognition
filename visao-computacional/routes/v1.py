import json
import boto3
from utils.getCreationDate import getCreationDate
from utils.loadVariables import loadVariables
from utils.loadImageS3 import loadImageS3
from utils.detectLabels import detectLabels

cloudwatch = boto3.client('logs')

def v1Vision(event, context):
    try:
        # Carregando as variáveis
        bucket, imageName, imageUrl = loadVariables(event)
        
        # Carregando imagem do s3
        file_path = loadImageS3(bucket, imageName)

        # Informando a data que a imagem foi enviada ao S3
        timestamp = getCreationDate(bucket, imageName)

        # Chamando labels do Rekognition
        labels = detectLabels('/tmp/' + imageName)
        
        # Log do CloudWatch
        log_data = {
            "url_to_image": imageUrl,
            "created_image": timestamp,
            "labels": labels
        }
        print(json.dumps(log_data))
        
        response_data = {
            "url_to_image": imageUrl,
            "created_image": timestamp,
            "labels": [
                {"Name": label["Name"], "Confidence": label["Confidence"]} for label in labels
            ]
        }

        response = {
            "statusCode": 200,
            "body": json.dumps(response_data),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
    except Exception as e:
        response = {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
    return response
