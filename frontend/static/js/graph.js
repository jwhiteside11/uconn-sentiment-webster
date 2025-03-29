const DEV_API_URL = "http://localhost:5100/api";
const PROD_API_URL = "http://34.44.103.189:5100/api";
const ACTIVE_API_URL = PROD_API_URL;

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  
  if (parts.length === 2) {
      return parts.pop().split(';').shift();  // Extracts and returns the cookie value
  }
  return null;  // Return null if the cookie doesn't exist
}

const updateSummary = (query) => {
  const headers = {"WBS-API-PASSKEY": getCookie("WBS-API-PASSKEY")}
  fetch(`${ACTIVE_API_URL}/search_news/summary?${query}`, {headers})
  .then(res => res.json() )
  .then(json => {
    console.log(json)
    const elems = []
    json["documents"].forEach(hit => {
      let p2 = document.createElement('p');
      // p2.textContent = `Score: ${hit["score"].toFixed(2)} Magnitude: ${hit["magnitude"].toFixed(2)}`;  // Set the content of the <p> tag
      p2.textContent = `${JSON.stringify(hit)}`
      elems.push(p2);
    })
    const res_box = document.getElementById("summary-results")
    res_box.replaceChildren(...elems)
  })
  .catch(error => {
      console.error('Error fetching data:', error);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const ticker_select = document.getElementById("ticker-select")
  
  ticker_select.oninput = () => {
    updateSummary(`ticker=${ticker_select.value}`)
  }
})