
// Função para consumir a API e manipular a resposta
async function fetchUsers() {
  const apiUrl = 'http://localhost:5000/api/users';
    try {
        // Faz a requisição para a API
        const response = await fetch(apiUrl,{
          method: "GET",
          headers:{
            'Content-Type': 'application/json',
          }
        });
        
        // Verifica se a resposta foi bem-sucedida
        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status}`);
        }

        // Converte a resposta em JSON
        const users = await response.json();
        
        // Opcional: Exibe os dados em uma página HTML
        displayUsers(users);
    } catch (error) {
        console.error('Erro ao buscar usuários:', error);
    }
}

// Função para exibir os usuários no HTML
function displayUsers(users) {
    const usersContainer = document.getElementById('usersContainer');
    usersContainer.innerHTML = ''; // Limpa o conteúdo anterior

    users.forEach(user => {
        // Cria um elemento de lista para cada usuário
        const userElement = document.createElement('li');
        userElement.textContent = `ID: ${user.ID_Cliente}, Nome: ${user.Nome}, Email: ${user.Email}`;
        usersContainer.appendChild(userElement);
    });
}

// Chama a função para buscar os usuários ao carregar a página
document.addEventListener('DOMContentLoaded', fetchUsers);