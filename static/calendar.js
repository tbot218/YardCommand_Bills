document.addEventListener("DOMContentLoaded", async () => {

  // --------------------------------------------------
  // Elements
  // --------------------------------------------------
  const calEl = document.getElementById("calendar");
  const addBtn = document.getElementById("addBtn");

  const modal = document.getElementById("billModal");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const saveModalBtn = document.getElementById("saveModalBtn");
  const removeBillBtn = document.getElementById("removeBillBtn");

  // --------------------------------------------------
  // State
  // --------------------------------------------------
  let activeBillId = null;

  // --------------------------------------------------
  // Helpers
  // --------------------------------------------------
  function normalizeDate(dateStr) {
    if (!dateStr) return null;
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;

    const parts = dateStr.split("/");
    if (parts.length === 3) {
      const [dd, mm, yyyy] = parts;
      return `${yyyy}-${mm.padStart(2, "0")}-${dd.padStart(2, "0")}`;
    }
    return dateStr;
  }

  async function fetchBills() {
    const res = await fetch("/bills");
    if (!res.ok) throw new Error("Failed to fetch bills");
    return await res.json();
  }

  function billsToEvents(bills) {
    return bills.map(b => ({
      id: String(b.id),
      title: b.amount ? `${b.name} ($${b.amount})` : b.name,
      start: b.due_date,
      allDay: true,
      extendedProps: { ...b }
    }));
  }

  // --------------------------------------------------
  // Calendar
  // --------------------------------------------------
  const calendar = new FullCalendar.Calendar(calEl, {
    initialView: "dayGridMonth",
    height: "auto",
    events: [],

    eventClick: (info) => {
      const b = info.event.extendedProps;

      activeBillId = info.event.id;

      document.getElementById("modalTitle").value = b.name || "";
      document.getElementById("modalDueDate").value = b.due_date || "";
      document.getElementById("modalAmount").value = b.amount ?? "";
      document.getElementById("modalNotes").value = b.notes || "";

      modal.style.display = "block";
    }
  });

  calendar.render();

  async function refreshCalendar() {
    const bills = await fetchBills();
    calendar.removeAllEvents();
    calendar.addEventSource(billsToEvents(bills));
  }

  // --------------------------------------------------
  // Add Bill (POST)
  // --------------------------------------------------
  addBtn.addEventListener("click", async () => {
    const payload = {
      name: document.getElementById("title").value.trim(),
      due_date: normalizeDate(document.getElementById("due_date").value),
      amount: parseFloat(document.getElementById("amount").value),
      frequency: "monthly",
      category: "business",
      gst_credit: true,
      notes: document.getElementById("notes").value.trim()
    };

    if (!payload.name || !payload.due_date) {
      alert("Name and due date are required");
      return;
    }

    const res = await fetch("/bills", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      alert(await res.text());
      return;
    }

    await refreshCalendar();
  });

  // --------------------------------------------------
  // Save Bill (PUT)
  // --------------------------------------------------
  saveModalBtn.addEventListener("click", async () => {
    if (!activeBillId) return;

    const payload = {
      name: document.getElementById("modalTitle").value.trim(),
      due_date: normalizeDate(document.getElementById("modalDueDate").value),
      amount: parseFloat(document.getElementById("modalAmount").value),
      notes: document.getElementById("modalNotes").value.trim()
    };

    const res = await fetch(`/bills/${activeBillId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      alert("Save failed:\n" + await res.text());
      return;
    }

    modal.style.display = "none";
    activeBillId = null;
    await refreshCalendar();
  });

  // --------------------------------------------------
  // Remove Bill (DELETE)
  // --------------------------------------------------
  removeBillBtn.addEventListener("click", async () => {
    if (!activeBillId) return;

    if (!confirm("Are you sure you want to remove this bill?")) return;

    const res = await fetch(`/bills/${activeBillId}`, {
      method: "DELETE"
    });

    if (!res.ok) {
      alert("Remove failed");
      return;
    }

    modal.style.display = "none";
    activeBillId = null;
    await refreshCalendar();
  });

  // --------------------------------------------------
  // Close Modal
  // --------------------------------------------------
  closeModalBtn.addEventListener("click", () => {
    modal.style.display = "none";
    activeBillId = null;
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
      activeBillId = null;
    }
  });

  // --------------------------------------------------
  // Initial load
  // --------------------------------------------------
  await refreshCalendar();
});
