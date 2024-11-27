import face_recognition
import cv2
import numpy as np
from skimage import io
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt


def procesar_imagen(image_path):
    # Procesamiento de la imagen
    print("Comenzó el procesamiento de imagen")
    imagen = face_recognition.load_image_file(image_path)
    print("#1")
    face_locations = face_recognition.face_locations(imagen, model="cnn")
    print("#2")
    face_encodings = face_recognition.face_encodings(imagen, face_locations)
    print("#3")

    resultados = []
    pil_image = Image.fromarray(imagen)
    print("#4")
    draw = ImageDraw.Draw(pil_image)
    print("#5")

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
        text_width, text_height = draw.textsize("Cara detectada")
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
        draw.text((left + 2, bottom - text_height - 5), "Cara detectada", fill=(255, 255, 255, 255))

        resultados.append({
            "ubicacion": (top, right, bottom, left),
            "mensaje": "Cara detectada"
        })
    print("#6")

    # Guardar la imagen con rectángulos para enviar como resultado
    pil_image.save("resultado_imagen.jpg")

    print("#7")
    return {
        "resultados": resultados,
        "imagen_procesada": "resultado_imagen.jpg"
    }


def procesar_video(video_path):
    # Procesamiento del video
    print("Comenzó el procesamiento de video")
    video = cv2.VideoCapture(video_path)
    print("#8")
    fps = video.get(cv2.CAP_PROP_FPS)
    intervalo_segundos = 5
    intervalo_muestras = int(fps * intervalo_segundos)
    frame_inicial = 0

    detecciones = []
    print("#9")
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        if frame_inicial % intervalo_muestras == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(frame_rgb, model="cnn")
            for (top, right, bottom, left) in face_locations:
                detecciones.append({
                    "frame": frame_inicial,
                    "ubicacion": (top, right, bottom, left)
                })

        frame_inicial += 1

    print("#10")
    video.release()
    return {"detecciones": detecciones}
