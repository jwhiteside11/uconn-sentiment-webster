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
    this.initPath(value);

    // this.path = document.getElementsByClassName("value-path")[0];
    const dialText = document.createElement('div')
    dialText.className = "dial-text"
    dialArticle.appendChild(dialText)

    this.scoreValue = document.createElement("p");
    if (typeof(value) === "string") {
      this.scoreValue.textContent = value;
    } else {
      this.scoreValue.textContent = value.toFixed(size === 'lg' ? 3 : 2);
    }
    this.scoreValue.className = "score-value"
    dialText.appendChild(this.scoreValue)

    if (size === 'lg') {
      this.label = document.createElement("p");
      this.label.textContent = text;
      this.label.className = "bank-name"
      dialText.appendChild(this.label)
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

  setValues(value, text) {
    if (this.size === 'lg') {
      this.scoreValue.textContent = value.toFixed(3);
      this.label.textContent = text
    } else {
      this.scoreValue.textContent = value.toFixed(2);
    }
    this.setPath(value)
  }

  initPath(value) {
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

  setPath(value) {
    // Clamp value between -1 and 1
    value = Math.max(-1, Math.min(1, value));
    // Convert -1 to 1 range to 0 to 1 for the arc
    const normalizedValue = (value + 1) / 2;
    // Calculate the dash offset based on the score
    const dashOffset = this.totalLength * (1 - normalizedValue);
    // Update the path
    this.path.style.strokeDashoffset = dashOffset
    this.path.style.stroke = this.getColor(value);
  }

  getColor(value) {
    if (value <= -0.333) return "#FF4D4D"; // Red
    if (value <= 0.333) return "#F1C54B"; // Yellow
    return "#4CAF50"; // Green
  }
}

const GRAPH_URL = `${getURL()}/search_news/summary`
const otherSummaries = {}
var selectedSummary = null;
var averages = {};

const dial1 = new ScoreDial("", "");

const bankNames = {
  "FCNCA": "First Citizens BancShares, Inc.",
  "MTB": "M&T Bank Corporation",
  "HBAN": "Huntington Bancshares Inc",
  "RF": "Regions Financial corporation",
  "NYCB": "New York Community Bancorp, Inc.",
  "ZION": "Zions Bancorporation",
  "CMA": "Comerica Incorporated",
  "FHN": "First Horizon Corporation",
  "WBS": "Webster Financial Corporation",
  "WAL": "Western Alliance Bancorporation",
  "VLY": "Valley National Bancorp",
  "SNV": "Synovus Financial",
  "WTFC": "Wintrust Financial corporation",
  "CFR": "Cullen/Frost Bankers, Inc.",
  "BOKF": "BOK Financial Corporation",
  "ONB": "Old National Bancorp",
  "FNB": "F.N.B. Corporation",
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  
  if (parts.length === 2) {
      return parts.pop().split(';').shift();  // Extracts and returns the cookie value
  }
  return null;  // Return null if the cookie doesn't exist
}

// Dials

const fetchThenUpdateSummary = (ticker) => {
  const headers = {"WBS-API-PASSKEY": getCookie("WBS-API-PASSKEY")}
  fetch(`${GRAPH_URL}?ticker=${ticker}`, {headers})
  .then(res => res.json())
  .then(json => {
    console.log(json)
    otherSummaries[ticker] = json
    selectedSummary = json
    updateSummary(ticker)
  })
  .catch(error => {
      console.error('Error fetching data:', error);
  });
}

const updateSummary = (ticker) => {
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
  
  dial1.setValues(averages["avg_total"], bankNames[ticker])
}

const findAverages = () => {
  const mo_totals = {};
  selectedSummary["documents"].forEach(hit => {
    const [dayow, mo_day, year, time] = hit["date"].split(",")
    key = `${mo_day.trim().substring(0, 3)} ${year.trim().substring(2)}`
    if (mo_totals[key]) {
      mo_totals[key][0] += hit["score"]
      mo_totals[key][1] += hit["magnitude"]
    } else {
      mo_totals[key] = [hit["score"], hit["magnitude"]]
    }
  });

  let total = 0
  let cnt = 0
  Object.keys(mo_totals).forEach(key => {
    total += mo_totals[key][0]
    cnt += mo_totals[key][1]
  })

  mo_totals["avg_total"] = total / cnt
  
  console.log(mo_totals)
  averages = mo_totals
}

// Line graph

const getMonths = () => {
  let months = Array.from(Object.keys(averages)).filter(v => v !== 'avg_total')
  months.sort((a, b) => {
    const moA = a.substring(0, 3)
    const moB = b.substring(0, 3)
    const yA = a.substring(4, 6)
    const yB = b.substring(4, 6)
    if (yA < yB) {
      return -1; // a comes before b
    }
    if (yA > yB) {
      return 1; // a comes after b
    }
    if (moA < moB) {
      return -1; // a comes before b
    }
    if (moA > moB) {
      return 1; // a comes after b
    }
    return 0; // a and b are equal
  });
  console.log("MONTHS", months)
  return months
}

const makeChart = (id) => {
  const months = getMonths();

  var ctx = document.getElementById(id).getContext('2d');
  var lineChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ["Aug 24", "Sep 24", "Oct 24", "Nov 24", "Dec 24", "Jan 25"],
      datasets: [{
        label: 'Sales',
        data: [30, 45, 60, 35, 50, 40],
        borderColor: '#CEE9C3',
        borderWidth: 4,
        fill: false
      }, {
        label: 'Not Sales',
        data: [20, 15, 30, 35, 80, 35],
        borderColor: '#F8D49A',
        borderWidth: 4,
        fill: false
      }]
    },
    options: {
      plugins: {
          legend: {
              position: 'right', // Set legend position to the right
              labels: {
                  boxWidth: 20,    // Size of the box in the legend
                  padding: 15      // Padding between the legend items
              }
          }
      },
      layout: {
          padding: {
              right: 50  // Add some space on the right side to avoid clipping
          }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const ticker_select = document.getElementById("ticker-select")
  fetchThenUpdateSummary(ticker_select.value)
  setTimeout(() => makeChart('myChart'), 200)
  
  ticker_select.oninput = () => {
    const ticker = ticker_select.value;
    if (otherSummaries[ticker] !== undefined) {
      selectedSummary = otherSummaries[ticker]
      updateSummary(ticker)
    } else {
      fetchThenUpdateSummary(ticker)
    }
  }
})