import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import clientsApi from "../../api/clientsApi";
import styles from "./CreateClient.module.css";

function CreateClient() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    phone: "",
    email: "",
    address: "",
  });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await clientsApi.create(form);
      navigate("/clients");
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to create client.");
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.headerRow}>
        <div>
          <p className={styles.eyebrow}>Client Management</p>
          <h2>Create New Client</h2>
        </div>
        <Link to="/clients" className={styles.backLink}>
          Back to Clients
        </Link>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      <form onSubmit={handleSubmit} className={styles.form}>
        <input
          type="text"
          name="name"
          placeholder="Client Name"
          value={form.name}
          onChange={handleChange}
          className={styles.input}
          required
        />

        <input
          type="text"
          name="phone"
          placeholder="Phone"
          value={form.phone}
          onChange={handleChange}
          className={styles.input}
        />

        <input
          type="email"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          className={styles.input}
        />

        <input
          type="text"
          name="address"
          placeholder="Address"
          value={form.address}
          onChange={handleChange}
          className={styles.input}
        />

        <button type="submit" className={styles.button}>
          Save Client
        </button>
      </form>
    </div>
  );
}

export default CreateClient;
