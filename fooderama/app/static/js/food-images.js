// Configuração da API Unsplash - Chave configurada
const UNSPLASH_ACCESS_KEY = "i7dc1sDWW9VYI4wYRS807fkjL17o77mGaXy3s7y_LWU";

// Teste de carregamento
console.log("DEBUG: food-images.js carregado");

// Mapeamento de tipos de comida para termos de busca em inglês (melhores resultados)
const foodTypeMapping = {
  pizza: "pizza food",
  hamburguer: "burger hamburger",
  lanche: "sandwich snack food",
  massa: "pasta italian food",
  japonesa: "sushi japanese food",
  mexicana: "mexican food tacos",
  churrasco: "barbecue grilled meat",
  doce: "dessert cake sweet",
  sorvete: "ice cream gelato",
  vegetariana: "vegetarian salad healthy",
  "frutos do mar": "seafood fish shrimp",
  arabe: "arabic middle eastern food",
  "comida caseira": "homemade comfort food",
};

// Cache local para evitar muitas requisições
const imageCache = new Map();

/**
 * Busca uma imagem do Unsplash baseada no tipo de comida
 * @param {string} foodType - Tipo de comida
 * @param {string} foodName - Nome específico do prato
 * @returns {Promise<string>} URL da imagem
 */
async function getUnsplashImage(foodType, foodName = "") {
  // Criar chave para cache
  const cacheKey = `${foodType}-${foodName}`.toLowerCase();

  // Verificar se já temos no cache
  if (imageCache.has(cacheKey)) {
    return imageCache.get(cacheKey);
  }

  // Determinar termo de busca
  let searchTerm = foodTypeMapping[foodType.toLowerCase()] || foodType;
  if (foodName) {
    searchTerm = `${foodName} ${searchTerm}`;
  }

  try {
    // Se não tiver chave da API, usar imagem padrão por tipo
    if (
      !UNSPLASH_ACCESS_KEY ||
      UNSPLASH_ACCESS_KEY === "YOUR_UNSPLASH_ACCESS_KEY"
    ) {
      const defaultImage = getDefaultImageByType(foodType);
      imageCache.set(cacheKey, defaultImage);
      return defaultImage;
    }

    // Fazer requisição para Unsplash
    const response = await fetch(
      `https://api.unsplash.com/search/photos?query=${encodeURIComponent(
        searchTerm
      )}&per_page=1&orientation=landscape`,
      {
        headers: {
          Authorization: `Client-ID ${UNSPLASH_ACCESS_KEY}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error("Erro na API Unsplash");
    }

    const data = await response.json();

    if (data.results && data.results.length > 0) {
      const imageUrl = data.results[0].urls.small;
      imageCache.set(cacheKey, imageUrl);
      return imageUrl;
    } else {
      // Se não encontrar imagem, usar padrão
      const defaultImage = getDefaultImageByType(foodType);
      imageCache.set(cacheKey, defaultImage);
      return defaultImage;
    }
  } catch (error) {
    console.error("Erro ao buscar imagem:", error);
    // Em caso de erro, usar imagem padrão
    const defaultImage = getDefaultImageByType(foodType);
    imageCache.set(cacheKey, defaultImage);
    return defaultImage;
  }
}

/**
 * Retorna uma imagem padrão baseada no tipo de comida (usando Unsplash Source)
 * @param {string} foodType - Tipo de comida
 * @returns {string} URL da imagem padrão
 */
function getDefaultImageByType(foodType) {
  // URLs do Unsplash Source (não precisa de API key)
  const defaultImages = {
    pizza: "https://source.unsplash.com/400x300/?pizza",
    hamburguer: "https://source.unsplash.com/400x300/?burger",
    lanche: "https://source.unsplash.com/400x300/?sandwich",
    massa: "https://source.unsplash.com/400x300/?pasta",
    japonesa: "https://source.unsplash.com/400x300/?sushi",
    mexicana: "https://source.unsplash.com/400x300/?tacos",
    churrasco: "https://source.unsplash.com/400x300/?barbecue",
    doce: "https://source.unsplash.com/400x300/?dessert",
    sorvete: "https://source.unsplash.com/400x300/?icecream",
    vegetariana: "https://source.unsplash.com/400x300/?salad",
    "frutos do mar": "https://source.unsplash.com/400x300/?seafood",
    arabe: "https://source.unsplash.com/400x300/?middleeastern",
    "comida caseira": "https://source.unsplash.com/400x300/?homecooking",
  };

  return (
    defaultImages[foodType.toLowerCase()] ||
    "https://source.unsplash.com/400x300/?food"
  );
}

/**
 * Aplica imagens automaticamente a todos os pratos na página
 */
async function applyImagesToFoodItems() {
  const foodItems = document.querySelectorAll("[data-food-type]");

  for (const item of foodItems) {
    const foodType = item.dataset.foodType;
    const foodName = item.dataset.foodName || "";

    try {
      const imageUrl = await getUnsplashImage(foodType, foodName);

      // Buscar elemento de imagem dentro do item
      const imgElement = item.querySelector("img");
      if (imgElement) {
        imgElement.src = imageUrl;
        imgElement.onerror = function () {
          // Se a imagem falhar, usar padrão
          this.src = getDefaultImageByType(foodType);
        };
      }
    } catch (error) {
      console.error("Erro ao aplicar imagem:", error);
    }
  }
}

/**
 * Busca uma imagem específica para um prato
 * @param {string} foodType - Tipo de comida
 * @param {string} foodName - Nome do prato
 * @param {HTMLImageElement} imgElement - Elemento de imagem para aplicar
 */
async function loadFoodImage(foodType, foodName, imgElement) {
  console.log(
    "DEBUG loadFoodImage: foodType=",
    foodType,
    "foodName=",
    foodName,
    "imgElement=",
    imgElement
  );
  try {
    const imageUrl = await getUnsplashImage(foodType, foodName);
    console.log("DEBUG: URL da imagem obtida:", imageUrl);
    imgElement.src = imageUrl;
    imgElement.onerror = function () {
      console.log("DEBUG: Erro ao carregar imagem, usando fallback");
      this.src = getDefaultImageByType(foodType);
    };
  } catch (error) {
    console.error("Erro ao carregar imagem:", error);
    imgElement.src = getDefaultImageByType(foodType);
  }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function () {
  applyImagesToFoodItems();
});

// Exportar funções para uso global
window.FoodImageAPI = {
  getUnsplashImage,
  getDefaultImageByType,
  applyImagesToFoodItems,
  loadFoodImage,
};
