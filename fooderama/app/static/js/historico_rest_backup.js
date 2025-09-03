document.addEventListener("DOMContentLoaded", function () {
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
});
