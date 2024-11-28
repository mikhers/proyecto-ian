import os
import io
import asyncio
from fastapi import FastAPI, File, UploadFile
from concurrent.futures import ThreadPoolExecutor
from notebook.refactor import procesar_archivos
from notebook.funciones import procesar_imagen, procesar_video, guardar_frame
from fastapi.responses import StreamingResponse
from fastapi import Request
import numpy as np


app = FastAPI()
executor = ThreadPoolExecutor()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI"}

# Define la ruta para procesar la carga de archivos
@app.post("/upload/")
async def procesar_archivos(imagen: UploadFile = File(...), video: UploadFile = File(...)):
    # Eliminar archivos previos
    for file_name in ["resultado_imagen.jpg", "frame_detectado.jpg"]:
        if os.path.exists(file_name):
            os.remove(file_name)

    # Guardar archivos subidos
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    imagen_path = f"uploads/{imagen.filename}"
    video_path = f"uploads/{video.filename}"
    with open(imagen_path, "wb") as img_file:
        img_file.write(await imagen.read())
    with open(video_path, "wb") as vid_file:
        vid_file.write(await video.read())

    # Procesar la imagen primero
    resultado_imagen = await asyncio.to_thread(procesar_imagen, imagen_path)

    # Obtener los encodings de la imagen
    face_encodings_imagen = [np.array(res["encoding"]) for res in resultado_imagen["resultados"]]

    # Procesar el video con los encodings de la imagen
    resultado_video = await asyncio.to_thread(procesar_video, video_path, face_encodings_imagen)

    # Guardar el frame detectado si hay detecciones
    if resultado_video["detecciones"]:
        deteccion = resultado_video["detecciones"][0]
        target_name = os.path.splitext(os.path.basename(imagen_path))[0]
        frame_path = await asyncio.to_thread(guardar_frame, video_path, deteccion["frame"], deteccion, target_name)
    else:
        frame_path = None

    return {
        "mensaje": "Archivos procesados con éxito",
        "imagen": {
            "numero_caras_detectadas": len(resultado_imagen["resultados"]),
            "ubicaciones_caras": [res["ubicacion"] for res in resultado_imagen["resultados"]],
            "imagen_procesada_path": resultado_imagen["imagen_procesada"]
        },
        "video": {
            "numero_caras_detectadas": len(resultado_video["detecciones"]),
            "detalles_detecciones": resultado_video["detecciones"],
            "frame_guardado_path": frame_path
        }
    }

@app.get("/imagen/")
def get_imagen(request: Request):
    frame_path = "resultado_imagen.jpg"
    if os.path.exists(frame_path):
        headers = {
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache"
        }
        return StreamingResponse(open(frame_path, "rb"), media_type="image/jpeg", headers=headers)
    return {"error": "Archivo no encontrado"}

@app.get("/video_frame/")
def get_video_frame(request: Request):
    frame_path = "frame_detectado.jpg"
    if os.path.exists(frame_path):
        headers = {
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache"
        }
        return StreamingResponse(open(frame_path, "rb"), media_type="image/jpeg", headers=headers)
    return {"error": "Frame no encontrado"}

# Crea una carpeta para guardar archivos
if not os.path.exists("uploads"):
    os.makedirs("uploads")


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Cache-Control", "Pragma"],
)