# Avaliação Sprint 8 - Programa de Bolsas Compass UOL / AWS e IFCE

[![N|Solid](https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/LogoCompasso-positivo.png/440px-LogoCompasso-positivo.png)](https://compass.uol/pt/home/)

Avaliação da oitava sprint do programa de bolsas Compass UOL para formação em machine learning para AWS.

---

## Sumário
- [Objetivo](#objetivo)
- [Ferramentas](#ferramentas)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Desenvolvimento](#desenvolvimento)
    - [Rotas](#rotas)
    - [Funções](#funções)
- [Resultado](#resultado)
- [Impedimentos](#impedimentos)
- [Conclusão](#conclusão)
- [Equipe](#equipe)

---

## Objetivo

Este projeto tem como objetivo demonstrar a utilização do serviço de reconhecimento de imagens da AWS, o Amazon Rekognition, através de rotas de API Gateway em uma aplicação serverless na AWS Lambda. Além disso, também utilizaremos o CloudWatch para gravar os logs dos resultados obtidos na análise das imagens. As rotas disponíveis são responsáveis por extrair tags das imagens armazenadas no S3 através do Rekognition e retornar essas informações em formato JSON para a aplicação cliente. As funções Lambda implementadas serão acionadas pela API Gateway, que será responsável por direcionar as requisições HTTP para as funções Lambda apropriadas.

## Ferramentas

* [AWS](https://aws.amazon.com/pt/) plataforma de computação em nuvem da Amazon.
  * [S3](https://aws.amazon.com/s3/) serviço de armazenamento.
  * [API Gateway](https://aws.amazon.com/api-gateway/) serviço para criação, implantação e gerenciamento de APIs.
  * [Lambda](https://aws.amazon.com/lambda/) serviço de computação *serverless* que permite a execução de código sem a preocupação de gerenciar servidores.
  * [Rekognition](https://aws.amazon.com/rekognition/) realiza o reconhecimento de imagens e vídeos por meio do aprendizado de máquina.

## Estrutura do projeto
```
visao-computacional/
│└──handler.py
│└──serverless.yml
├── routes/
│   └── homepage.py
│   └── v1.py
│   └── v2.py
│   └── v3.py
├── utils/
│   └── classifyEmotion.py
│   └── detectFaces.py
│   └── detectLabels.py
│   └── getCreationDate.py
│   └── loadImageS3.py
│   └── loadVariables.py
├── templates/
│   └── index.html
```
A organização do código foi definida por meio da divisão de pastas com responsabilidades específicas para facilitar a localização e manutenção das funcionalidades.
> **routes** possui as rotas juntamente com o encaminhamento para a página de acesso as mesmas na web.

> **utils** contém as funções que permitiram a modularização das rotas.

> **templates** frontend da aplicação.

## Desenvolvimento

### Rotas

### /v1/vision:

Essa rota tem como objetivo receber uma imagem armazenada em um bucket S3 e extrair suas tags por meio do serviço Rekognition da AWS. Além disso, ela também faz uso do serviço de log do CloudWatch para gravar as informações da imagem processada e as tags identificadas.

O trecho de código em questão registra as informações de log no CloudWatch, contendo a URL da imagem, o horário de criação e as tags extraídas do Amazon Rekognition pela função [detectLabels](#detectlabels). Em seguida, a função retorna um objeto JSON com as mesmas informações das tags, mas em um formato mais legível para o usuário.
```py
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
```
### /v2/vision:

Essa rota utiliza o serviço de detecção de labels do Amazon Rekognition para identificar as faces presentes na imagem, retornando uma lista com as faces detectadas.

Nesse trecho, a função [detectFaces](#detectfaces) é chamada para detectar as faces na imagem. O resultado da detecção é registrado em um objeto de log que é impresso no console. Em seguida, é verificado se alguma face foi detectada e, se houver, a posição de cada face é registrada em um array. Essas informações são então retornadas como parte da resposta da API.
```py
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
```
### /v3/vision:

A função dessa rota é retornar a posição das faces assim como a emoção principal que as mesmas possuem para registrar as informações no CloudWatch. Tal requisito foi especificado pela quantidade de rostos identificados, sendo utilizado a função [detectFaces](#detectfaces).

Quando nenhuma face é identificada, *none* é retornado nos parâmetros.
```py
faces_response = detectFaces(file_path)

if len(faces_response) == 0:
    response_data['faces'].append({
        'position': {'Height': None, 'Left': None, 'Top': None, 'Width': None},
        'classified_emotion': None,
        'classified_emotion_confidence': None
    })
```

Para somente uma face a saída retorna os campos especificados acima com seus devidos valores e utiliza da função [classifyEmotion](#classifyemotion) para retornar a emoção principal e a taxa de confiança dela.
```py
elif len(faces_response) == 1:
    face_details = faces_response[0]
    classified_emotion, classified_emotion_confidence = classifyEmotion(face_details)
    position = face_details['BoundingBox']
    response_data['faces'].append({...})
```

Já para os casos com mais de um rosto detectado foi criado um laço para percorrer os objetos de cada face e retornar os campos citados.
```py
else:
    for face_details in faces_response:
        classified_emotion, classified_emotion_confidence = classifyEmotion(face_details)
        position = face_details['BoundingBox']
        response_data['faces'].append({...})
```

### Funções

- ### loadVariables 
    Essa função usa a biblioteca **json** para analisar o corpo do objeto de evento e extrair as variáveis ​​*bucket* e *imageName*. A função também cria uma URL da imagem com essas variáveis e as ​retorna.

- ### loadImageS3
    Essa função usa a biblioteca **boto3** para baixar uma imagem de um bucket S3 e salvá-la. Retornando o caminho do arquivo onde a foto foi salva.

- ### getCreationDate
    Função que retorna a data e hora que um objeto foi enviado para um bucket do Amazon S3.

- ### detectLabels
    Chama o serviço Rekognition da AWS para reconhecer as características da imagem passadas como parâmetro. Em seguida, retorna uma lista com as labels identificadas, sendo no máximo 10 e com uma confiança mínima de 75%.

- ### detectFaces:
    Acessa o serviço Amazon Rekognition e detecta as faces em uma imagem passada como parâmetro. A imagem é lida em bytes e passada para o método *detect_faces*, que retorna detalhes das faces encontradas. Esses detalhes são armazenados em uma variável e retornados pela função.

- ### classifyEmotion:
    Recebe detalhes da face de uma imagem e classifica a emoção predominante e sua confiança. Ela percorre a lista de emoções e armazena a confiança de cada emoção em um dicionário. Em seguida, retorna a emoção com a maior confiança.

## Resultado
Para utilizar os recursos das rotas acesse este [link](https://n3bay1s6wi.execute-api.us-east-1.amazonaws.com/home). Para testar, basta colocar o nome do seu próprio bucket, ou inserir o nome do mesmo como "photos-sprint8-davi" e o nome da imagem como "gato.jpg" ou "homem.jpg", pois é um bucket para teste público de um dos integrantes da equipe.

Lembrando que o link somente será habilitado para uso no dia da avaliação ou após contatar a equipe.

## Impedimentos
- Inserir uma imagem no bucket especificado por meio da página html.

## Conclusão
A conclusão desta avaliação é extremamente positiva. O desenvolvimento deste projeto nos permitiu aprimorar nossos conhecimentos em serverless, bem como nos recursos da AWS. Além disso, foi proveitoso o trabalho em equipe, o que nos permitiu trocar experiências e ideias para solucionar desafios e aprender uns com os outros.

Ao finalizar este projeto, foi visível a evolução de cada membro da equipe em relação a avaliação passada sobre o mesmo assunto, demonstrando que estamos constantemente em busca de evolução e aprimoramento em nossas habilidades e conhecimentos.

## Equipe

- [Davi](https://github.com/davi222-santos)
- [Dayanne](https://github.com/dayannebugarim)
- [Josiana](https://github.com/JosianaSilva)
- [Rafael](https://github.com/Kurokishin)

