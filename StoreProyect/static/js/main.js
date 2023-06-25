const searchInput = document.querySelector("#search-input");
const searchResults = document.querySelector("#search-results");

searchInput.addEventListener("input", () => {
  const searchTerm = searchInput.value;

  if (searchTerm.trim() === "") {
    // Restablecer el contenedor de resultados si el campo de búsqueda está vacío
    searchResults.innerHTML = "";
    searchResults.classList.remove('has-results');
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
      // Limpiar los resultados anteriores
      searchResults.innerHTML = "";

      if (data.results.length > 0) {
        // Crear una lista para los resultados
        const resultList = document.createElement("ul");
        resultList.classList.add("list-group", "pt-2");

        data.results.forEach((result) => {
          // Crear un elemento de lista y enlace por cada resultado
          const listItem = document.createElement("li");
          listItem.classList.add("list-group-item");

          const link = document.createElement("a");
          link.classList.add("list-group-item", "list-group-item-action", "active", "list-group-item-dark");
          link.href = "/searchProduct/" + result.id;
          link.textContent = result.name;

          listItem.appendChild(link);
          resultList.appendChild(listItem);
        });

        // Agregar la lista de resultados al contenedor
        searchResults.appendChild(resultList);

        // Mostrar el contenedor de resultados si hay resultados disponibles
        searchResults.classList.add('has-results');
      } else {
        // Ocultar el contenedor de resultados si no hay resultados disponibles
        searchResults.classList.remove('has-results');
      }
    })
    .catch((error) => {
      console.log(error);
    });
});
