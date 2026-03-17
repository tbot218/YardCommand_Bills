import { Link } from "react-router-dom";

import styles from "./Dashboard.module.css";

const cards = [
  {
    title: "Clients",
    description: "Track active properties, contact details, and service relationships.",
    action: "Open clients",
    to: "/clients",
  },
  {
    title: "Bills",
    description: "Create invoices, monitor due dates, and start building accounts receivable.",
    action: "Open bills",
    to: "/bills",
  },
];

function Dashboard() {
  const user = localStorage.getItem("yard_user") || "Yard Command";

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <p className={styles.eyebrow}>Operations Dashboard</p>
        <h1>Run the business from one place.</h1>
        <p className={styles.lead}>
          Welcome back, {user}. This is the first management hub for Yard Command:
          clients in one lane, billing in the next, and room to grow into a full
          groundskeeping operations system.
        </p>
      </section>

      <section className={styles.grid}>
        {cards.map((card) => (
          <article key={card.title} className={styles.card}>
            <h2>{card.title}</h2>
            <p>{card.description}</p>
            <Link to={card.to} className={styles.link}>
              {card.action}
            </Link>
          </article>
        ))}
      </section>
    </div>
  );
}

export default Dashboard;
