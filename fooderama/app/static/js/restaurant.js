document.addEventListener("DOMContentLoaded", function () {
  const cartButton = document.getElementById("cartButton");
  const cart = document.getElementById("cart");
  const closeCart = document.getElementById("closeCart");
  const addToCartForm = document.getElementById("addToCartForm");
  const cartItemsContainer = document.querySelector("#cart tbody");
  let cartItems = [];

  cartButton.addEventListener("click", function () {
    cart.classList.toggle("hidden");
  });

  closeCart.addEventListener("click", function () {
    cart.classList.add("hidden");
  });

  const modal = document.getElementById("static-modal");
  const modalBackdrop = document.getElementById("static-modal");
  const modalContent = document.getElementById("addToCartForm");
  const pratoImagem = document.getElementById("modalPratoImagem");
  const pratoNome = document.getElementById("modalPratoNome");
  const pratoDescricao = document.getElementById("modalPratoDescricao");
  const pratoPreco = document.getElementById("modalPratoPreco");
  const enderecosContainer = document.querySelector(
    "#enderecosContainer .flex"
  );
  const totalValue = document.getElementById("totalValue");
  const quantidadeInput = document.querySelector('input[name="quantidade"]');
  let currentPrato = null;
  let currentEnderecos = [];

  // Elementos do modal de endereços
  const addressModal = document.getElementById("addressModal");
  const changeAddressBtn = document.getElementById("changeAddressBtn");
  const closeAddressModal = document.getElementById("closeAddressModal");
  const addressList = document.getElementById("addressList");
  const addNewAddressBtn = document.getElementById("addNewAddressBtn");

  window.selectAddress = function (addressId) {
    const selectedAddress = currentEnderecos.find(
      (addr) => addr.ID_Endereco === addressId
    );

    if (selectedAddress) {
      // Atualizar o endereço no modal do prato
      enderecosContainer.innerHTML = "";
      const addressElement = document.createElement("div");
      addressElement.textContent = `${selectedAddress.Rua}, ${selectedAddress.Numero} - ${selectedAddress.Bairro}, CEP: ${selectedAddress.CEP}`;
      enderecosContainer.appendChild(addressElement);

      // Fechar modal de endereços
      closeAddressModalFunc();
    }
  };

  // Função para abrir o modal com as informações do prato e endereço
  function openModal(prato, foodType, enderecos) {
    currentPrato = prato;
    currentEnderecos = enderecos; // Armazenar endereços atuais
    pratoImagem.src = `../static/images/tipos_comida/${foodType}.png`;
    pratoNome.textContent = prato.Nome;
    pratoDescricao.textContent = prato.Descricao;
    pratoPreco.textContent = `R$ ${prato.Preco.toFixed(2)}`;
    quantidadeInput.value = 1; // Resetar a quantidade para 1

    // Primeiro mostra o modal e backdrop
    modal.classList.remove("hidden");
    modalBackdrop.classList.remove("hidden");

    // Garantir que as classes de animação estejam removidas inicialmente
    modalContent.classList.remove("scale-100", "opacity-100");

    // Pequeno atraso para garantir que a classe hidden seja removida antes da animação
    setTimeout(() => {
      modalContent.classList.add("scale-100", "opacity-100");
    }, 10);

    updateTotalValue(prato.Preco, quantidadeInput.value);

    // Preencher o endereço no modal
    enderecosContainer.innerHTML = "";
    if (enderecos.length > 0) {
      // Ordena os endereços pela Data_Atualizacao em ordem decrescente
      enderecos.sort(
        (a, b) => new Date(b.Data_Atualizacao) - new Date(a.Data_Atualizacao)
      );
      const address = enderecos[0]; // Pega o endereço mais recente
      const addressElement = document.createElement("div");
      addressElement.textContent = `${address.Rua}, ${address.Numero} - ${address.Bairro}, CEP: ${address.CEP}`;
      enderecosContainer.appendChild(addressElement);
    }
  }

  // Função para atualizar o valor total
  function updateTotalValue(preco, quantidade) {
    const total = preco * quantidade;
    totalValue.textContent = `Valor total: R$ ${total.toFixed(2)}`;
  }

  // Adiciona evento de clique para cada botão de abrir modal
  document.querySelectorAll(".open-modal-btn").forEach((button) => {
    button.addEventListener("click", function () {
      try {
        const prato = JSON.parse(this.getAttribute("data-prato"));
        const foodType = this.getAttribute("data-food-type");
        const enderecos = JSON.parse(this.getAttribute("data-enderecos"));
        openModal(prato, foodType, enderecos);
      } catch (error) {
        console.error(
          "Erro ao processar os dados do prato ou endereços:",
          error
        );
      }
    });
  });

  // Atualiza o valor total quando a quantidade muda
  quantidadeInput.addEventListener("input", function (e) {
    var value = e.target.value;
    if (value === "0") {
      e.target.value = "";
    }
    if (currentPrato) {
      updateTotalValue(currentPrato.Preco, e.target.value);
    }
  });

  // Define a quantidade para 1 se o campo estiver vazio ao perder o foco
  quantidadeInput.addEventListener("blur", function (e) {
    if (e.target.value === "") {
      e.target.value = "1";
      if (currentPrato) {
        updateTotalValue(currentPrato.Preco, e.target.value);
      }
    }
  });

  function setModalPratoPreco(preco) {
    const precoElement = document.getElementById("modalPratoPreco");
    if (preco <= 0) {
      preco = 1;
    }
    precoElement.textContent = `R$ ${preco.toFixed(2)}`;
  }

  // Função para fechar o modal
  function closeModal() {
    console.log("Fechando modal...");

    // Remove as classes de animação primeiro
    modalContent.classList.remove("scale-100", "opacity-100");

    // Restaurar scroll do body
    document.body.style.overflow = "";

    // Depois de um pequeno delay, esconde o modal completamente
    setTimeout(() => {
      modal.classList.add("hidden");

      // Garantir que todas as overlays sejam removidas
      const allModals = document.querySelectorAll('[id*="modal"]');
      allModals.forEach((modalEl) => {
        if (modalEl !== addressModal) {
          // Não mexer no modal de endereços
          modalEl.classList.add("hidden");
          modalEl.style.display = "none";
        }
      });

      // Remover qualquer backdrop que possa ter ficado
      const backdrops = document.querySelectorAll(".fixed.inset-0");
      backdrops.forEach((backdrop) => {
        if (backdrop !== addressModal) {
          backdrop.style.display = "none";
        }
      });

      console.log("Modal fechado completamente!");
    }, 300); // 300ms para coincidir com a duração da animação CSS
  }

  // Fechar o modal ao clicar no botão de fechar
  document
    .querySelectorAll('[data-modal-hide="static-modal"]')
    .forEach((button) => {
      button.addEventListener("click", function () {
        closeModal();
      });
    });

  // Fechar o modal ao clicar no backdrop (fundo escuro)
  modalBackdrop.addEventListener("click", function (e) {
    // Só fecha se clicar diretamente no backdrop, não nos elementos filhos
    if (e.target === modalBackdrop) {
      closeModal();
    }
  });

  // Adicionar item ao carrinho
  addToCartForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const quantidade = parseInt(quantidadeInput.value);
    const item = {
      id: currentPrato.ID_Prato,
      nome: currentPrato.Nome,
      preco: currentPrato.Preco,
      quantidade: quantidade,
      total: currentPrato.Preco * quantidade,
    };
    cartItems.push(item);
    updateCart();

    closeModal();
  });

  // Atualizar o carrinho
  function updateCart() {
    cartItemsContainer.innerHTML = "";
    let subTotal = 0;
    cartItems.forEach((item) => {
      subTotal += item.total;
      const row = document.createElement("tr");
      row.classList.add("border-b");
      row.innerHTML = `
                <td class="py-4">
                    <div class="product flex items-center space-x-3">
                        <img src="https://picsum.photos/50" alt="" class="w-12 h-12 rounded-md" />
                        <div class="info">
                            <div class="name font-medium">${item.nome}</div>
                        </div>
                    </div>
                </td>
                <td class="py-4">R$ ${item.preco.toFixed(2)}</td>
                <td class="py-4">${item.quantidade}</td>
                <td class="py-4">R$ ${item.total.toFixed(2)}</td>
                <td class="py-4"><button class="remove" data-id="${
                  item.id
                }"><i class="bx bx-x"></i></button></td>
            `;
      cartItemsContainer.appendChild(row);
    });
    document.querySelector(
      "#cart .sub-total"
    ).textContent = `R$ ${subTotal.toFixed(2)}`;
  }

  // Remover item do carrinho
  cartItemsContainer.addEventListener("click", function (e) {
    if (e.target.closest(".remove")) {
      const itemId = e.target.closest(".remove").getAttribute("data-id");
      cartItems = cartItems.filter((item) => item.id !== itemId);
      updateCart();
    }
  });

  // Finalizar compra
  const finalizarCompraButton = document.querySelector(
    "#cart button.finalizar-compra"
  );
  finalizarCompraButton.addEventListener("click", function () {
    const paymentMethod = document.querySelector(
      'select[name="payment_method"]'
    ).value;
    if (paymentMethod === "Default") {
      alert("Por favor, selecione um método de pagamento.");
      return;
    }

    fetch("/finalizar_compra", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        payment_method: paymentMethod,
        cart_items: cartItems,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          alert(data.error);
        } else {
          alert(data.message);
          cartItems = [];
          updateCart();
          cart.classList.add("hidden");
        }
      })
      .catch((error) => {
        console.error("Erro ao finalizar compra:", error);
      });
  });

  // Funcionalidades do modal de endereços
  function openAddressModal() {
    loadAddresses();
    addressModal.classList.remove("hidden");
  }

  function closeAddressModalFunc() {
    addressModal.classList.add("hidden");
  }

  function loadAddresses() {
    addressList.innerHTML = "Carregando...";

    fetch("/api/enderecos")
      .then((response) => response.json())
      .then((addresses) => {
        currentEnderecos = addresses;
        renderAddresses(addresses);
      })
      .catch((error) => {
        console.error("Erro ao carregar endereços:", error);
        addressList.innerHTML = "Erro ao carregar endereços.";
      });
  }

  function renderAddresses(addresses) {
    if (addresses.length === 0) {
      addressList.innerHTML =
        "<p class='text-gray-500 text-center py-4'>Nenhum endereço cadastrado.</p>";
      return;
    }

    addressList.innerHTML = addresses
      .map((address, index) => {
        // Escapar caracteres especiais - converter para string primeiro
        const rua = String(address.Rua || "")
          .replace(/'/g, "&#39;")
          .replace(/"/g, "&quot;");
        const numero = String(address.Numero || "")
          .replace(/'/g, "&#39;")
          .replace(/"/g, "&quot;");
        const bairro = String(address.Bairro || "")
          .replace(/'/g, "&#39;")
          .replace(/"/g, "&quot;");
        const cep = String(address.CEP || "")
          .replace(/'/g, "&#39;")
          .replace(/"/g, "&quot;");

        return `
        <div class="border-b border-gray-200 py-3 last:border-b-0">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <p class="font-medium text-gray-900">${rua}, ${numero}</p>
              <p class="text-sm text-gray-600">${bairro} - CEP: ${cep}</p>
            </div>
            <button onclick="selectAddress('${address.ID_Endereco}')" 
                    class="ml-3 px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600">
              Escolher
            </button>
          </div>
        </div>
      `;
      })
      .join("");
  }

  // Event listeners para modal de endereços
  if (changeAddressBtn) {
    changeAddressBtn.addEventListener("click", function (e) {
      e.preventDefault();
      openAddressModal();
    });
  }

  if (closeAddressModal) {
    closeAddressModal.addEventListener("click", closeAddressModalFunc);
  }

  if (addNewAddressBtn) {
    addNewAddressBtn.addEventListener("click", function () {
      window.open("/cadastrar_endereco", "_blank");
    });
  }

  // Fechar modal ao clicar fora dele
  addressModal.addEventListener("click", function (e) {
    if (e.target === addressModal) {
      closeAddressModalFunc();
    }
  });
});
