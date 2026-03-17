import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import clientsApi from "../../api/clientsApi";
import styles from "./ClientsList.module.css";

function ClientsList() {
  const navigate = useNavigate();
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadClients = async () => {
      try {
        const res = await clientsApi.getAll();
        setClients(res.data);
      } catch (err) {
        console.error("Error loading clients:", err);
      } finally {
        setLoading(false);
      }
    };

    loadClients();
  }, []);

  return (
    <div className={styles.container}>
      <div className={styles.headerRow}>
        <div>
          <p className={styles.eyebrow}>Client Management</p>
          <h2>Active Clients</h2>
        </div>
        <div className={styles.actions}>
          <Link to="/dashboard" className={styles.secondaryBtn}>
            Back to Dashboard
          </Link>
          <button className={styles.createBtn} onClick={() => navigate("/clients/create")}>
            New Client
          </button>
        </div>
      </div>

      {loading ? (
        <p>Loading clients...</p>
      ) : (
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Client Name</th>
              <th>Phone</th>
              <th>Email</th>
              <th>Address</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {clients.map((client) => (
              <tr key={client.id}>
                <td>{client.name}</td>
                <td>{client.phone || "-"}</td>
                <td>{client.email || "-"}</td>
                <td>{client.address || "-"}</td>
                <td>{client.is_archived ? "Archived" : "Active"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default ClientsList;
