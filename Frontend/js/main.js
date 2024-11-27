document.addEventListener("DOMContentLoaded", () => {
    // Inicializar estado oculto
    document.getElementById("loading").classList.add("hidden");
    document.getElementById("result").classList.add("hidden");
});

document.getElementById("upload-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const formContainer = document.getElementById("form-container");
    const loadingDiv = document.getElementById("loading");
    const resultDiv = document.getElementById("result");
    const imageResultDiv = document.getElementById("image-result");
    const videoResultDiv = document.getElementById("video-result");
    const previewImage = document.getElementById("preview-image");

    const formData = new FormData();
    const image = document.getElementById("image").files[0];
    const video = document.getElementById("video").files[0];
    
    console.log({formContainer})
    console.log("loading" + loadingDiv)
    console.log("result" + resultDiv)
    console.log("image" + imageResultDiv)
    console.log("video" + videoResultDiv)
    console.log("preview" + previewImage)
    console.log("image" + image)
    console.log("video" + video)

    if (!image || !video) { 
        alert("Por favor, selecciona una imagen y un video antes de subir.");
        return;
    }

    formData.append("imagen", image);
    formData.append("video", video);

    // Mostrar la imagen cargada en el contenedor de carga
    previewImage.src = URL.createObjectURL(image);
    formContainer.classList.add("hidden");
    loadingDiv.classList.remove("hidden");

    try {
        const response = await fetch("http://127.0.0.1:8000/upload/", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();

        // Ocultar el contenedor de carga y mostrar los resultados
        loadingDiv.classList.add("hidden");

        imageResultDiv.innerHTML = `
            <h3>Imagen Procesada:</h3>
            <p>${result.imagen_resultado.resultados.map(res => `<br>Ubicación: ${res.ubicacion} - Mensaje: ${res.mensaje}`).join('')}</p>
        `;

        videoResultDiv.innerHTML = `
            <h3>Detecciones en Video:</h3>
            ${result.video_resultado.detecciones.map(det => `
                <p>Frame: ${det.frame}, Ubicación: ${det.ubicacion}</p>
            `).join('')}
        `;

        resultDiv.classList.remove("hidden");
    } catch (error) {
        console.error("Error al procesar los archivos:", error);
        loadingDiv.classList.add("hidden");
        formContainer.classList.remove("hidden");
        alert("Ocurrió un error. Intenta nuevamente.");
    }
});
