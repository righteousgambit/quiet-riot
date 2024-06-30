"use client";

import { useState, ChangeEvent } from "react";
import styles from "./page.module.css";

export default function Home() {
  const [principalType, setPrincipalType] = useState("");
  const [principalValue, setPrincipalValue] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [enums, setEnums] = useState<number>(1000000);
  const [serverStartDate, setServerStartDate] = useState<string>("10/15/1986");
  const handlePrincipalTypeChange = (e: ChangeEvent<HTMLSelectElement>) => {
    setPrincipalType(e.target.value);
  };

  const handlePrincipalValueChange = (e: ChangeEvent<HTMLInputElement>) => {
    setPrincipalValue(e.target.value);
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] || null);
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Handle form submission logic here
  };

  return (
    <main className={styles.main}>
      <div className={styles.titleContainer}>
        <h1>Quiet Riot</h1>
        <h2>🎶 C&#39;mon, Feel The Noise 🎶</h2>
      </div>
      <div className={styles.description}>
        <p>{enums} IAM Principals Enumerated since {serverStartDate}</p>
      </div>

      <div className={styles.formContainer}>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label htmlFor="principalType">Principal Type:</label>
            <select
              id="principalType"
              value={principalType}
              onChange={handlePrincipalTypeChange}
              className={styles.input}
            >
              <option value="">Select Principal Type</option>
              <option value="User">User</option>
              <option value="Group">Group</option>
              <option value="Role">Role</option>
            </select>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="principalValue">Principal Value:</label>
            <input
              type="text"
              id="principalValue"
              value={principalValue}
              onChange={handlePrincipalValueChange}
              className={styles.input}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="fileUpload">Upload File:</label>
            <input
              type="file"
              id="fileUpload"
              onChange={handleFileChange}
              className={styles.input}
            />
          </div>

          <button type="submit" className={styles.button}>
            Submit
          </button>
        </form>
      </div>
    </main>
  );
}
