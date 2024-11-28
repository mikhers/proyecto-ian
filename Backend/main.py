from fastapi import FastAPI, File, UploadFile
import os
import io


from notebook.refactor import procesar_archivos
from notebook.funciones import procesar_imagen, procesar_video, guardar_frame
from fastapi.responses import StreamingResponse
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI"}

# Define la ruta para procesar la carga de archivos
@app.post("/upload/")
async def procesar_archivos(imagen: UploadFile = File(...), video: UploadFile = File(...)):
    # Guardar los archivos subidos
    imagen_path = f"uploads/{imagen.filename}"
    video_path = f"uploads/{video.filename}"

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    with open(imagen_path, "wb") as img_file:
        img_file.write(await imagen.read())

    with open(video_path, "wb") as vid_file:
        vid_file.write(await video.read())

    # Procesar la imagen
    resultado_imagen = procesar_imagen(imagen_path)
    imagen_procesada_path = resultado_imagen["imagen_procesada"]

    # Procesar el video
    resultado_video = procesar_video(video_path)
    if resultado_video["detecciones"]:
        frame_path = guardar_frame(video_path, resultado_video["detecciones"][0]["frame"])
    else:
        frame_path = None

    # Construir la respuesta con todos los detalles
    detalles_imagen = {
        "numero_caras_detectadas": len(resultado_imagen["resultados"]),
        "ubicaciones_caras": [resultado["ubicacion"] for resultado in resultado_imagen["resultados"]],
        "imagen_procesada_path": imagen_procesada_path
    }

    if resultado_video["detecciones"]:
        detalles_video = {
            "numero_caras_detectadas": len(resultado_video["detecciones"]),
            "detalles_detecciones": resultado_video["detecciones"],
            "frame_guardado_path": frame_path
        }
    else:
        detalles_video = {
            "numero_caras_detectadas": 0,
            "detalles_detecciones": [],
            "frame_guardado_path": None
        }

    return {
        "mensaje": "Archivos procesados con éxito",
        "imagen": detalles_imagen,
        "video": detalles_video
    }

@app.get("/imagen/")
def get_imagen():
    frame_path = "resultado_imagen.jpg"
    if os.path.exists(frame_path):
        return StreamingResponse(open(frame_path, "rb"), media_type="image/jpeg")
    return {"error": "Archivo no encontrado"}

@app.get("/video_frame/")
def get_video_frame():
    frame_path = "frame_detectado.jpg"
    if os.path.exists(frame_path):
        return StreamingResponse(open(frame_path, "rb"), media_type="image/jpeg")
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
)