import boto3

# Reconhece as labels da imagem
def detectLabels(image_file):
    rekognition = boto3.client('rekognition')
    with open(image_file, 'rb') as f:
        response = rekognition.detect_labels(
            Image={
                'Bytes': f.read()
            },
            MaxLabels=10,
            MinConfidence=75
        )
    labels = response['Labels']
    return labels
