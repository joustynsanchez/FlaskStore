alert("Hello i´m working");
const popoverTriggerList = document.querySelectorAll(
  '[data-bs-toggle="popover"]'
);
const popoverList = [...popoverTriggerList].map(
  (popoverTriggerEl) => new bootstrap.Popover(popoverTriggerEl)
);

document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.querySelector("#search-input");
  const searchResults = document.querySelector("#search-results");

  searchInput.addEventListener("input", () => {
    const searchTerm = searchInput.value;

    if (searchTerm.trim() === "") {
      // Restablecer el contenedor de resultados si el campo de búsqueda está vacío
      searchResults.classList.add("hidden-card-result");
      searchResults.innerHTML = "";
      return;
    }

    // Realiza la solicitud AJAX al servidor Flask
    fetch("/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ searchTerm: searchTerm }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.results.length > 0) {
          // Mostrar el contenedor de resultados si hay resultados disponibles
          searchResults.classList.remove("hidden-card-result");
        } else {
          // Ocultar el contenedor de resultados si no hay resultados disponibles
          searchResults.classList.add("hidden-card-result");
        }

        // Limpiar los resultados anteriores
        const resultList = document.createElement("ul");
        resultList.classList.add("list-group", "pt-2");

        // Agregar cada resultado como un elemento de lista
        data.results.forEach((result) => {
          const listItem = document.createElement("a");
          listItem.classList.add("list-group-item");
          listItem.textContent = result.name;
          resultList.appendChild(listItem);
          listItem.href = "/searchProduct/" + result.id
        });

        // Agregar la lista de resultados al contenedor
        searchResults.appendChild(resultList);
      });
  });
});
