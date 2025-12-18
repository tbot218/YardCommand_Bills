console.log("calendar.js loaded");

document.addEventListener("DOMContentLoaded", async () => {

  // --------------------------------------------------
  // DOM references
  // --------------------------------------------------
  const calendarEl = document.getElementById("calendar");

  const titleInput = document.getElementById("title");
  const dueDateInput = document.getElementById("due_date");
  const amountInput = document.getElementById("amount");
  const notesInput = document.getElementById("notes");
  const addBtn = document.getElementById("addBtn");

  const repeatMonthly = document.getElementById("repeatMonthly");
  const repeat4Weeks = document.getElementById("repeat4Weeks");

  const modal = document.getElementById("billModal");
  const modalTitle = document.getElementById("modalTitle");
  const modalDueDate = document.getElementById("modalDueDate");
  const modalAmount = document.getElementById("modalAmount");
  const modalNotes = document.getElementById("modalNotes");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const saveModalBtn = document.getElementById("saveModalBtn");
  const removeBillBtn = document.getElementById("removeBillBtn");

  let selectedEvent = null;

  // --------------------------------------------------
  // Checkbox locking
  // --------------------------------------------------
  repeatMonthly.addEventListener("change", () => {
    if (repeatMonthly.checked) repeat4Weeks.checked = false;
  });

  repeat4Weeks.addEventListener("change", () => {
    if (repeat4Weeks.checked) repeatMonthly.checked = false;
  });

  // --------------------------------------------------
  // Calendar init
  // --------------------------------------------------
  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    height: "auto",

    eventClick: (info) => {
      selectedEvent = info.event;

      modalTitle.value = info.event.title;
      modalDueDate.value = info.event.startStr;
      modalAmount.value = info.event.extendedProps.amount || "";
      modalNotes.value = info.event.extendedProps.notes || "";

      modal.style.display = "block";
    }
  });

  calendar.render();

  // --------------------------------------------------
  // Load bills
  // --------------------------------------------------
  async function loadBills() {
    const res = await fetch("/bills");
    const bills = await res.json();

    calendar.removeAllEvents();

    bills.forEach(bill => {
      calendar.addEvent({
        id: bill.id,
        title: bill.name,
        start: bill.due_date,
        allDay: true,
        extendedProps: {
          amount: bill.amount,
          notes: bill.notes
        }
      });
    });
  }

  // --------------------------------------------------
  // Load totals (weekly + monthly)
  // --------------------------------------------------
  async function loadTotals() {
    try {
      // Weekly
      const weeklyRes = await fetch("/totals/weekly");
      const weeklyData = await weeklyRes.json();

      const weekKey = weeklyData.current_week;
      const weekTotal = weeklyData.totals?.[weekKey] ?? 0;

      const weeklyEl = document.getElementById("weekly-total");
      if (weeklyEl) {
        weeklyEl.innerText = `$${weekTotal.toFixed(2)}`;
      }

      // Monthly
      const monthlyRes = await fetch("/totals/monthly");
      const monthlyData = await monthlyRes.json();

      const monthKey = monthlyData.current_month;
      const monthTotal = monthlyData.totals?.[monthKey] ?? 0;

      const monthlyEl = document.getElementById("monthly-total");
      if (monthlyEl) {
        monthlyEl.innerText = `$${monthTotal.toFixed(2)}`;
      }

    } catch (err) {
      console.error("Failed to load totals:", err);
    }
  }

  // --------------------------------------------------
  // Initial load (order matters)
  // --------------------------------------------------
  await loadBills();
  await loadTotals();

  // --------------------------------------------------
  // Add bill
  // --------------------------------------------------
  addBtn.addEventListener("click", async () => {
    const name = titleInput.value.trim();
    const due_date = dueDateInput.value;
    const amount = parseFloat(amountInput.value);

    if (!name || !due_date || isNaN(amount)) {
      alert("Please fill in title, due date, and amount.");
      return;
    }

    const payload = {
      name,
      due_date,
      amount,
      frequency: "monthly",
      category: "business",
      gst_credit: true,
      notes: notesInput.value.trim(),
      repeat_monthly: repeatMonthly.checked,
      repeat_4weeks: repeat4Weeks.checked
    };

    const res = await fetch("/bills", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      alert("Failed to add bill.");
      return;
    }

    titleInput.value = "";
    dueDateInput.value = "";
    amountInput.value = "";
    notesInput.value = "";
    repeatMonthly.checked = false;
    repeat4Weeks.checked = false;

    await loadBills();
    await loadTotals();
  });

  // --------------------------------------------------
  // Modal controls
  // --------------------------------------------------
  closeModalBtn.addEventListener("click", () => {
    modal.style.display = "none";
    selectedEvent = null;
  });

  saveModalBtn.addEventListener("click", async () => {
    if (!selectedEvent) return;

    const payload = {
      name: modalTitle.value.trim(),
      due_date: modalDueDate.value,
      amount: parseFloat(modalAmount.value),
      notes: modalNotes.value.trim()
    };

    const res = await fetch(`/bills/${selectedEvent.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      alert("Failed to save changes.");
      return;
    }

    modal.style.display = "none";
    selectedEvent = null;

    await loadBills();
    await loadTotals();
  });

  removeBillBtn.addEventListener("click", async () => {
    if (!selectedEvent) return;
    if (!confirm("Remove this bill?")) return;

    const res = await fetch(`/bills/${selectedEvent.id}`, {
      method: "DELETE"
    });

    if (!res.ok) {
      alert("Failed to remove bill.");
      return;
    }

    modal.style.display = "none";
    selectedEvent = null;

    await loadBills();
    await loadTotals();
  });

});
