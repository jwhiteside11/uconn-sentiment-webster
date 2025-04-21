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
      this.label = document.createElement("p");
      this.label.style.textAlign = "center";
      this.label.textContent = text;

      subtextContainer.appendChild(this.label);
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
var selectedAverages = null;
var averages = {};
var category_averages = {};

// Initialize the dials
const dial1 = new ScoreDial("", "");
const dial2 = new ScoreDial(0.751, "Customer Service", 'sm');
const dial3 = new ScoreDial(0.151, "Financial Performance", 'sm');
const dial4 = new ScoreDial(-0.851, "Leadership", 'sm');
const dial5 = new ScoreDial(-0.151, "Risk Management and Compliance", 'sm');

const categories = [
  "Customer Service",
  "Financial Performance",
  "Risk Management and Compliance",
  "Corporate Social Responsibility",
  "Leadership",
  "Technology",
]

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

const fetchThenUpdateSummary = async (chart, ticker) => {
  const headers = {"WBS-API-PASSKEY": getCookie("WBS-API-PASSKEY")}
  var chartRes = null;
  try {
    const res = await fetch(`${GRAPH_URL}?ticker=${ticker}`, {headers})
    const json = await res.json()
    console.log(json)
    otherSummaries[ticker] = json
    selectedSummary = json
    selectedAverages = {}
    chartRes = updateSummary(chart, ticker)
  } catch (error) {
      console.error('Error fetching data:', error);
  };
  return chartRes
}

const updateSummary = (chart, ticker) => {
  const elems = []
  selectedSummary["documents"].forEach(hit => {
    let p2 = document.createElement('pre');
    // p2.textContent = `Score: ${hit["score"].toFixed(2)} Magnitude: ${hit["magnitude"].toFixed(2)}`;  // Set the content of the <p> tag
    hit["keywords"] = typeof(hit["keywords"]) === "string" ? JSON.parse(hit["keywords"]) : hit["keywords"]
    p2.textContent = `${JSON.stringify(hit, null, 2)}`
    elems.push(p2);
  });
  
  const res_box = document.getElementById("summary-results")
  res_box.replaceChildren(...elems)

  findAverages(ticker)
  
  dial1.setValues(averages[ticker]["totals"]["avg_total"], bankNames[ticker])
  dial2.setValues(selectedAverages[dial2.label.textContent]["avg_total"])
  dial3.setValues(selectedAverages[dial3.label.textContent]["avg_total"])
  dial4.setValues(selectedAverages[dial4.label.textContent]["avg_total"])
  dial5.setValues(selectedAverages[dial5.label.textContent]["avg_total"])

  if (chart) {
    chart.destroy()
  }
  return makeChart('myChart')
}

const findAverages = (ticker) => {
  const mo_totals = {};
  selectedAverages = {};
  categories.forEach(cat => selectedAverages[cat] = {weighted_score: 0, magnitude: 0})

  selectedSummary["documents"].forEach(hit => {
    const [dayow, mo_day, year, time] = hit["date"].split(",")
    key = `${mo_day.trim().substring(0, 3)} ${year.trim().substring(2)}`
    if (mo_totals[key]) {
      mo_totals[key][0] += hit["weighted_score"]
      mo_totals[key][1] += hit["magnitude"]
    } else {
      mo_totals[key] = [hit["weighted_score"], hit["magnitude"]]
    }
    const keywords = typeof(hit["keywords"]) === "string" ? JSON.parse(hit["keywords"]) : hit["keywords"]
    for (let cat in keywords) {
      selectedAverages[cat]["weighted_score"] += keywords[cat]["weighted_score"]
      selectedAverages[cat]["magnitude"] += keywords[cat]["magnitude"]
    }
  });

  categories.forEach(cat => {
    if (selectedAverages[cat]["magnitude"] === 0) {
      selectedAverages[cat]["avg_total"] = 0
    } else {
      selectedAverages[cat]["avg_total"] = selectedAverages[cat]["weighted_score"] / selectedAverages[cat]["magnitude"];
    }
  });

  selectedAverages["by_month"] = mo_totals
  category_averages[ticker] = selectedAverages
  // console.log(category_averages);

  let total = 0
  let cnt = 0
  Object.keys(mo_totals).forEach(key => {
    total += mo_totals[key][0]
    cnt += mo_totals[key][1]
  })

  mo_totals["totals"] = {
    "avg_total": total / cnt,
    "weighted_total": total,
    "total_magnitude": cnt,
  }
  
  // console.log(mo_totals)
  averages[ticker] = mo_totals
}

// Line graph

const monthMap = { "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12 };

const getMonths = () => {
  const allMonths = {}
  for (let ticker in averages) {
    allMonths[ticker] = Array.from(Object.keys(averages[ticker])).filter(v => v !== 'totals')
  }

  allMonths["combined"] = new Set()
  for (let ticker in allMonths) {
    allMonths["combined"] = new Set([...allMonths["combined"], ...allMonths[ticker]])
  }

  allMonths["combined"] = [...allMonths["combined"]]

  allMonths["combined"].sort((a, b) => {
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
    if (monthMap[moA] < monthMap[moB]) {
      return -1; // a comes before b
    }
    if (monthMap[moA] > monthMap[moB]) {
      return 1; // a comes after b
    }
    return 0; // a and b are equal
  });

  console.log("MONTHS", allMonths)
  return allMonths
}

const lineGraphColors = [
  "#3366CC", // Blue
  "#DC3912", // Red
  "#FF9900", // Orange
  "#109618", // Green
  "#990099", // Purple
  "#3B3EAC", // Indigo
  "#0099C6", // Cyan
  "#DD4477", // Pink
  "#66AA00", // Lime Green
  "#B82E2E"  // Dark Red
];

const makeChart = (id) => {
  const months = getMonths();
  const datasets = []
  let i = 0;
  for (let ticker in category_averages) {
    const data = []
    for (let mkey of months[ticker]) {
      // console.log(mkey, category_averages[ticker]["by_month"])
      if (mkey in category_averages[ticker]["by_month"]) {
        data.push(category_averages[ticker]["by_month"][mkey][0] / category_averages[ticker]["by_month"][mkey][1])
      } else {
        data.push(null)
      }
    }
    datasets.push({
      label: ticker,
      data,
      borderColor: lineGraphColors[i],
      borderWidth: 4,
      fill: false
    })
    i++
  }
  // console.log("datasets", datasets)
  var ctx = document.getElementById(id).getContext('2d');
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: months["combined"],
      datasets
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
          min: -1,
          max: 1,
        }
      }
    }
  });
}

var chart = null;

document.addEventListener("DOMContentLoaded", async () => {
  const ticker_select = document.getElementById("ticker-select")
  chart = await fetchThenUpdateSummary(chart, ticker_select.value)
  
  ticker_select.oninput = async () => {
    const ticker = ticker_select.value;
    if (otherSummaries[ticker] !== undefined) {
      selectedSummary = otherSummaries[ticker]
      selectedAverages = category_averages[ticker]
      chart = updateSummary(chart, ticker)
    } else {
      chart = await fetchThenUpdateSummary(chart, ticker)
    }
  }
})