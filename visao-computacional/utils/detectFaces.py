import boto3

def detectFaces(image_file):
    rekognition = boto3.client('rekognition')
    with open(image_file, 'rb') as f:
        response = rekognition.detect_faces(
            Image={
                'Bytes': f.read()
            },
            Attributes=['ALL']
        )
    faces = response['FaceDetails']
    return faces
