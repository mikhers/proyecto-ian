import face_recognition
import cv2
import numpy as np
from skimage import io
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt


def procesar_imagen(image_path):
    # Cargar la imagen usando face_recognition
    imagen = face_recognition.load_image_file(image_path)

    # Detectar ubicaciones de caras
    face_locations = face_recognition.face_locations(imagen, model="cnn")

    # Crear una copia procesada de la imagen para guardar resultados
    pil_image = Image.fromarray(imagen)
    draw = ImageDraw.Draw(pil_image)

    resultados = []
    for (top, right, bottom, left) in face_locations:
        # Dibujar rectángulos alrededor de las caras detectadas
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

        # Guardar la ubicación de la cara detectada
        resultados.append({
            "ubicacion": (top, right, bottom, left),
            "mensaje": "Cara detectada"
        })

    # Guardar la imagen procesada con rectángulos
    imagen_procesada_path = "resultado_imagen.jpg"
    pil_image.save(imagen_procesada_path)

    # Devolver detalles del análisis
    return {
        "resultados": resultados,
        "numero_caras_detectadas": len(resultados),
        "imagen_procesada": imagen_procesada_path
    }

def procesar_video(video_path):
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    intervalo_segundos = 5
    intervalo_muestras = int(fps * intervalo_segundos)
    frame_inicial = 0

    detecciones = []

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

    video.release()
    return {"detecciones": detecciones}

def guardar_frame(video_path, frame_index):
    video = cv2.VideoCapture(video_path)
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = video.read()
    frame_path = "frame_detectado.jpg"
    if ret:
        cv2.imwrite(frame_path, frame)
    video.release()
    return frame_path