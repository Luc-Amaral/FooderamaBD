// Variáveis globais
let currentRestaurantId = null;

// Obter o ID do restaurante da URL
function obterRestauranteIdDaUrl() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get("id");
}

// Carregar horários ao abrir a página
async function carregarHorarios() {
  const restauranteId = obterRestauranteIdDaUrl();

  if (!restauranteId) {
    alert("ID do restaurante não encontrado na URL.");
    voltarParaRestaurante();
    return;
  }

  currentRestaurantId = restauranteId;

  try {
    console.log("Carregando horários para restaurante:", restauranteId);

    const response = await fetch(`/api/horarios/${restauranteId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const horarios = await response.json();
    console.log("Horários recebidos:", horarios);

    // Mapear dias da semana
    const diasMap = {
      Segunda: "segunda",
      Terca: "terca",
      Quarta: "quarta",
      Quinta: "quinta",
      Sexta: "sexta",
      Sabado: "sabado",
      Domingo: "domingo",
    };

    // Limpar formulário (valores padrão)
    const diasSemana = [
      "segunda",
      "terca",
      "quarta",
      "quinta",
      "sexta",
      "sabado",
      "domingo",
    ];

    diasSemana.forEach((dia) => {
      document.getElementById(`${dia}_ativo`).checked = false;
      document.getElementById(`${dia}_abertura`).value = "08:00";
      document.getElementById(`${dia}_fechamento`).value = "18:00";
    });

    // Preencher com os horários existentes
    horarios.forEach((horario) => {
      const diaForm = diasMap[horario.DiaSemana];
      if (diaForm) {
        document.getElementById(`${diaForm}_ativo`).checked =
          horario.Status === 1;
        document.getElementById(`${diaForm}_abertura`).value =
          horario.HoraAbertura;
        document.getElementById(`${diaForm}_fechamento`).value =
          horario.HoraFechamento;
      }
    });
  } catch (error) {
    console.error("Erro ao carregar horários:", error);
  }
}

// Salvar horários
async function salvarHorarios() {
  if (!currentRestaurantId) {
    alert("Erro: ID do restaurante não encontrado.");
    return;
  }

  try {
    // Coletar dados do formulário
    const diasSemana = [
      { nome: "Segunda", form: "segunda" },
      { nome: "Terca", form: "terca" },
      { nome: "Quarta", form: "quarta" },
      { nome: "Quinta", form: "quinta" },
      { nome: "Sexta", form: "sexta" },
      { nome: "Sabado", form: "sabado" },
      { nome: "Domingo", form: "domingo" },
    ];

    const horarios = [];
    let hasError = false;

    diasSemana.forEach((dia) => {
      const ativo = document.getElementById(`${dia.form}_ativo`).checked;
      const abertura = document.getElementById(`${dia.form}_abertura`).value;
      const fechamento = document.getElementById(
        `${dia.form}_fechamento`
      ).value;

      // Validar se horário de abertura é antes do fechamento
      if (ativo && abertura && fechamento && abertura >= fechamento) {
        alert(
          `Erro: O horário de abertura deve ser anterior ao horário de fechamento para ${dia.nome.toLowerCase()}-feira.`
        );
        hasError = true;
        return;
      }

      horarios.push({
        dia: dia.nome,
        abertura: abertura,
        fechamento: fechamento,
        status: ativo ? 1 : 0,
      });
    });

    if (hasError) return;

    // Mostrar loading
    const salvarBtn = document.getElementById("salvar-btn");
    const originalText = salvarBtn.textContent;
    salvarBtn.textContent = "Salvando...";
    salvarBtn.disabled = true;

    // Enviar dados para o servidor
    const response = await fetch("/api/salvar_horarios", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        restaurante_id: currentRestaurantId,
        horarios: horarios,
      }),
    });

    const result = await response.json();

    if (response.ok) {
      alert("Horários salvos com sucesso!");
      // Voltar para a página do restaurante
      voltarParaRestaurante();
    } else {
      alert(result.error || "Erro ao salvar horários");
    }
  } catch (error) {
    console.error("Erro ao salvar horários:", error);
    alert("Erro ao salvar horários. Tente novamente.");
  } finally {
    // Restaurar botão
    const salvarBtn = document.getElementById("salvar-btn");
    if (salvarBtn) {
      salvarBtn.textContent = "Salvar Horários";
      salvarBtn.disabled = false;
    }
  }
}

// Voltar para a página do restaurante
function voltarParaRestaurante() {
  if (currentRestaurantId) {
    window.location.href = `/restaurant/${currentRestaurantId}`;
  } else {
    window.history.back();
  }
}

// Inicializar quando a página carregar
document.addEventListener("DOMContentLoaded", function () {
  carregarHorarios();
});
