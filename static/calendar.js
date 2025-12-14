let calendar = null;

document.addEventListener("DOMContentLoaded", () => {
    const calendarEl = document.getElementById("calendar");

    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        events: fetchBills
    });

    calendar.render();
});

function fetchBills(fetchInfo, successCallback) {
    fetch("/bills")
        .then(r => r.json())
        .then(bills => {
            successCallback(
                bills.map(b => ({
                    title: `${b.name} ($${b.amount})`,
                    start: b.due_date
                }))
            );
        });
}

function openModal() {
    document.getElementById("billModal").style.display = "block";
}

function closeModal() {
    document.getElementById("billModal").style.display = "none";
}

function submitBill() {
    fetch("/bills", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            name: document.getElementById("bill-name").value,
            due_date: document.getElementById("bill-date").value,
            amount: document.getElementById("bill-amount").value,
            frequency: "once",
            category: "general",
            gst_credit: false
        })
    }).then(() => {
        closeModal();
        calendar.refetchEvents();
    });
}
document.addEventListener("DOMContentLoaded", async () => {
  const calEl = document.getElementById("calendar");
  const addBtn = document.getElementById("addBtn");

  const modal = document.getElementById("billModal");
  const closeModalBtn = document.getElementById("closeModalBtn");

  async function fetchBills() {
    const res = await fetch("/bills");
    if (!res.ok) throw new Error("Failed to fetch bills");
    return await res.json();
  }

  function billsToEvents(bills) {
    return bills.map(b => ({
      id: String(b.id),
      title: b.amount ? `${b.title} ($${b.amount})` : b.title,
      start: b.due_date,
      allDay: true,
      extendedProps: {
        title: b.title,
        due_date: b.due_date,
        amount: b.amount,
        notes: b.notes
      }
    }));
  }

  const calendar = new FullCalendar.Calendar(calEl, {
    initialView: "dayGridMonth",
    height: "auto",
    events: [],

    eventClick: function(info) {
      const p = info.event.extendedProps;

      document.getElementById("modalTitle").value = p.title || "";
      document.getElementById("modalDueDate").value = p.due_date || "";
      document.getElementById("modalAmount").value = p.amount || "";
      document.getElementById("modalNotes").value = p.notes || "";

      modal.style.display = "block";
    }
  });

  calendar.render();

  async function refreshCalendar() {
    const bills = await fetchBills();
    calendar.removeAllEvents();
    calendar.addEventSource(billsToEvents(bills));
  }

  addBtn.addEventListener("click", async () => {
    const title = document.getElementById("title").value.trim();
    const due_date = document.getElementById("due_date").value;
    const amount = document.getElementById("amount").value.trim() || null;
    const notes = document.getElementById("notes").value.trim() || null;

    if (!title || !due_date) {
      alert("Title and due date required");
      return;
    }

    const res = await fetch("/bills", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, due_date, amount, notes })
    });

    if (!res.ok) {
      alert("Failed to add bill");
      return;
    }

    document.getElementById("title").value = "";
    document.getElementById("due_date").value = "";
    document.getElementById("amount").value = "";
    document.getElementById("notes").value = "";

    await refreshCalendar();
  });

  closeModalBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });

  await refreshCalendar();
});
