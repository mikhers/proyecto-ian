from fastapi import FastAPI, File, UploadFile
import os

from notebook.refactor import procesar_archivos
from notebook.funciones import procesar_imagen, procesar_video
app = FastAPI()

# Define la ruta para procesar la carga de archivos
@app.post("/upload/")
async def procesar_archivos(image: UploadFile = File(...), video: UploadFile = File(...)):
    # Guardar los archivos subidos
    imagen_path = f"uploads/{image.filename}"
    video_path = f"uploads/{video.filename}"

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    with open(imagen_path, "wb") as img_file:
        img_file.write(await image.read())

    with open(video_path, "wb") as vid_file:
        vid_file.write(await video.read())

    # Procesar la imagen y el video
    resultado_imagen = procesar_imagen(imagen_path)
    print("procesar_imagen(imagen_path)")
    print(resultado_imagen)
    resultado_video = procesar_video(video_path)
    print("procesar_video(video_path)")
    print(resultado_video)

    return {
        "mensaje": "Archivos procesados con éxito",
        "imagen_resultado": resultado_imagen,
        "video_resultado": resultado_video
    }

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