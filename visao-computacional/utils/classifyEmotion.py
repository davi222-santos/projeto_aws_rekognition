def classifyEmotion(face_details):
    emotions = face_details['Emotions']
    emotion_confidence = {}

    for emotion in emotions:
        emotion_type = emotion['Type']
        emotion_confidence[emotion_type] = emotion['Confidence']
    classified_emotion = max(emotion_confidence, key=emotion_confidence.get)
    classified_emotion_confidence = emotion_confidence[classified_emotion]

    return classified_emotion, classified_emotion_confidence