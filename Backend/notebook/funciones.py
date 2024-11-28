import face_recognition
import cv2
import numpy as np
from skimage import io
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt


def procesar_imagen(image_path):
    # Cargar la imagen y detectar caras
    imagen = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(imagen, model="hog")
    face_encodings = face_recognition.face_encodings(imagen, face_locations)

    # Dibujar rectángulos en la imagen
    pil_image = Image.fromarray(imagen)
    draw = ImageDraw.Draw(pil_image)

    resultados = []
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
        resultados.append({
            "ubicacion": (top, right, bottom, left),
            "encoding": face_encoding.tolist()
        })

    # Guardar imagen procesada
    imagen_procesada_path = "resultado_imagen.jpg"
    pil_image.save(imagen_procesada_path)

    return {
        "resultados": resultados,
        "imagen_procesada": imagen_procesada_path
    }

def procesar_video(video_path, target_face_encodings):
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    intervalo_segundos = 5
    intervalo_muestras = int(fps * intervalo_segundos)
    frame_inicial = 0
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    detecciones = []

    while video.isOpened():
        ret, frame = video.read()
        if not ret or frame_inicial >= total_frames:
            break
        if frame_inicial % intervalo_muestras == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(frame_rgb, model="hog")
            face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                coincidencias = face_recognition.compare_faces(target_face_encodings, face_encoding)
                if True in coincidencias:
                    detecciones.append({
                        "frame": frame_inicial,
                        "ubicacion": (top, right, bottom, left)
                    })
        frame_inicial += 1

    video.release()
    return {"detecciones": detecciones}

def guardar_frame(video_path, frame_index, deteccion, target_name="Persona Detectada"):
    video = cv2.VideoCapture(video_path)
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = video.read()
    frame_path = "frames/frame_detectado.jpg"
    if ret:
        top, right, bottom, left = deteccion["ubicacion"]
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, target_name, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        cv2.imwrite(frame_path, frame)
    video.release()
    return frame_path