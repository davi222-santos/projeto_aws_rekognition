import json
import boto3
from utils.getCreationDate import getCreationDate
from utils.loadVariables import loadVariables
from utils.loadImageS3 import loadImageS3
from utils.detectFaces import detectFaces

cloudwatch = boto3.client('logs')
rekognition = boto3.client('rekognition')

def v2Vision(event, context):
    try:
        # Carregando as variáveis
        bucket, imageName, imageUrl = loadVariables(event)
        
        # Carregando imagem do s3
        file_path = loadImageS3(bucket, imageName)

        # Informando a data que a imagem foi enviada ao S3
        timestamp = getCreationDate(bucket, imageName)
        
        # Chamando faces do Rekognition
        response = detectFaces(file_path)
        
        log_data = {
            "url_to_image": imageUrl,
            "created_image": timestamp,
            "response": response
        }
        print(json.dumps(log_data))
        
        if response:
            haveFaces = True
            positions = [
                {
                    "Height": details["BoundingBox"]["Height"],
                    "Left": details["BoundingBox"]["Left"],
                    "Top": details["BoundingBox"]["Top"],
                    "Width": details["BoundingBox"]["Width"]
                } for details in response
            ]
        else:
            haveFaces = False
            positions = None

        response_data = {
            "url_to_image": imageUrl,
            "created_image": timestamp,
            "have_faces": haveFaces,
            "position_faces": positions
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
