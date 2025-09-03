// Navegação dropdown do carrinho
const cartDropdown = document.getElementById("navbarCartDropdown");
const cartButton = document.getElementById("navbarCartButton");

// Verificar se os elementos existem antes de adicionar event listeners
if (cartButton && cartDropdown) {

// Função para abrir o dropdown com animação
function openDropdown() {
  cartDropdown.classList.remove("hidden"); // Torna o dropdown visível
  setTimeout(() => {
    cartDropdown.classList.add("opacity-100", "translate-y-0"); // Inicia a animação
  }, 10); // Atraso curto para aplicar transições
}

// Função para fechar o dropdown com animação
function closeDropdown() {
  cartDropdown.classList.remove("opacity-100", "translate-y-0"); // Reverte a animação
  setTimeout(() => {
    cartDropdown.classList.add("hidden"); // Esconde após a transição
  }, 300); // Aguarda a duração da animação
}

// Alterna entre abrir e fechar o dropdown ao clicar no botão do carrinho
cartButton.addEventListener("click", function (event) {
  event.stopPropagation(); // Impede a propagação para o document
  if (cartDropdown.classList.contains("hidden")) {
    openDropdown();
  } else {
    closeDropdown();
  }
});

// Fecha o dropdown ao clicar fora dele
document.addEventListener("click", function (event) {
  if (
    !cartDropdown.classList.contains("hidden") &&
    !cartButton.contains(event.target) &&
    !cartDropdown.contains(event.target)
  ) {
    closeDropdown();
  }
});

// Flash messages auto-hide
setTimeout(function () {
  var flashMessages = document.getElementById("flash-messages");
  if (flashMessages) {
    flashMessages.style.display = "none";
  }
}, 5000); // 5000 milliseconds = 5 seconds

} // Fechar o bloco if para verificação dos elementos do carrinho
