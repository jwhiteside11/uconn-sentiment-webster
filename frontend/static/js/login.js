const login = () => {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  fetch("/login", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password })
  })
    .then(res => res.json())
    .then(json => {
      if (json.success) {
        window.location.href = "/graph_news";
      } else {
        alert("Login failed.");
      }
    })
    .catch(error => {
      console.error("Login error:", error);
    });
};

document.getElementById("login").onsubmit = (e) => {
  e.preventDefault();
  login();
};


const loginForm = document.getElementById("login");
loginForm.onsubmit = (e) => {
  // e.preventDefault()
  console.log("SUBMITTING")
  // login()
}