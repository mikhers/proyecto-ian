import os
import io
import asyncio
from fastapi import FastAPI, File, UploadFile
from concurrent.futures import ThreadPoolExecutor
from notebook.refactor import procesar_archivos
from notebook.funciones import procesar_imagen, procesar_video, guardar_frame
from fastapi.responses import StreamingResponse
from fastapi import Request
app = FastAPI()
executor = ThreadPoolExecutor()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI"}

# Define la ruta para procesar la carga de archivos
@app.post("/upload/")
async def procesar_archivos(imagen: UploadFile = File(...), video: UploadFile = File(...)):
    # Eliminar archivos previos
    if os.path.exists("resultado_imagen.jpg"):
        os.remove("resultado_imagen.jpg")
    if os.path.exists("frame_detectado.jpg"):
        os.remove("frame_detectado.jpg")

    # Guardar los archivos subidos
    imagen_path = f"uploads/{imagen.filename}"
    video_path = f"uploads/{video.filename}"

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    with open(imagen_path, "wb") as img_file:
        img_file.write(await imagen.read())

    with open(video_path, "wb") as vid_file:
        vid_file.write(await video.read())

    # Procesar la imagen y el video en paralelo usando asyncio
    loop = asyncio.get_event_loop()

    procesar_imagen_task = loop.run_in_executor(executor, procesar_imagen, imagen_path)
    procesar_video_task = loop.run_in_executor(executor, procesar_video, video_path)

    # Esperar a que ambas tareas terminen
    resultado_imagen, resultado_video = await asyncio.gather(procesar_imagen_task, procesar_video_task)

    imagen_procesada_path = resultado_imagen["imagen_procesada"]

    # Procesar el frame del video (si hay detecciones)
    if resultado_video["detecciones"]:
        frame_path_task = loop.run_in_executor(executor, guardar_frame, video_path, resultado_video["detecciones"][0]["frame"])
        frame_path = await frame_path_task
    else:
        frame_path = None

    # Responder con todos los detalles una vez que ambos procesos hayan terminado
    return {
        "mensaje": "Archivos procesados con éxito",
        "imagen": {
            "numero_caras_detectadas": len(resultado_imagen["resultados"]),
            "ubicaciones_caras": [resultado["ubicacion"] for resultado in resultado_imagen["resultados"]],
            "imagen_procesada_path": imagen_procesada_path
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