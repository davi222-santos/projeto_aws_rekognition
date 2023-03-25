import json

# Carrega as variáveis usadas nas rotas
def loadVariables(event):
    body = json.loads(event['body'])
    bucket = body['bucket']
    imageName = body['imageName']
    imageUrl = f"https://{bucket}.s3.amazonaws.com/{imageName}"
    
    return bucket, imageName, imageUrl