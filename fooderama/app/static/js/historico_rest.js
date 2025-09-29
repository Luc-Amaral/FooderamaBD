document.addEventListener("DOMContentLoaded", function () {
 

  
  let lastUpdateTime = null;
  let lastKnownOrderCount = null; 
  let refreshInterval = null;
  let isPageVisible = true;

  
  document.addEventListener("visibilitychange", function () {
    isPageVisible = !document.hidden;
    if (isPageVisible) {
      checkForNewOrders();
    }
  });

  // Funcionalidade do modal de observações
  document.addEventListener('click', function(e) {
    if (e.target.classList.contains('observacoes-btn')) {
      const pedidoId = e.target.getAttribute('data-pedido-id');
      abrirModalObservacoes(pedidoId);
    }
  });

  function abrirModalObservacoes(pedidoId) {
    const modal = document.getElementById('observacoesModal');
    const pedidoIdElement = document.getElementById('pedidoId');
    const observacoesTexto = document.getElementById('observacoesTexto');
    
    pedidoIdElement.textContent = pedidoId;
    observacoesTexto.textContent = 'Carregando...';
    modal.classList.remove('hidden');

    fetch(`/api/pedido_observacoes/${pedidoId}`)
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          observacoesTexto.textContent = `Erro: ${data.error}`;
        } else {
          observacoesTexto.textContent = data.observacoes;
        }
      })
      .catch(error => {
        console.error('Erro ao carregar observações:', error);
        observacoesTexto.textContent = 'Erro ao carregar observações';
      });
  }

  window.fecharModalObservacoes = function() {
    const modal = document.getElementById('observacoesModal');
    modal.classList.add('hidden');
  };

  // Função para obter contagem inicial de pedidos na página
  function getInitialOrderCount() {
    const pendingOrderRows = document.querySelectorAll(
      "table:first-of-type tbody tr"
    );
    // Filtrar apenas as linhas que não são mensagens de "nenhum pedido"
    const actualOrders = Array.from(pendingOrderRows).filter(
      (row) => !row.textContent.includes("Nenhum pedido pendente")
    );
    lastKnownOrderCount = actualOrders.length;
    console.log(
      `Contagem inicial de pedidos na página: ${lastKnownOrderCount}`
    );
    return lastKnownOrderCount;
  }

  // Função para verificar novos pedidos e atualizar a tabela
  async function checkForNewOrders() {
    if (!isPageVisible) return; 

    try {
      const response = await fetch("/api/get_restaurant_orders");
      if (response.ok) {
        const data = await response.json();
        const currentOrderCount = data.orders.length;

        // Na primeira verificação, apenas armazenar a contagem atual
        if (lastKnownOrderCount === null) {
          lastKnownOrderCount = currentOrderCount;
          console.log(
            `Contagem inicial definida: ${lastKnownOrderCount} pedidos`
          );
          updateOrdersTable(data.orders); 
          return;
        }

        // Verificar se o número de pedidos aumentou (novos pedidos chegaram)
        if (currentOrderCount > lastKnownOrderCount) {
          const novosPedidosCount = currentOrderCount - lastKnownOrderCount;
          console.log(
            `${novosPedidosCount} novo(s) pedido(s) detectado(s)! Atualizando tabela...`
          );
          showNotification(
            `${novosPedidosCount} novo(s) pedido(s) recebido(s)!`
          );

          // Atualizar a tabela com os novos pedidos
          updateOrdersTable(data.orders);

          // Atualizar a contagem conhecida
          lastKnownOrderCount = currentOrderCount;
        } else if (currentOrderCount < lastKnownOrderCount) {
          // Pedidos foram aceitos/recusados, atualizar tabela
          console.log(`Pedidos processados. Atualizando tabela...`);
          updateOrdersTable(data.orders);
          lastKnownOrderCount = currentOrderCount;
        } else {
          console.log(
            `Nenhum pedido novo. Contagem atual: ${currentOrderCount}, conhecida: ${lastKnownOrderCount}`
          );
        }

        lastUpdateTime = new Date().toISOString();
      }
    } catch (error) {
      console.error("Erro ao verificar novos pedidos:", error);
    }
  }

  // Função para atualizar a tabela de pedidos
  function updateOrdersTable(orders) {
    const tbody = document.querySelector("table tbody");
    if (!tbody) return;

    // Limpar tabela atual
    tbody.innerHTML = "";

    // Adicionar novos pedidos
    orders.forEach((order) => {
      const row = document.createElement("tr");
      row.className = "border-t";

      row.innerHTML = `
        <td class="py-4 pr-4">${order.ID_Pedido}</td>
        <td class="py-4 pr-4">${order.payment_method}</td>
        <td class="py-4 pr-4">${order.date} ${order.time}</td>
        <td class="py-4 pr-4">${order.total.toFixed(2)}</td>
        <td class="py-4 pr-4">
          <!-- Botão Observações (em cima) -->
          <div class="mb-2">
            <button type="button" 
                    class="w-full px-4 py-2 bg-blue-500 text-white rounded-lg observacoes-btn hover:bg-blue-600"
                    data-pedido-id="${order.ID_Pedido}">
              Observações
            </button>
          </div>
          <!-- Botões Aceitar e Recusar (embaixo, lado a lado) -->
          <div class="flex gap-2">
            <form action="/aceitar_pedido/${order.ID_Pedido}" method="post" class="flex-1">
              <button type="submit" class="w-full px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600">
                Aceitar
              </button>
            </form>
            <form action="/recusar_pedido/${order.ID_Pedido}" method="post" class="flex-1">
              <button type="submit" class="w-full px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600">
                Recusar
              </button>
            </form>
          </div>
        </td>
      `;

      tbody.appendChild(row);
    });

    // Se não há pedidos, mostrar mensagem
    if (orders.length === 0) {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td colspan="5" class="py-8 text-center text-gray-500">
          Nenhum pedido pendente no momento
        </td>
      `;
      tbody.appendChild(row);
    }
  }

  // Função para mostrar notificação
  function showNotification(message) {
    const existingNotification = document.querySelector(".notification-toast");
    if (existingNotification) {
      existingNotification.remove();
    }

    // Criar nova notificação
    const notification = document.createElement("div");
    notification.className =
      "notification-toast fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-300";
    notification.innerHTML = `
          <div class="flex items-center space-x-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>${message}</span>
          </div>
      `;

    document.body.appendChild(notification);

    // Animar entrada
    setTimeout(() => {
      notification.style.transform = "translateX(0)";
    }, 100);

    // Remover após 5 segundos
    setTimeout(() => {
      notification.style.transform = "translateX(100%)";
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 5000);
  }

  // Adicionar indicador de status de conexão
  function addConnectionIndicator() {
    const indicator = document.createElement("div");
    indicator.id = "connection-indicator";
    indicator.className =
      "fixed bottom-4 right-4 px-3 py-2 rounded-full text-sm font-medium";
    indicator.innerHTML = `
          <div class="flex items-center space-x-2">
              <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>Monitorando pedidos...</span>
          </div>
      `;
    indicator.style.backgroundColor = "rgba(0, 0, 0, 0.8)";
    indicator.style.color = "white";
    indicator.style.zIndex = "40";

    document.body.appendChild(indicator);
  }

  // Inicializar auto-refresh
  function startAutoRefresh() {
    console.log("Iniciando monitoramento de pedidos a cada 8 segundos...");

    setTimeout(() => {
      checkForNewOrders();
    }, 2000);

    // Configurar intervalo de 8 segundos
    refreshInterval = setInterval(checkForNewOrders, 8000);

    // Adicionar indicador visual
    addConnectionIndicator();
  }

  // Parar auto-refresh (útil para debug)
  window.stopAutoRefresh = function () {
    if (refreshInterval) {
      clearInterval(refreshInterval);
      refreshInterval = null;
      console.log("Auto-refresh parado.");
    }

    const indicator = document.getElementById("connection-indicator");
    if (indicator) {
      indicator.remove();
    }
  };

  // Iniciar quando a página carrega
  startAutoRefresh();

  console.log("Sistema de auto-refresh inicializado!");
  console.log("Para parar: execute stopAutoRefresh() no console");
});
