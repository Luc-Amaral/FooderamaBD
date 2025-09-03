// Recupera o parâmetro de consulta 'food-type'
const urlParams = new URLSearchParams(window.location.search);
const foodType = urlParams.get("food-type");
