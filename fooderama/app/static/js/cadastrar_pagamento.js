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
        cartaoFields.classList.remove("hidden");
        numeroCartao.required = true;
        nomePortador.required = true;
        dataVencimento.required = true;
        cvv.required = true;
    } else {
        cartaoFields.classList.add("hidden");
        numeroCartao.required = false;
        nomePortador.required = false;
        dataVencimento.required = false;
        cvv.required = false;

        // Limpar campos
        numeroCartao.value = "";
        nomePortador.value = "";
        dataVencimento.value = "";
        cvv.value = "";
    }
}

// Formatação automática
document
    .getElementById("numero_cartao")
    .addEventListener("input", function (e) {
        let value = e.target.value.replace(/\s/g, "").replace(/[^0-9]/gi, "");
        let formattedValue = value.match(/.{1,4}/g)?.join(" ") ?? value;
        e.target.value = formattedValue;
    });

document.getElementById("cvv").addEventListener("input", function (e) {
    e.target.value = e.target.value.replace(/[^0-9]/g, "");
});

function formatExpiry(input) {
    let value = input.value.replace(/\D/g, "");
    if (value.length >= 2) {
        value = value.substring(0, 2) + "/" + value.substring(2, 4);
    }
    input.value = value;
}

// Validação do formulário
document
    .getElementById("pagamentoForm")
    .addEventListener("submit", function (e) {
        const selectedRadio = document.querySelector(
            'input[name="tipo_metodo"]:checked'
        );

        if (!selectedRadio) {
            e.preventDefault();
            alert("Por favor, selecione um tipo de método de pagamento.");
            return false;
        }

        const selectedValue = selectedRadio.value;

        if (selectedValue === "Debito" || selectedValue === "Credito") {
            const numeroCartao = document
                .getElementById("numero_cartao")
                .value.trim();
            const nomePortador = document
                .getElementById("nome_portador")
                .value.trim();
            const dataVencimento = document
                .getElementById("data_vencimento")
                .value.trim();
            const cvv = document.getElementById("cvv").value.trim();

            if (!numeroCartao || !nomePortador || !dataVencimento || !cvv) {
                e.preventDefault();
                alert("Por favor, preencha todos os campos do cartão.");
                return false;
            }

            const datePattern = /^\d{2}\/\d{2}$/;
            if (!datePattern.test(dataVencimento)) {
                e.preventDefault();
                alert("Por favor, digite a data de vencimento no formato MM/AA.");
                return false;
            }
        }

        return true;
    });