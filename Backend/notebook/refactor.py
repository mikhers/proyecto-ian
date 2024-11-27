import os

# Importamos las librerías necesarias para el procesamiento
import face_recognition
import urllib.request
import bz2
import cv2


def procesar_archivos(image_path, video_path):
    # Aquí irá tu código de procesamiento adaptado
    # Cargamos la imagen y el video desde los paths proporcionados

    # Cargar el modelo CNN si es necesario
    if not os.path.exists("mmod_human_face_detector.dat"):
        cnn_model_url = "http://dlib.net/files/mmod_human_face_detector.dat.bz2"
        archive_path  = "mmod_human_face_detector.dat.bz2"
        urllib.request.urlretrieve(cnn_model_url, archive_path)
        with bz2.BZ2File(archive_path, "rb") as file, open("mmod_human_face_detector.dat", "wb") as out_file:
            out_file.write(file.read())

    # Cargar imagen objetivo y extraer encoding
    imagen_objetivo = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(imagen_objetivo)
    if not face_encodings:
        return "No se detectaron rostros en la imagen de entrenamiento."
    target_face_encoding = face_encodings[0]
    target_name = "Persona Objetivo"

    # Procesar el video
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    intervalo_segundos = 5  # Cambia esto si deseas otro intervalo
    intervalo_muestras = int(fps * intervalo_segundos)
    frame_inicial = 0
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    detecciones = []

    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        if frame_inicial >= total_frames:
            break
        if frame_inicial % intervalo_muestras == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(frame_rgb, model="cnn")
            face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                coincidencias = face_recognition.compare_faces([target_face_encoding], face_encoding)
                if True in coincidencias:
                    tiempo_segundos = frame_inicial / fps
                    minutos = int(tiempo_segundos // 60)
                    segundos = int(tiempo_segundos % 60)
                    deteccion = f"Detectado en el minuto {minutos}:{segundos:02d}"
                    detecciones.append(deteccion)
                    # Opcional: guardar el frame donde se detectó el rostro
                    # frame_output_path = f"output/deteccion_{minutos}_{segundos}.jpg"
                    # cv2.imwrite(frame_output_path, cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR))
        frame_inicial += 1
    video.release()

    if detecciones:
        return {"detecciones": detecciones}
    else:
        return "No se detectó a la persona objetivo en el video."
