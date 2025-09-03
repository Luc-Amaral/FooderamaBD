document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("rating").addEventListener("input", function (e) {
    var value = e.target.value;
    if (!/^[1-5]$/.test(value)) {
      e.target.value = "";
    }
  });

  // Adicionar evento onsubmit ao formulário
  const reviewForm = document.getElementById("reviewForm");
  if (reviewForm) {
    reviewForm.addEventListener("submit", function (e) {
      addDateTime();
    });
  }
});

function addDateTime() {
  const now = new Date();
  document.getElementById("date").value = now.toISOString().split("T")[0];
  document.getElementById("time").value = now.toTimeString().split(" ")[0];
}
