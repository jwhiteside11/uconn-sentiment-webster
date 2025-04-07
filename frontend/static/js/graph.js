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

class ScoreDial {
  constructor(value, text, size = 'lg') {
    this.dial = this.createDial(value, text, size)
  }

  createDial(value, text, size) {
    this.size = size
    const container = document.getElementById(`${size}-dial-container`);
    const dialArticle = document.createElement("article");
    dialArticle.className = `dial ${size}`;
    container.appendChild(dialArticle);

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    dialArticle.appendChild(svg)
    
    const svgSize = size === 'lg' ? 180 : 60;
    const svgRad = svgSize * 0.94;

    this.path = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    this.path.setAttribute("cx", svgSize);
    this.path.setAttribute("cy", svgSize);
    this.path.setAttribute("r", svgRad);
    this.path.style.fill = "none";
    this.path.style.stroke = "#eee";
    this.path.style.strokeWidth = svgSize * 0.12;
    this.path.style.strokeDasharray = 0;
    this.path.style.strokeDashoffset = 0;
    this.path.style.transition = "stroke-dashoffset 1s ease";

    const bkgd = this.path.cloneNode(true)
    svg.appendChild(bkgd)
    svg.appendChild(this.path)

    // Initialize path
    this.totalLength = 2 * Math.PI * svgRad;
    this.setPath(value);

    // this.path = document.getElementsByClassName("value-path")[0];
    const dialText = document.createElement('div')
    dialText.className = "dial-text"
    dialArticle.appendChild(dialText)

    this.scoreValue = document.createElement("p");
    this.scoreValue.textContent = value.toFixed(size === 'lg' ? 3 : 2);
    this.scoreValue.className = "score-value"
    dialText.appendChild(this.scoreValue)

    if (size === 'lg') {
      const label = document.createElement("p");
      label.textContent = text;
      label.className = "bank-name"
      dialText.appendChild(label)
    } else {
      const subtextContainer = document.createElement('div');
      subtextContainer.style.width = "148px";
      subtextContainer.style.marginLeft = "-12px";
      const subtext = document.createElement("p");
      subtext.style.textAlign = "center";
      subtext.textContent = text;

      subtextContainer.appendChild(subtext);
      dialArticle.appendChild(subtextContainer);
    }

    return dialArticle
  }

  setValue(value) {
    this.scoreValue.textContent = value.toFixed(this.size === 'lg' ? 3 : 2);
    this.setPath(value)
  }

  setPath(value) {
    // Clamp value between -1 and 1
    value = Math.max(-1, Math.min(1, value));
    // Convert -1 to 1 range to 0 to 1 for the arc
    const normalizedValue = (value + 1) / 2;
    // Calculate the dash offset based on the score
    const dashOffset = this.totalLength * (1 - normalizedValue);

    // Update the path
    this.path.style.strokeDasharray = this.totalLength; // start path at full length to hide color
    setTimeout(() => this.path.style.strokeDashoffset = dashOffset, 50) // set path to normalized value after 50ms to trigger animation
    this.path.style.strokeDashoffset = this.totalLength;
    this.path.style.stroke = this.getColor(value);
    this.path.style.transform = "rotate(90deg)"
    this.path.style.transformOrigin = "center"
  }

  getColor(value) {
    if (value <= -0.333) return "#FF4D4D"; // Red
    if (value <= 0.333) return "#F1C54B"; // Yellow
    return "#4CAF50"; // Green
  }
}

const GRAPH_URL = `${getURL()}/search_news/summary`
const otherSummaries = {}
var selectedSummary = wbsSummary;
var averages = {};
const dial1 = new ScoreDial(0.342, "Webster Bank");

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  
  if (parts.length === 2) {
      return parts.pop().split(';').shift();  // Extracts and returns the cookie value
  }
  return null;  // Return null if the cookie doesn't exist
}

const fetchSummary = async (query) => {
  const headers = {"WBS-API-PASSKEY": getCookie("WBS-API-PASSKEY")}
  return fetch(`${GRAPH_URL}?${query}`, {headers})
}

const updateSummary = () => {
  const elems = []
  selectedSummary["documents"].forEach(hit => {
    let p2 = document.createElement('p');
    // p2.textContent = `Score: ${hit["score"].toFixed(2)} Magnitude: ${hit["magnitude"].toFixed(2)}`;  // Set the content of the <p> tag
    p2.textContent = `${JSON.stringify(hit)}`
    elems.push(p2);
  });
  
  const res_box = document.getElementById("summary-results")
  res_box.replaceChildren(...elems)

  findAverages()
}

const findAverages = () => {
  const mo_totals = {};
  selectedSummary["documents"].forEach(hit => {
    const [dayow, mo_day, year, time] = hit["date"].split(",")
    key = `${mo_day.trim().substring(0, 3)} ${year.trim().substring(2)}`
    if (mo_totals[key]) {
      mo_totals[key][0] += hit["score"]
      mo_totals[key][1]++
    } else {
      mo_totals[key] = [hit["score"], 1]
    }
  });
  let total = 0
  let cnt = 0
  Object.keys(mo_totals).forEach(key => {
    total += mo_totals[key][0]
    cnt += mo_totals[key][1]
  })
  mo_totals["avg_total"] = total / cnt
  averages = mo_totals
  console.log(mo_totals)
  dial1.setValue(mo_totals["avg_total"])
}

document.addEventListener("DOMContentLoaded", () => {
  const ticker_select = document.getElementById("ticker-select")
  
  ticker_select.oninput = () => {
    const ticker = ticker_select.value;
    if (otherSummaries[ticker] !== undefined) {
      selectedSummary = otherSummaries[ticker]
      updateSummary()
    } else {
      fetchSummary(`ticker=${ticker}`)
      .then(res => res.json() )
      .then(json => {
        console.log(json)
        otherSummaries[ticker] = json
        selectedSummary = json
        updateSummary()
      })
      .catch(error => {
          console.error('Error fetching data:', error);
      });
    }
  }
})