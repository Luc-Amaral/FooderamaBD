document.addEventListener("DOMContentLoaded", function () {
  // Código original para mudança de status
  const statusElements = document.querySelectorAll(".status-text");

  statusElements.forEach((statusElement) => {
    if (statusElement.textContent.trim() === "ACEITO") {
      setTimeout(() => {
        statusElement.textContent = "EM PREPARO";
        statusElement.classList.remove("text-yellow-600");
        statusElement.classList.add("text-blue-600");
      }, 3000);

      setTimeout(() => {
        statusElement.textContent = "TRANSITO";
        statusElement.classList.remove("text-blue-600");
        statusElement.classList.add("text-orange-600");
      }, 6000); // 3000 + 3000

      setTimeout(() => {
        statusElement.textContent = "ENTREGUE";
        statusElement.classList.remove("text-orange-600");
        statusElement.classList.add("text-green-600");
      }, 9000); // 6000 + 3000
    }
  });

  // NOVO: Sistema de auto-refresh para novos pedidos
  let lastUpdateTime = null;
  let refreshInterval = null;
  let isPageVisible = true;
  
  // Detectar quando a página fica visível/invisível
  document.addEventListener('visibilitychange', function() {
      isPageVisible = !document.hidden;
      if (isPageVisible) {
          checkForNewOrders(); // Verificar imediatamente quando voltar à página
      }
  });
  
  // Função para verificar novos pedidos
  async function checkForNewOrders() {
      if (!isPageVisible) return; // Não atualizar se a página não estiver visível
      
      try {
          const response = await fetch('/api/check_new_orders');
          if (response.ok) {
              const data = await response.json();
              
              // Se há novos pedidos, atualizar a página
              if (data.novos_pedidos > 0) {
                  console.log(`${data.novos_pedidos} novos pedidos encontrados! Atualizando página...`);
                  showNotification(`${data.novos_pedidos} novo(s) pedido(s) recebido(s)!`);
                  
                  // Aguardar 2 segundos para mostrar a notificação e depois recarregar
                  setTimeout(() => {
                      window.location.reload();
                  }, 2000);
              } else {
                  console.log('Nenhum novo pedido encontrado.');
              }
              
              lastUpdateTime = data.timestamp;
          }
      } catch (error) {
          console.error('Erro ao verificar novos pedidos:', error);
      }
  }
  
  // Função para mostrar notificação
  function showNotification(message) {
      // Remover notificação existente se houver
      const existingNotification = document.querySelector('.notification-toast');
      if (existingNotification) {
          existingNotification.remove();
      }
      
      // Criar nova notificação
      const notification = document.createElement('div');
      notification.className = 'notification-toast fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-300';
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
          notification.style.transform = 'translateX(0)';
      }, 100);
      
      // Remover após 5 segundos
      setTimeout(() => {
          notification.style.transform = 'translateX(100%)';
          setTimeout(() => {
              notification.remove();
          }, 300);
      }, 5000);
  }
  
  // Adicionar indicador de status de conexão
  function addConnectionIndicator() {
      const indicator = document.createElement('div');
      indicator.id = 'connection-indicator';
      indicator.className = 'fixed bottom-4 right-4 px-3 py-2 rounded-full text-sm font-medium';
      indicator.innerHTML = `
          <div class="flex items-center space-x-2">
              <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>Monitorando pedidos...</span>
          </div>
      `;
      indicator.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
      indicator.style.color = 'white';
      indicator.style.zIndex = '40';
      
      document.body.appendChild(indicator);
  }
  
  // Inicializar auto-refresh
  function startAutoRefresh() {
      console.log('Iniciando monitoramento de pedidos a cada 5 segundos...');
      
      // Verificar imediatamente
      checkForNewOrders();
      
      // Configurar intervalo de 5 segundos
      refreshInterval = setInterval(checkForNewOrders, 5000);
      
      // Adicionar indicador visual
      addConnectionIndicator();
  }
  
  // Parar auto-refresh (útil para debug)
  window.stopAutoRefresh = function() {
      if (refreshInterval) {
          clearInterval(refreshInterval);
          refreshInterval = null;
          console.log('Auto-refresh parado.');
      }
      
      const indicator = document.getElementById('connection-indicator');
      if (indicator) {
          indicator.remove();
      }
  };
  
  // Iniciar quando a página carrega
  startAutoRefresh();
  
  console.log('Sistema de auto-refresh inicializado!');
  console.log('Para parar: execute stopAutoRefresh() no console');
});
