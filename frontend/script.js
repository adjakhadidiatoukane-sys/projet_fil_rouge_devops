const TOKEN_KEY = "token";

const $ = (id) => document.getElementById(id);
const message = $("message");

function show(text, type) {
  message.textContent = text;
  message.className = type || "";
}

async function api(path, method, body, withToken) {
  const headers = { "Content-Type": "application/json" };
  if (withToken) headers.Authorization = "Bearer " + sessionStorage.getItem(TOKEN_KEY);
  const response = await fetch("/api" + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.error || "Erreur " + response.status);
    error.status = response.status;
    throw error;
  }
  return data;
}

function showProfile(profile) {
  $("auth").hidden = true;
  $("profile").hidden = false;
  $("profile-email").textContent = profile.email;
  $("profile-created").textContent = profile.created_at;
  $("profile-name").value = profile.full_name;
  $("profile-bio").value = profile.bio;
}

function showAuth() {
  sessionStorage.removeItem(TOKEN_KEY);
  $("profile").hidden = true;
  $("auth").hidden = false;
}

async function loadProfile() {
  if (!sessionStorage.getItem(TOKEN_KEY)) return showAuth();
  try {
    showProfile(await api("/profile", "GET", null, true));
  } catch (error) {
    showAuth();
    show(error.message, "error");
  }
}

$("register-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const data = await api("/register", "POST", {
      full_name: $("register-name").value,
      email: $("register-email").value,
      password: $("register-password").value,
    });
    $("register-form").reset();
    show(data.message, "ok");
  } catch (error) {
    show(error.message, "error");
  }
});

$("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const data = await api("/login", "POST", {
      email: $("login-email").value,
      password: $("login-password").value,
    });
    sessionStorage.setItem(TOKEN_KEY, data.token);
    $("login-form").reset();
    show("", "");
    loadProfile();
  } catch (error) {
    show(error.message, "error");
  }
});

$("profile-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const profile = await api("/profile", "PUT", {
      full_name: $("profile-name").value,
      bio: $("profile-bio").value,
    }, true);
    showProfile(profile);
    show("Profil mis à jour.", "ok");
  } catch (error) {
    if (error.status === 401) showAuth();
    show(error.message, "error");
  }
});

$("logout").addEventListener("click", () => {
  showAuth();
  show("Vous êtes déconnecté.", "ok");
});

loadProfile();
