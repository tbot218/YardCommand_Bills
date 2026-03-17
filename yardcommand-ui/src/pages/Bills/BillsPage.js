import { useEffect, useMemo, useState } from "react";

import billsApi from "../../api/billsApi";
import styles from "./BillsPage.module.css";

const weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const yearMonthNames = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

function getMonthStart(date) {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

function isoDate(date) {
  return date.toISOString().slice(0, 10);
}

function parseIsoDate(value) {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day);
}

function formatMonth(date) {
  return new Intl.DateTimeFormat("en-AU", {
    month: "long",
    year: "numeric",
  }).format(date);
}

function formatCurrency(amount) {
  return new Intl.NumberFormat("en-AU", {
    style: "currency",
    currency: "AUD",
    maximumFractionDigits: 2,
  }).format(amount);
}

function addMonthsClamped(date, monthCount) {
  const target = new Date(date.getFullYear(), date.getMonth() + monthCount, 1);
  const lastDay = new Date(target.getFullYear(), target.getMonth() + 1, 0).getDate();
  target.setDate(Math.min(date.getDate(), lastDay));
  return target;
}

function addDays(date, dayCount) {
  const next = new Date(date);
  next.setDate(next.getDate() + dayCount);
  return next;
}

function buildRepeatedDates(startDate, repeatMode) {
  const dates = [startDate];

  if (repeatMode === "monthly") {
    for (let index = 1; index < 12; index += 1) {
      dates.push(addMonthsClamped(startDate, index));
    }
  }

  if (repeatMode === "fourWeeks") {
    for (let index = 1; index < 13; index += 1) {
      dates.push(addDays(startDate, index * 28));
    }
  }

  return dates;
}

function buildCalendarDays(activeMonth, billsByDate, todayKey) {
  const firstDay = getMonthStart(activeMonth);
  const startOffset = (firstDay.getDay() + 6) % 7;
  const gridStart = new Date(firstDay);
  gridStart.setDate(firstDay.getDate() - startOffset);

  return Array.from({ length: 42 }, (_, index) => {
    const date = new Date(gridStart);
    date.setDate(gridStart.getDate() + index);
    const key = isoDate(date);

    return {
      key,
      date,
      inMonth: date.getMonth() === activeMonth.getMonth(),
      bills: billsByDate[key] || [],
      isToday: key === todayKey,
    };
  });
}

function buildMiniMonth(year, monthIndex, billsByDate, todayKey) {
  const firstDay = new Date(year, monthIndex, 1);
  const startOffset = (firstDay.getDay() + 6) % 7;
  const daysInMonth = new Date(year, monthIndex + 1, 0).getDate();
  const totalCells = Math.ceil((startOffset + daysInMonth) / 7) * 7;

  return Array.from({ length: totalCells }, (_, index) => {
    const dayNumber = index - startOffset + 1;
    if (dayNumber < 1 || dayNumber > daysInMonth) {
      return null;
    }

    const key = isoDate(new Date(year, monthIndex, dayNumber));
    return {
      key,
      dayNumber,
      hasBills: Boolean(billsByDate[key]?.length),
      isToday: key === todayKey,
    };
  });
}

function BillsPage() {
  const today = new Date();
  const todayKey = isoDate(today);
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [viewMode, setViewMode] = useState("year");
  const [activeMonth, setActiveMonth] = useState(getMonthStart(today));
  const [selectedDate, setSelectedDate] = useState(isoDate(today));
  const [editForms, setEditForms] = useState({});
  const [editingBillId, setEditingBillId] = useState(null);
  const [form, setForm] = useState({
    title: "",
    amount: "",
    due_date: isoDate(today),
    description: "",
    repeatMonthly: false,
    repeatEveryFourWeeks: false,
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const response = await billsApi.getAll();
      setBills(response.data);
    } catch (err) {
      console.error(err);
      setError("Could not load bills data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const billsByDate = useMemo(
    () =>
      bills.reduce((grouped, bill) => {
        grouped[bill.due_date] = grouped[bill.due_date] || [];
        grouped[bill.due_date].push(bill);
        return grouped;
      }, {}),
    [bills]
  );

  const calendarDays = useMemo(
    () => buildCalendarDays(activeMonth, billsByDate, todayKey),
    [activeMonth, billsByDate, todayKey]
  );

  const monthlyBills = useMemo(() => {
    const prefix = `${activeMonth.getFullYear()}-${String(activeMonth.getMonth() + 1).padStart(2, "0")}`;
    return bills.filter((bill) => bill.due_date.startsWith(prefix));
  }, [activeMonth, bills]);

  const monthlyTotal = monthlyBills.reduce((sum, bill) => sum + bill.amount, 0);
  const selectedBills = useMemo(() => billsByDate[selectedDate] || [], [billsByDate, selectedDate]);

  useEffect(() => {
    setEditForms(
      selectedBills.reduce((forms, bill) => {
        forms[bill.id] = {
          title: bill.title,
          amount: String(bill.amount),
          due_date: bill.due_date,
          description: bill.description || "",
          status: bill.status,
        };
        return forms;
      }, {})
    );
  }, [selectedBills]);

  const miniMonths = useMemo(
    () =>
      yearMonthNames.map((label, monthIndex) => ({
        label,
        monthIndex,
        cells: buildMiniMonth(activeMonth.getFullYear(), monthIndex, billsByDate, todayKey),
        total: bills
          .filter((bill) =>
            bill.due_date.startsWith(
              `${activeMonth.getFullYear()}-${String(monthIndex + 1).padStart(2, "0")}`
            )
          )
          .reduce((sum, bill) => sum + bill.amount, 0),
      })),
    [activeMonth, bills, billsByDate, todayKey]
  );

  const handleChange = (event) => {
    const { name, value, checked, type } = event.target;

    if (name === "repeatMonthly") {
      setForm((current) => ({
        ...current,
        repeatMonthly: checked,
        repeatEveryFourWeeks: checked ? false : current.repeatEveryFourWeeks,
      }));
      return;
    }

    if (name === "repeatEveryFourWeeks") {
      setForm((current) => ({
        ...current,
        repeatEveryFourWeeks: checked,
        repeatMonthly: checked ? false : current.repeatMonthly,
      }));
      return;
    }

    setForm((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError("");

    const repeatMode = form.repeatMonthly
      ? "monthly"
      : form.repeatEveryFourWeeks
        ? "fourWeeks"
        : null;

    const dueDates = buildRepeatedDates(parseIsoDate(form.due_date), repeatMode);

    try {
      await Promise.all(
        dueDates.map((dueDate) =>
          billsApi.create({
            title: form.title,
            amount: Number(form.amount),
            due_date: isoDate(dueDate),
            issue_date: isoDate(dueDate),
            description: form.description,
            status: "draft",
          })
        )
      );

      await loadData();
      setActiveMonth(getMonthStart(parseIsoDate(form.due_date)));
      setSelectedDate(form.due_date);
      setViewMode("month");
      setForm({
        title: "",
        amount: "",
        due_date: isoDate(today),
        description: "",
        repeatMonthly: false,
        repeatEveryFourWeeks: false,
      });
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Could not create bill.");
    } finally {
      setSaving(false);
    }
  };

  const handleEditChange = (billId, event) => {
    const { name, value } = event.target;
    setEditForms((current) => ({
      ...current,
      [billId]: {
        ...current[billId],
        [name]: value,
      },
    }));
  };

  const handleSaveBill = async (billId) => {
    const payload = editForms[billId];
    if (!payload) {
      return;
    }

    setEditingBillId(billId);
    setError("");

    try {
      await billsApi.update(billId, {
        title: payload.title,
        amount: Number(payload.amount),
        due_date: payload.due_date,
        issue_date: payload.due_date,
        description: payload.description,
        status: payload.status,
      });
      await loadData();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Could not save bill changes.");
    } finally {
      setEditingBillId(null);
    }
  };

  const shiftMonth = (direction) => {
    setActiveMonth((current) => new Date(current.getFullYear(), current.getMonth() + direction, 1));
  };

  const shiftYear = (direction) => {
    setActiveMonth((current) => new Date(current.getFullYear() + direction, current.getMonth(), 1));
  };

  const currentMonthIndex = today.getMonth();
  const currentYear = today.getFullYear();

  return (
    <div className={styles.page}>
      <div className={styles.scanLines} />

      <header className={styles.hero}>
        <div className={styles.heroCopy}>
          <p className={styles.kicker}>Yard Command</p>
          <h1>Bills Calendar</h1>
        </div>

        <div className={styles.totalModule}>
          <span className={styles.totalLabel}>Selected Month Total</span>
          <strong className={styles.totalValue}>{formatCurrency(monthlyTotal)}</strong>
          <div className={styles.totalGlow} />
        </div>
      </header>

      {error && <div className={styles.error}>{error}</div>}

      {viewMode === "year" ? (
        <section className={styles.yearScene}>
          <div className={styles.yearTopBar}>
            <button type="button" className={styles.navButton} onClick={() => shiftYear(-1)}>
              Prev Year
            </button>
            <div className={styles.yearCore}>
              <span className={styles.yearCaption}>Annual Calendar</span>
              <strong>{activeMonth.getFullYear()}</strong>
            </div>
            <button type="button" className={styles.navButton} onClick={() => shiftYear(1)}>
              Next Year
            </button>
          </div>

          <div className={styles.yearScroll}>
            {miniMonths.map((month) => {
              const isCurrentMonth =
                month.monthIndex === currentMonthIndex &&
                activeMonth.getFullYear() === currentYear;
              const distance = Math.abs(month.monthIndex - activeMonth.getMonth());
              const sizeClass =
                distance === 0
                  ? styles.monthCardFocused
                  : distance === 1
                    ? styles.monthCardNear
                    : styles.monthCardFar;

              return (
                <button
                  key={month.label}
                  type="button"
                  className={`${styles.monthCard} ${sizeClass} ${isCurrentMonth ? styles.monthCurrent : ""}`}
                  onClick={() => {
                    const nextMonth = new Date(activeMonth.getFullYear(), month.monthIndex, 1);
                    setActiveMonth(nextMonth);
                    setSelectedDate(isoDate(nextMonth));
                    setViewMode("month");
                  }}
                >
                  <div className={styles.monthCardHeader}>
                    <span>{month.label}</span>
                    <strong>{formatCurrency(month.total)}</strong>
                  </div>

                  <div className={styles.miniWeekdays}>
                    {["M", "T", "W", "T", "F", "S", "S"].map((day, index) => (
                      <span key={`${month.label}-${index}`}>{day}</span>
                    ))}
                  </div>

                  <div className={styles.miniGrid}>
                    {month.cells.map((cell, index) =>
                      cell ? (
                        <span
                          key={cell.key}
                          className={`${styles.miniDay} ${cell.hasBills ? styles.miniDayHot : ""}`}
                        >
                          <span className={cell.isToday ? styles.todayBadge : ""}>{cell.dayNumber}</span>
                        </span>
                      ) : (
                        <span key={`${month.label}-blank-${index}`} className={styles.miniBlank} />
                      )
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </section>
      ) : viewMode === "month" ? (
        <section className={styles.monthScene}>
          <div className={styles.monthTopBar}>
            <div className={styles.monthNavCluster}>
              <button type="button" className={styles.navButton} onClick={() => setViewMode("year")}>
                Back to Year
              </button>
              <button type="button" className={styles.navButton} onClick={() => shiftMonth(-1)}>
                Prev Month
              </button>
              <button type="button" className={styles.navButton} onClick={() => shiftMonth(1)}>
                Next Month
              </button>
            </div>

            <div className={styles.monthTitle}>
              <span className={styles.yearCaption}>Monthly Calendar</span>
              <strong>{formatMonth(activeMonth)}</strong>
            </div>
          </div>

          <div className={styles.weekdays}>
            {weekdays.map((weekday) => (
              <span key={weekday}>{weekday}</span>
            ))}
          </div>

          {loading ? (
            <div className={styles.loading}>Loading monthly grid...</div>
          ) : (
            <div className={styles.calendarGrid}>
              {calendarDays.map((day) => (
                <button
                  key={day.key}
                  type="button"
                  className={`${styles.dayCell} ${!day.inMonth ? styles.dayMuted : ""} ${
                    day.key === selectedDate ? styles.daySelected : ""
                  } ${day.bills.length > 0 ? styles.dayHasBills : ""} ${day.isToday ? styles.dayToday : ""}`}
                  onClick={() => {
                    setSelectedDate(day.key);
                    setViewMode("day");
                  }}
                >
                  <div className={styles.dayHead}>
                    <span className={day.isToday ? styles.todayBadge : ""}>{day.date.getDate()}</span>
                    {day.bills.length > 0 && <span className={styles.billCount}>{day.bills.length}</span>}
                  </div>

                  <div className={styles.monthBillList}>
                    {day.bills.slice(0, 4).map((bill) => (
                      <div key={bill.id} className={styles.monthBillItem}>
                        <span className={styles.monthBillTitle}>{bill.title}</span>
                        <span>{formatCurrency(bill.amount)}</span>
                      </div>
                    ))}
                  </div>
                </button>
              ))}
            </div>
          )}

          <div className={styles.lowerPanels}>
            <div className={styles.dayPanel}>
              <p className={styles.kicker}>Selected Date</p>
              <h2>
                <span className={selectedDate === todayKey ? styles.todayBadge : ""}>{selectedDate}</span>
              </h2>
              {selectedBills.length === 0 ? (
                <p className={styles.emptyText}>No bills on this date yet.</p>
              ) : (
                <div className={styles.selectedList}>
                  {selectedBills.map((bill) => (
                    <article key={bill.id} className={styles.selectedCard}>
                      <strong>{bill.title}</strong>
                      <span>{formatCurrency(bill.amount)}</span>
                      {bill.description && <p>{bill.description}</p>}
                    </article>
                  ))}
                </div>
              )}
            </div>

            <div className={styles.formPanel}>
              <p className={styles.kicker}>Bills Insert</p>
              <h2>Add to Calendar</h2>

              <form onSubmit={handleSubmit} className={styles.form}>
                <input
                  name="title"
                  value={form.title}
                  onChange={handleChange}
                  className={styles.input}
                  placeholder="Bill title"
                  required
                />

                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  name="amount"
                  value={form.amount}
                  onChange={handleChange}
                  className={styles.input}
                  placeholder="Amount"
                  required
                />

                <input
                  type="date"
                  name="due_date"
                  value={form.due_date}
                  onChange={handleChange}
                  className={styles.input}
                  required
                />

                <textarea
                  name="description"
                  value={form.description}
                  onChange={handleChange}
                  className={styles.textarea}
                  placeholder="Notes"
                />

                <div className={styles.repeatPanel}>
                  <label className={styles.checkboxRow}>
                    <input
                      type="checkbox"
                      name="repeatMonthly"
                      checked={form.repeatMonthly}
                      onChange={handleChange}
                    />
                    <span>Repeat same date each month</span>
                  </label>

                  <label className={styles.checkboxRow}>
                    <input
                      type="checkbox"
                      name="repeatEveryFourWeeks"
                      checked={form.repeatEveryFourWeeks}
                      onChange={handleChange}
                    />
                    <span>Repeat every four weeks</span>
                  </label>
                </div>

                <button type="submit" className={styles.submitButton} disabled={saving}>
                  {saving ? "Saving..." : "Add to Calendar"}
                </button>
              </form>
            </div>
          </div>
        </section>
      ) : (
        <section className={styles.monthScene}>
          <div className={styles.monthTopBar}>
            <div className={styles.monthNavCluster}>
              <button type="button" className={styles.navButton} onClick={() => setViewMode("year")}>
                Back to Year
              </button>
              <button type="button" className={styles.navButton} onClick={() => setViewMode("month")}>
                Back to Month
              </button>
              <button type="button" className={styles.navButton} onClick={() => setViewMode("month")}>
                Monthly Grid
              </button>
            </div>

            <div className={styles.monthTitle}>
              <span className={styles.yearCaption}>Daily View</span>
              <strong>
                <span className={selectedDate === todayKey ? styles.todayBadge : ""}>{selectedDate}</span>
              </strong>
            </div>
          </div>

          <div className={styles.dailyScene}>
            <div className={styles.dayPanel}>
              <p className={styles.kicker}>Bills Edit</p>
              <h2>
                <span className={selectedDate === todayKey ? styles.todayBadge : ""}>{selectedDate}</span>
              </h2>
              {selectedBills.length === 0 ? (
                <p className={styles.emptyText}>No bills on this date yet.</p>
              ) : (
                <div className={styles.selectedList}>
                  {selectedBills.map((bill) => (
                    <article key={bill.id} className={styles.selectedCard}>
                      <input
                        name="title"
                        value={editForms[bill.id]?.title || ""}
                        onChange={(event) => handleEditChange(bill.id, event)}
                        className={styles.input}
                        placeholder="Bill title"
                      />
                      <input
                        type="number"
                        min="0.01"
                        step="0.01"
                        name="amount"
                        value={editForms[bill.id]?.amount || ""}
                        onChange={(event) => handleEditChange(bill.id, event)}
                        className={styles.input}
                        placeholder="Amount"
                      />
                      <input
                        type="date"
                        name="due_date"
                        value={editForms[bill.id]?.due_date || ""}
                        onChange={(event) => handleEditChange(bill.id, event)}
                        className={styles.input}
                      />
                      <select
                        name="status"
                        value={editForms[bill.id]?.status || "draft"}
                        onChange={(event) => handleEditChange(bill.id, event)}
                        className={styles.input}
                      >
                        <option value="draft">Draft</option>
                        <option value="sent">Sent</option>
                        <option value="paid">Paid</option>
                        <option value="overdue">Overdue</option>
                      </select>
                      <textarea
                        name="description"
                        value={editForms[bill.id]?.description || ""}
                        onChange={(event) => handleEditChange(bill.id, event)}
                        className={styles.textarea}
                        placeholder="Notes"
                      />
                      <button
                        type="button"
                        className={styles.submitButton}
                        onClick={() => handleSaveBill(bill.id)}
                        disabled={editingBillId === bill.id}
                      >
                        {editingBillId === bill.id ? "Saving..." : "Save Bill"}
                      </button>
                    </article>
                  ))}
                </div>
              )}
            </div>

            <div className={styles.formPanel}>
              <p className={styles.kicker}>Bills Insert</p>
              <h2>Add to Calendar</h2>

              <form onSubmit={handleSubmit} className={styles.form}>
                <input
                  name="title"
                  value={form.title}
                  onChange={handleChange}
                  className={styles.input}
                  placeholder="Bill title"
                  required
                />

                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  name="amount"
                  value={form.amount}
                  onChange={handleChange}
                  className={styles.input}
                  placeholder="Amount"
                  required
                />

                <input
                  type="date"
                  name="due_date"
                  value={form.due_date}
                  onChange={handleChange}
                  className={styles.input}
                  required
                />

                <textarea
                  name="description"
                  value={form.description}
                  onChange={handleChange}
                  className={styles.textarea}
                  placeholder="Notes"
                />

                <div className={styles.repeatPanel}>
                  <label className={styles.checkboxRow}>
                    <input
                      type="checkbox"
                      name="repeatMonthly"
                      checked={form.repeatMonthly}
                      onChange={handleChange}
                    />
                    <span>Repeat same date each month</span>
                  </label>

                  <label className={styles.checkboxRow}>
                    <input
                      type="checkbox"
                      name="repeatEveryFourWeeks"
                      checked={form.repeatEveryFourWeeks}
                      onChange={handleChange}
                    />
                    <span>Repeat every four weeks</span>
                  </label>
                </div>

                <button type="submit" className={styles.submitButton} disabled={saving}>
                  {saving ? "Saving..." : "Add to Calendar"}
                </button>
              </form>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

export default BillsPage;
