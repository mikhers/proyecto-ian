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

    // Ocultar el contenedor de carga y mostrar los resultados
    loadingSpinner.classList.add('hidden'); // ocultaro loader

    setTimeout(() => {
      loadingModal.classList.remove('hidden'); // mostrar modal
    }, 4000);

    loadingModalTexts.innerHTML = `
    <p>Ubicación de la cara: ${JSON.stringify(
      result.imagen.ubicaciones_caras
    )}</p>

    <p>Coincidecias detectadas: ${result.imagen.numero_caras_detectadas}</p>
    
    `;


  } catch (error) {
    console.error('Error al procesar los archivos:', error);
    loadingDiv.classList.add('hidden');
    alert('Ocurrió un error. Intenta nuevamente.');
  }
});
