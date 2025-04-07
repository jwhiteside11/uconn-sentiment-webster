function getURL() {
  // Split the string at "://"
  const parts = API_URL.split("://");
  // Further split the second part at ":"
  const [containerName, port] = parts[1].split(":");
  const ipv4Pattern = /^\d{1,3}(\.\d{1,3}){3}$/;
  if (ipv4Pattern.test(containerName)) {
    return API_URL
  }
  return API_URL.replace(containerName, "localhost")
}

const SEARCH_URL = `${getURL()}/search_news`

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  
  if (parts.length === 2) {
      return parts.pop().split(';').shift();  // Extracts and returns the cookie value
  }
  return null;  // Return null if the cookie doesn't exist
}

let activeQuery = "";

const monitorSearchBar = () => {
  const search_bar = document.getElementById("search-bar")
  const ticker_select = document.getElementById("ticker-select")
  activeQuery = `ticker=${ticker_select.value}&search_term=`
  
  const intervalID = setInterval(() => {
    if (activeQuery != "") {
      updateSearchResults()
      activeQuery = ""
    }
  }, 300)
  
  search_bar.oninput = (event) => {
    activeQuery = `ticker=${ticker_select.value}&search_term=${event.target.value}`
  }
  
  ticker_select.oninput = () => {
    activeQuery = `ticker=${ticker_select.value}&search_term=${search_bar.value}`
  }
}

const updateSearchResults = () => {
  const headers = {"WBS-API-PASSKEY": getCookie("WBS-API-PASSKEY")}
  console.log(headers)
  fetch(`${SEARCH_URL}?${activeQuery}`, {headers})
  .then(res => res.json() )
  .then(json => {
    console.log(json)
    const elems = []
    json["hits"].forEach(hit => {
      let outer = document.createElement('a');
      outer.href = hit["url"]
      outer.target = "_blank"
      let p1 = document.createElement('h3');
      let p2 = document.createElement('p');
      let p3 = document.createElement('div');
      p1.textContent = hit["title"];  // Set the content of the <h3> tag
      p2.textContent = `Score: ${hit["score"].toFixed(2)} Magnitude: ${hit["magnitude"].toFixed(2)}`;  // Set the content of the <p> tag
      p3.innerHTML = hit["highlights"].slice(0, 3).map(hit => `<p>${hit}</p>`).join("\n");  // Set the content of the <p> tag
      outer.appendChild(p1)
      outer.appendChild(p2)
      outer.appendChild(p3)
      elems.push(outer);
    })
    const res_box = document.getElementById("search-results")
    res_box.replaceChildren(...elems)
  })
  .catch(error => {
      console.error('Error fetching data:', error);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  monitorSearchBar()
})