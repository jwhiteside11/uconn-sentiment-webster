const DEV_AUTH_URL = "http://localhost:5100/auth";
const PROD_AUTH_URL = "http://34.44.103.189:5100/auth";
const ACTIVE_AUTH_URL = PROD_AUTH_URL;

const login = () => {
  const username = document.getElementById("username");
  const password = document.getElementById("password");

  fetch(`${ACTIVE_AUTH_URL}/authenticate/`, {
    method: 'POST',  // Specify the request method
    headers: {
      'Content-Type': 'application/json',  // Type of data being sent
    },
    body: JSON.stringify({username, password})
  })
  .then(res => res.json() )
  .then(json => {
    console.log(json)
    let now = new Date();
    now.setHours(now.getHours() + 1);
    document.cookie = `WBS-API-PASSKEY=${json.passkey}; expires=${now.toUTCString()}; path=/`
  })
  .catch(error => {
      console.error('Error fetching data:', error);
  });
}

const loginForm = document.getElementById("login");
loginForm.onsubmit = (e) => {
  // e.preventDefault()
  console.log("SUBMITTING")
  // login()
}