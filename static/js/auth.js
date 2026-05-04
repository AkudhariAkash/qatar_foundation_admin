function toast(message) {
  const box = document.getElementById("toast");
  box.textContent = message;
  box.classList.add("show");
  setTimeout(() => box.classList.remove("show"), 2500);
}

function highlightCardFromQuery() {
  const view = new URLSearchParams(window.location.search).get("view");
  const isSignup = view === "signup";
  const targetId = isSignup ? "signupCard" : "loginCard";
  const hideId = isSignup ? "loginCard" : "signupCard";
  const target = document.getElementById(targetId);
  const hidden = document.getElementById(hideId);
  if (hidden) hidden.classList.add("hidden-view");
  if (!target) return;
  target.classList.add("active-card");
  target.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function postJSON(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

document.getElementById("signupForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const payload = Object.fromEntries(form.entries());
  const data = await postJSON("/api/signup", payload);
  toast(data.message || "Signup processed");
  if (data.status === "success") {
    e.target.reset();
  }
});

document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const payload = Object.fromEntries(form.entries());
  payload.remember = form.get("remember") === "on";
  const data = await postJSON("/api/login", payload);
  toast(data.message || "Login processed");
  if (data.status === "success") {
    window.location.href = "/dashboard";
  }
});

document.getElementById("forgotForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const payload = Object.fromEntries(form.entries());
  const data = await postJSON("/api/forgot-password", payload);
  if (data.reset_link) {
    toast("Reset link created. Redirecting...");
    window.location.href = data.reset_link;
  } else {
    toast("No reset link generated. Use a registered email.");
  }
  e.target.reset();
});

highlightCardFromQuery();
