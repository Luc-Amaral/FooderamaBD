// Adicionar evento para o botão Cancel
document.addEventListener("DOMContentLoaded", function () {
  const cancelButton = document.querySelector('button[type="button"]');
  if (cancelButton) {
    cancelButton.addEventListener("click", function () {
      window.location.href = "/autenticar_login";
    });
  }
});
