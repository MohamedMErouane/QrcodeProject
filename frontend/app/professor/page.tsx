"use client";
import { useState, useEffect } from 'react';
import styles from '../../styles/porfessor.module.css';

const ProfessorPage = () => {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    sessionDate: '',
    sessionName: '',
    professorName: '', // This will be set dynamically from the backend
    sessionTime: '', // New field for session time
  });
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null); // Store the session ID

  const classes = [
    { id: 1, name: 'Class 1' },
    { id: 2, name: 'Class 2' },
    { id: 3, name: 'Class 3' },
    { id: 4, name: 'Class 4' },
  ];

  useEffect(() => {
    const storedSessionId = sessionStorage.getItem('sessionId'); 
    const storedUsername = sessionStorage.getItem('username'); // Assuming the username is also stored in sessionStorage

    if (storedSessionId) {
      setSessionId(storedSessionId);
      fetchProfessorInfo(storedSessionId); // Fetch professor info after setting sessionId
    }

    if (storedUsername) {
      setFormData(prev => ({
        ...prev,
        professorName: storedUsername, // Set the professor name from sessionStorage
      }));
    }

    console.log("Stored session ID:", storedSessionId); // Debug: check session ID
    console.log("Stored username:", storedUsername); // Debug: check username
  }, []);

  const handleClassClick = () => {
    setShowForm(true);
  };

  const handleInputChange = (e: any) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFormSubmit = async (e: any) => {
    e.preventDefault();
    const response = await fetch('http://localhost:8080/generate-qr', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });

    if (response.ok) {
      const blob = await response.blob();
      const qrCodeUrl = URL.createObjectURL(blob);
      setQrCodeUrl(qrCodeUrl);
      setShowForm(false);
    } else {
      const errorData = await response.json();
      console.error('Error generating QR code:', errorData);
    }
  };

  const handleCancel = () => {
    setShowForm(false);
  };

  return (
    <div className={styles.professorPage}>
      <h1>{formData.professorName ? `${formData.professorName}'s Dashboard` : "Dashboard"}</h1>
      {!showForm && !qrCodeUrl && (
        <div className={styles.classCards}>
          {classes.map((classInfo) => (
            <div
              key={classInfo.id}
              className={styles.card}
              onClick={handleClassClick}
            >
              <h3>{classInfo.name}</h3>
            </div>
          ))}
        </div>
      )}

      {qrCodeUrl && (
        <div className={styles.qrCodeContainer}>
          <img src={qrCodeUrl} alt="QR Code" className={styles.qrImage} />
        </div>
      )}

      {showForm && !qrCodeUrl && (
        <div className={styles.formContainer}>
          <h2>Generate QR Code</h2>
          <form onSubmit={handleFormSubmit} className={styles.form}>
            <div>
              <label>Session Date:</label>
              <input
                type="date"
                name="sessionDate"
                value={formData.sessionDate}
                onChange={handleInputChange}
                className={styles.input}
                required
              />
            </div>
            <div>
              <label >Session Name:</label>
              <input
                type="text"
                name="sessionName"
                value={formData.sessionName}
                onChange={handleInputChange}
                className={styles.input}
                required
              />
            </div>
            <div>
              <label >Session Time:</label>
              <select
                name="sessionTime"
                value={formData.sessionTime}
                onChange={handleInputChange}
                className={styles.input}
                required
              >
                <option value="">Select a time</option>
                <option value="8 to 10">8 to 10</option>
                <option value="10 to 12">10 to 12</option>
                <option value="2 to 4">2 to 4</option>
                <option value="4 to 6">4 to 6</option>
              </select>
            </div>
            <div>
              <label>Professor Name:</label>
              <input
                type="text"
                name="professorName"
                value={formData.professorName}
                readOnly
                className={styles.input}
              />
            </div>
            <button type="submit" className={styles.button}>
              Generate QR Code
            </button>
            <button type="button" onClick={handleCancel} className={styles.cancelButton}>
              Cancel
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default ProfessorPage;
