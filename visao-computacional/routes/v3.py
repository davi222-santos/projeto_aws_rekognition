import json
import boto3
from utils.getCreationDate import getCreationDate
from utils.classifyEmotion import classifyEmotion
from utils.loadVariables import loadVariables
from utils.loadImageS3 import loadImageS3
from utils.detectFaces import detectFaces

rekognition = boto3.client('rekognition')
cloudwatch = boto3.client('logs')

def v3Vision(event, context):
    try:
        # Carregando as variáveis
        bucket, imageName, imageUrl = loadVariables(event)

        # Carregando imagem do s3
        file_path = loadImageS3(bucket, imageName)

        timestamp = getCreationDate(bucket, imageName)

        faces_response = detectFaces(file_path)

        log_data = {
            "url_to_image": imageUrl,
            "created_image": timestamp,
            "response": faces_response
        }

        response_data = {
            'url_to_image': imageUrl,
            'created_image': timestamp,
            'faces': []
        }

        # Armazena a emoção e a confiança no response_data
        if len(faces_response) == 0:
            response_data['faces'].append({
                'position': {
                    'Height': None,
                    'Left': None,
                    'Top': None,
                    'Width': None
                },
                'classified_emotion': None,
                'classified_emotion_confidence': None
            })
        elif len(faces_response) == 1:
            face_details = faces_response[0]
            classified_emotion, classified_emotion_confidence = classifyEmotion(face_details)
            position = face_details['BoundingBox']
            response_data['faces'].append({
                'position': {
                    'Height': position['Height'],
                    'Left': position['Left'],
                    'Top': position['Top'],
                    'Width': position['Width']
                },
                'classified_emotion': classified_emotion,
                'classified_emotion_confidence': classified_emotion_confidence
            })
        else:
            # Cria um array de objetos para cada face, caso exista mais de uma
            for face_details in faces_response:
                classified_emotion, classified_emotion_confidence = classifyEmotion(face_details)
                position = face_details['BoundingBox']
                response_data['faces'].append({
                    'position': {
                        'Height': position['Height'],
                        'Left': position['Left'],
                        'Top': position['Top'],
                        'Width': position['Width']
                    },
                    'classified_emotion': classified_emotion,
                    'classified_emotion_confidence': classified_emotion_confidence
                })

        print(json.dumps(log_data))

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
            "body": json.dumps({"error": str(e)}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
    return response
