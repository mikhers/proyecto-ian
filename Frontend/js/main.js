document.getElementById("upload-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData();
    const image = document.getElementById("image").files[0];
    const video = document.getElementById("video").files[0];

    formData.append("image", image);
    formData.append("video", video);

    const response = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: formData,
    });

    const result = await response.json();
    alert(JSON.stringify(result));
});