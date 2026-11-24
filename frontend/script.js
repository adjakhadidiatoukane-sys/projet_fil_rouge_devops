const API = "/api/tasks";
const list = document.getElementById("task-list");
const form = document.getElementById("task-form");
const input = document.getElementById("task-title");
const message = document.getElementById("message");

function showError(text) {
  message.textContent = text;
}

async function request(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error("Erreur " + response.status);
  }
  return response.status === 204 ? null : response.json();
}

function render(tasks) {
  list.innerHTML = "";
  for (const task of tasks) {
    const item = document.createElement("li");
    if (task.done) item.classList.add("done");

    const title = document.createElement("span");
    title.textContent = task.title;
    title.addEventListener("click", () => toggle(task.id));

    const remove = document.createElement("button");
    remove.textContent = "Supprimer";
    remove.className = "delete";
    remove.addEventListener("click", () => removeTask(task.id));

    item.append(title, remove);
    list.append(item);
  }
}

async function load() {
  try {
    render(await request(API));
    showError("");
  } catch (error) {
    showError("Impossible de charger les tâches.");
  }
}

async function toggle(id) {
  try {
    await request(API + "/" + id, { method: "PATCH" });
    load();
  } catch (error) {
    showError("Impossible de modifier la tâche.");
  }
}

async function removeTask(id) {
  try {
    await request(API + "/" + id, { method: "DELETE" });
    load();
  } catch (error) {
    showError("Impossible de supprimer la tâche.");
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await request(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: input.value }),
    });
    input.value = "";
    load();
  } catch (error) {
    showError("Impossible d'ajouter la tâche.");
  }
});

load();
