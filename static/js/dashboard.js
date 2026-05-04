const form = document.getElementById("opportunityForm");
const rows = document.getElementById("opportunityRows");
const title = document.getElementById("formTitle");

function toast(message) {
  const box = document.getElementById("toast");
  box.textContent = message;
  box.classList.add("show");
  setTimeout(() => box.classList.remove("show"), 2500);
}

function resetForm() {
  form.reset();
  form.id.value = "";
  title.textContent = "Add Opportunity";
}

function bindEditDelete() {
  document.querySelectorAll("[data-edit]").forEach((btn) => {
    btn.onclick = async () => {
      const id = btn.getAttribute("data-edit");
      const res = await fetch(`/api/opportunities/${id}`);
      const data = await res.json();
      if (data.status !== "success") {
        toast(data.message || "Failed to load");
        return;
      }
      const op = data.data;
      form.id.value = op.id;
      form.name.value = op.name;
      form.duration.value = op.duration;
      form.start_date.value = op.start_date;
      form.description.value = op.description;
      form.skills.value = op.skills;
      form.category.value = op.category;
      form.max_applicants.value = op.max_applicants;
      form.future_opportunities.checked = op.future_opportunities;
      title.textContent = "Edit Opportunity";
      window.scrollTo({ top: 0, behavior: "smooth" });
    };
  });

  document.querySelectorAll("[data-delete]").forEach((btn) => {
    btn.onclick = async () => {
      const id = btn.getAttribute("data-delete");
      const res = await fetch(`/api/opportunities/${id}`, { method: "DELETE" });
      const data = await res.json();
      toast(data.message || "Deleted");
      if (data.status === "success") {
        loadOpportunities();
      }
    };
  });
}

async function loadOpportunities() {
  const res = await fetch("/api/opportunities");
  const data = await res.json();

  if (data.status !== "success") {
    rows.innerHTML = "<tr><td colspan='5'>Failed to load opportunities.</td></tr>";
    return;
  }

  if (!data.data.length) {
    rows.innerHTML = "<tr><td colspan='5'>No opportunities created yet.</td></tr>";
    return;
  }

  rows.innerHTML = data.data.map((op) => `
    <tr>
      <td>${op.name}</td>
      <td>${op.category}</td>
      <td>${op.start_date}</td>
      <td>${op.max_applicants}</td>
      <td>
        <button class="btn secondary" data-edit="${op.id}">Edit</button>
        <button class="btn danger" data-delete="${op.id}">Delete</button>
      </td>
    </tr>
  `).join("");

  bindEditDelete();
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    name: form.name.value,
    duration: form.duration.value,
    start_date: form.start_date.value,
    description: form.description.value,
    skills: form.skills.value,
    category: form.category.value,
    max_applicants: form.max_applicants.value,
    future_opportunities: form.future_opportunities.checked,
  };

  const editId = form.id.value;
  const url = editId ? `/api/opportunities/${editId}` : "/api/opportunities";
  const method = editId ? "PUT" : "POST";

  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();

  if (data.status === "success") {
    toast(editId ? "Updated successfully" : "Created successfully");
    resetForm();
    loadOpportunities();
  } else {
    toast(data.message || (data.errors ? data.errors.join(", ") : "Request failed"));
  }
});

document.getElementById("cancelEdit").addEventListener("click", resetForm);
document.getElementById("logoutBtn").addEventListener("click", async () => {
  const res = await fetch("/api/logout", { method: "POST" });
  const data = await res.json();
  toast(data.message || "Logged out");
  if (data.status === "success") {
    window.location.href = "/login";
  }
});

loadOpportunities();
