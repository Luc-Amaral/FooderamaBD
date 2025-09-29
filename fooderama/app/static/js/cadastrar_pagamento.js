
console.log("DEBUG: cadastrar_pagamento.js carregado");


function toggleCartaoFields() {
    const cartaoFields = document.getElementById("cartaoFields");
    const numeroCartao = document.getElementById("numero_cartao");
    const nomePortador = document.getElementById("nome_portador");
    const dataVencimento = document.getElementById("data_vencimento");
    const cvv = document.getElementById("cvv");

    const selectedRadio = document.querySelector(
        'input[name="tipo_metodo"]:checked'
    );

    if (!selectedRadio) {
        cartaoFields.classList.add("hidden");
        return;
    }

    const selectedValue = selectedRadio.value;

    if (selectedValue === "Debito" || selectedValue === "Credito") {
        // Mostrar campos do cartão
        cartaoFields.classList.remove("hidden");

        // Tornar campos obrigatórios
        numeroCartao.required = true;
        nomePortador.required = true;
        dataVencimento.required = true;
        cvv.required = true;

        console.log("DEBUG: Campos de cartão habilitados para", selectedValue);
    } else {
        // Ocultar campos do cartão (PIX)
        cartaoFields.classList.add("hidden");

        // Remover obrigatoriedade
        numeroCartao.required = false;
        nomePortador.required = false;
        dataVencimento.required = false;
        cvv.required = false;

        // Limpar campos
        numeroCartao.value = "";
        nomePortador.value = "";
        dataVencimento.value = "";
        cvv.value = "";

        console.log("DEBUG: Campos de cartão desabilitados para PIX");
    }
}


function formatCardNumber(e) {
    let value = e.target.value.replace(/\s/g, "").replace(/[^0-9]/gi, "");
    let formattedValue = value.match(/.{1,4}/g)?.join(" ") ?? value;

    // Limitar a 19 caracteres (16 dígitos + 3 espaços)
    if (formattedValue.length > 19) {
        formattedValue = formattedValue.substring(0, 19);
    }

    e.target.value = formattedValue;
}

/**
 * Remove caracteres não numéricos do CVV
 * @param {Event} e - Evento de input
 */
function formatCVV(e) {
    e.target.value = e.target.value.replace(/[^0-9]/g, "");
}

/**
 * Formata a data de vencimento no formato MM/AA
 * @param {HTMLInputElement} input 
 */

function formatExpiry(input) {
    let value = input.value.replace(/\D/g, "");

    if (value.length >= 2) {
        value = value.substring(0, 2) + "/" + value.substring(2, 4);
    }

    input.value = value;
}

/**
 * Valida o formulário antes do envio
 * @param {Event} e - Evento de submit
 * @returns {boolean} - True se válido, false caso contrário
 */
function validateForm(e) {
    const selectedRadio = document.querySelector(
        'input[name="tipo_metodo"]:checked'
    );

    // Verificar se um tipo foi selecionado
    if (!selectedRadio) {
        e.preventDefault();
        alert("Por favor, selecione um tipo de método de pagamento.");
        return false;
    }

    const selectedValue = selectedRadio.value;
    console.log("DEBUG: Validando formulário para", selectedValue);

    // Se for cartão, validar campos específicos
    if (selectedValue === "Debito" || selectedValue === "Credito") {
        const numeroCartao = document.getElementById("numero_cartao").value.trim();
        const nomePortador = document.getElementById("nome_portador").value.trim();
        const dataVencimento = document
            .getElementById("data_vencimento")
            .value.trim();
        const cvv = document.getElementById("cvv").value.trim();

        // Verificar se todos os campos estão preenchidos
        if (!numeroCartao || !nomePortador || !dataVencimento || !cvv) {
            e.preventDefault();
            alert("Por favor, preencha todos os campos do cartão.");
            return false;
        }

        // Validar formato da data MM/AA
        const datePattern = /^\d{2}\/\d{2}$/;
        if (!datePattern.test(dataVencimento)) {
            e.preventDefault();
            alert("Por favor, digite a data de vencimento no formato MM/AA.");
            return false;
        }

        // Validar se o número do cartão tem pelo menos 13 dígitos
        const numeroLimpo = numeroCartao.replace(/\s/g, "");
        if (numeroLimpo.length < 13 || numeroLimpo.length > 19) {
            e.preventDefault();
            alert("Por favor, digite um número de cartão válido (13-19 dígitos).");
            return false;
        }

        // Validar CVV (3 ou 4 dígitos)
        if (cvv.length < 3 || cvv.length > 4) {
            e.preventDefault();
            alert("Por favor, digite um CVV válido (3 ou 4 dígitos).");
            return false;
        }

        // Validar mês da data de vencimento
        const [mes] = dataVencimento.split("/");
        if (parseInt(mes) < 1 || parseInt(mes) > 12) {
            e.preventDefault();
            alert("Por favor, digite um mês válido (01-12).");
            return false;
        }

        console.log("DEBUG: Validação de cartão aprovada");
    }

    console.log("DEBUG: Formulário válido, enviando...");
    return true;
}


function confirmDelete(metodId) {
    return confirm("Tem certeza que deseja excluir este método de pagamento?");
}


function initializePaymentForm() {
    console.log("DEBUG: Inicializando formulário de pagamento");

    // Event listener para formatação do número do cartão
    const numeroCartaoInput = document.getElementById("numero_cartao");
    if (numeroCartaoInput) {
        numeroCartaoInput.addEventListener("input", formatCardNumber);
    }

    // Event listener para formatação do CVV
    const cvvInput = document.getElementById("cvv");
    if (cvvInput) {
        cvvInput.addEventListener("input", formatCVV);
    }

    // Event listener para validação do formulário
    const pagamentoForm = document.getElementById("pagamentoForm");
    if (pagamentoForm) {
        pagamentoForm.addEventListener("submit", validateForm);
    }

    // Event listeners para os radio buttons
    const radioButtons = document.querySelectorAll('input[name="tipo_metodo"]');
    radioButtons.forEach((radio) => {
        radio.addEventListener("change", toggleCartaoFields);
    });

    console.log("DEBUG: Event listeners configurados");
}

// Inicializar quando o DOM estiver pronto
document.addEventListener("DOMContentLoaded", initializePaymentForm);

// Exportar funções para uso global (se necessário)
window.PaymentFormAPI = {
    toggleCartaoFields,
    formatExpiry,
    confirmDelete,
    validateForm,
};
