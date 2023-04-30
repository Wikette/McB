window.addEventListener("DOMContentLoaded", function () {
  let cropper;
  let inputImage = document.getElementById("photo");
  let image = document.getElementById("image");
  let croppedImage = document.getElementById("cropped_image");

  // Initialise le cropper lors de l'upload d'une photo
  inputImage.addEventListener("change", function () {
    let file = inputImage.files[0];
    if (file) {
      let reader = new FileReader();
      reader.onload = function (e) {
        image.src = e.target.result;
        image.style.display = "block";
        if (cropper) {
          cropper.destroy();
        }
        cropper = new Cropper(image, {
          aspectRatio: 1,
          viewMode: 1,
          crop: function (event) {
            croppedImage.value = cropper.getCroppedCanvas().toDataURL();
          },
        });
      };
      reader.readAsDataURL(file);
    }
  });
});
