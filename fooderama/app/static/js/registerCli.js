function showMessage() {
  var fields = ["street", "neighborhood", "number", "cep"];
  var filledFields = fields.filter(function (field) {
    var input = document.getElementById(field);
    return input.value.trim() !== "";
  });
  var messageAlert = document.getElementById("messageAlert");

  if (filledFields.length > 0 && filledFields.length < fields.length) {
    messageAlert.classList.remove("hidden");
    return false; // Prevent form submission
  } else {
    messageAlert.classList.add("hidden");
  }

  return true; 
}

// Adicionar eventos quando o documento estiver carregado
document.addEventListener("DOMContentLoaded", function () {
  // Evento para o botão Cancel
  const cancelButton = document.querySelector('button[type="button"]');
  if (cancelButton) {
    cancelButton.addEventListener("click", function () {
      window.location.href = "/autenticar_login";
    });
  }

  // Evento onsubmit para o formulário
  const form = document.querySelector("form");
  if (form) {
    form.addEventListener("submit", function (e) {
      if (!showMessage()) {
        e.preventDefault();
      }
    });
  }
});
