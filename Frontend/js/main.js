document.addEventListener('DOMContentLoaded', () => {
  // Inicializar estado oculto
  document.getElementById('loading').classList.add('hidden');
  document.getElementById('result').classList.add('hidden');
});

document.getElementById('upload-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const loadingDiv = document.getElementById('loading');
  const loadingSpinner = document.getElementById('loader');
  const loadingModal = document.getElementById('loading-modal');
  const loadingModalTexts = document.getElementById('loading-modal-texts');

  const resultDiv = document.getElementById('result');
  const imageResultDiv = document.getElementById('image-result');
  const videoResultDiv = document.getElementById('video-result');
  const previewImage = document.getElementById('preview-image');

  const imageServer = document.getElementById('image-server');
  const frameServer = document.getElementById('frame-server');

  const formData = new FormData();
  const image = document.getElementById('image').files[0];
  const video = document.getElementById('video').files[0];

  if (!image || !video) {
    alert('Por favor, selecciona una imagen y un video antes de subir.');
    return;
  }

  formData.append('imagen', image);
  formData.append('video', video);

  // Mostrar la imagen cargada en el contenedor de carga
  previewImage.src = URL.createObjectURL(image);

  loadingDiv.classList.remove('hidden');
  loadingSpinner.classList.remove('hidden');

  try {
    const response = await fetch('https://rostros.buho.media/upload/', {
      method: 'POST',
      body: formData,
    });

    const result = await response.json();

    // Agregar un parámetro único para evitar el caché
    const timestamp = new Date().getTime();

    imageServer.src = `https://rostros.buho.media/imagen/?_=${timestamp}`;
    frameServer.src = `https://rostros.buho.media/video_frame/?_=${timestamp}`;

    // Ocultar el contenedor de carga y mostrar los resultados
    loadingSpinner.classList.add('hidden'); // ocultar loader

    loadingModal.classList.remove('hidden'); // mostrar modal

    loadingModalTexts.innerHTML = `
    <p>Ubicación de la cara: ${JSON.stringify(
      result.imagen.ubicaciones_caras
    )}</p>

    <p>Coincidencias detectadas: ${result.imagen.numero_caras_detectadas}</p>
    `;
  } catch (error) {
    console.error('Error al procesar los archivos:', error);
    loadingDiv.classList.add('hidden');
    alert('Ocurrió un error. Intenta nuevamente.');
  }
});
