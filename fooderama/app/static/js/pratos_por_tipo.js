// Variáveis globais
let cart = [];
let currentRestaurantId = null;
let enderecos = [];
let currentPrato = null;

// Carregar endereços do usuário
async function carregarEnderecos() {
  try {
    const response = await fetch("/api/enderecos");
    enderecos = await response.json();

    // Atualizar select do modal do prato
    const modalSelect = document.getElementById("modalEndereco");
    if (modalSelect) {
      modalSelect.innerHTML = '<option value="">Selecione um endereço</option>';
      enderecos.forEach((endereco) => {
        modalSelect.innerHTML += `<option value="${endereco.ID_Endereco}">${endereco.Rua}, ${endereco.Numero} - ${endereco.Bairro}, ${endereco.CEP}</option>`;
      });
    }
  } catch (error) {
    console.error("Erro ao carregar endereços:", error);
  }
}

// Abrir modal do prato
function abrirModalPrato(
  id,
  restauranteId,
  nome,
  descricao,
  preco,
  estoque,
  nomeRestaurante
) {
  currentPrato = {
    id: id,
    restauranteId: restauranteId,
    nome: nome,
    descricao: descricao,
    preco: preco,
    estoque: estoque,
    nomeRestaurante: nomeRestaurante,
  };

  document.getElementById("modalPratoNome").textContent = nome;
  document.getElementById("modalPratoNome2").textContent = nome;
  document.getElementById("modalPratoRestaurante").textContent =
    nomeRestaurante;
  document.getElementById("modalPratoDescricao").textContent = descricao;
  document.getElementById("modalPratoPreco").textContent = `R$ ${preco.toFixed(
    2
  )}`;
  document.getElementById("modalQuantidade").value = 1;
  document.getElementById("modalQuantidade").max = estoque;

  atualizarValorTotal();
  document.getElementById("prato-modal").classList.remove("hidden");
}

// Fechar modal do prato
function fecharModalPrato() {
  document.getElementById("prato-modal").classList.add("hidden");
  currentPrato = null;
}

// Aumentar quantidade
function aumentarQuantidade() {
  const input = document.getElementById("modalQuantidade");
  const max = parseInt(input.max);
  if (parseInt(input.value) < max) {
    input.value = parseInt(input.value) + 1;
    atualizarValorTotal();
  }
}

// Diminuir quantidade
function diminuirQuantidade() {
  const input = document.getElementById("modalQuantidade");
  if (parseInt(input.value) > 1) {
    input.value = parseInt(input.value) - 1;
    atualizarValorTotal();
  }
}

// Atualizar valor total no modal
function atualizarValorTotal() {
  if (currentPrato) {
    const quantidade = parseInt(
      document.getElementById("modalQuantidade").value
    );
    const total = currentPrato.preco * quantidade;
    document.getElementById(
      "modalValorTotal"
    ).textContent = `Valor total: R$ ${total.toFixed(2)}`;
  }
}

// Adicionar ao carrinho
function adicionarAoCarrinho() {
  if (!currentPrato) return;

  const endereco = document.getElementById("modalEndereco").value;
  if (!endereco) {
    alert("Por favor, selecione um endereço de entrega.");
    return;
  }

  // Verificar se é do mesmo restaurante
  if (
    currentRestaurantId &&
    currentRestaurantId !== currentPrato.restauranteId
  ) {
    if (
      !confirm(
        "Você já tem itens de outro restaurante no carrinho. Deseja limpar o carrinho e adicionar este item?"
      )
    ) {
      return;
    }
    cart = [];
  }

  currentRestaurantId = currentPrato.restauranteId;
  const quantidade = parseInt(document.getElementById("modalQuantidade").value);

  // Verificar se o item já está no carrinho
  const existingItem = cart.find((item) => item.id === currentPrato.id);

  if (existingItem) {
    existingItem.quantidade += quantidade;
  } else {
    cart.push({
      id: currentPrato.id,
      nome: currentPrato.nome,
      preco: currentPrato.preco,
      quantidade: quantidade,
      nomeRestaurante: currentPrato.nomeRestaurante,
    });
  }

  atualizarCarrinho();
  fecharModalPrato();

  // Mostrar notificação
  alert(`${currentPrato.nome} foi adicionado ao carrinho!`);
}

// Atualizar carrinho
function atualizarCarrinho() {
  const cartButton = document.getElementById("cart-button");
  const cartCount = document.getElementById("cart-count");

  if (cart.length > 0) {
    cartButton.classList.remove("hidden");
    cartCount.textContent = cart.reduce(
      (sum, item) => sum + item.quantidade,
      0
    );
  } else {
    cartButton.classList.add("hidden");
  }
}

// Abrir checkout
function abrirCheckout() {
  if (cart.length === 0) {
    alert("Seu carrinho está vazio!");
    return;
  }

  // Mostrar itens do carrinho
  const cartItemsDiv = document.getElementById("cart-items");
  cartItemsDiv.innerHTML = "";

  let total = 0;
  cart.forEach((item, index) => {
    const itemTotal = item.preco * item.quantidade;
    total += itemTotal;

    cartItemsDiv.innerHTML += `
      <div class="flex justify-between items-center mb-3 p-3 border rounded">
        <div>
          <div class="font-semibold">${item.nome}</div>
          <div class="text-sm text-gray-500">${item.nomeRestaurante}</div>
          <div class="text-sm">Qtd: ${
            item.quantidade
          } x R$ ${item.preco.toFixed(2)}</div>
        </div>
        <div class="text-right">
          <div class="font-bold text-orange-500">R$ ${itemTotal.toFixed(
            2
          )}</div>
          <button onclick="removerDoCarrinho(${index})" class="text-red-500 text-sm hover:text-red-700">Remover</button>
        </div>
      </div>
    `;
  });

  document.getElementById(
    "total-value"
  ).textContent = `Total: R$ ${total.toFixed(2)}`;
  document.getElementById("checkout-modal").classList.remove("hidden");
}

// Fechar checkout
function fecharCheckout() {
  document.getElementById("checkout-modal").classList.add("hidden");
}

// Remover do carrinho
function removerDoCarrinho(index) {
  cart.splice(index, 1);
  if (cart.length === 0) {
    currentRestaurantId = null;
    fecharCheckout();
  } else {
    abrirCheckout(); // Reabrir para atualizar
  }
  atualizarCarrinho();
}

// Finalizar pedido
function finalizarPedido() {
  if (cart.length === 0) {
    alert("Seu carrinho está vazio!");
    return;
  }

  // Simular finalização do pedido
  alert("Pedido confirmado! Em breve você receberá a confirmação.");

  // Limpar carrinho
  cart = [];
  currentRestaurantId = null;
  atualizarCarrinho();
  fecharCheckout();
}

// Adicionar novo endereço (placeholder)
function adicionarEndereco() {
  alert("Funcionalidade de adicionar endereço será implementada em breve.");
}

// Eventos de inicialização
document.addEventListener("DOMContentLoaded", function () {
  carregarEnderecos();

  // Event listener para mudança na quantidade
  const quantidadeInput = document.getElementById("modalQuantidade");
  if (quantidadeInput) {
    quantidadeInput.addEventListener("input", atualizarValorTotal);
  }
});

// Fechar modal clicando fora
document.addEventListener("click", function (e) {
  if (e.target.id === "prato-modal") {
    fecharModalPrato();
  }
  if (e.target.id === "checkout-modal") {
    fecharCheckout();
  }
});
