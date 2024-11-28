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

    responses = {}
    
    # Crear la respuesta para la imagen procesada
    with open(imagen_procesada_path, "rb") as img_file:
        responses["imagen"] = StreamingResponse(io.BytesIO(img_file.read()), media_type="image/jpeg")

    # Crear la respuesta para el primer frame detectado del video (si existe)
    if frame_path:
        with open(frame_path, "rb") as frame_file:
            responses["frame"] = StreamingResponse(io.BytesIO(frame_file.read()), media_type="image/jpeg")

    return responses

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