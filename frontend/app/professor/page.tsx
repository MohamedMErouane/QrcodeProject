"use client";
import { useState } from 'react';
import styles from '../../styles/porfessor.module.css';

const ProfessorPage = () => {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    sessionDate: '',
    sessionName: '',
    professorName: 'Professor John',
  });
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null);

  const classes = [
    { id: 1, name: 'Class 1' },
    { id: 2, name: 'Class 2' },
    { id: 3, name: 'Class 3' },
    { id: 4, name: 'Class 4' },
  ];

  const handleClassClick = () => {
    setShowForm(true);
  };

  const handleInputChange = (e: any) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
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

    // Check if the response is in binary (QR code image)
    if (response.ok) {
      const blob = await response.blob(); // Get the response as a Blob (binary data)
      const qrCodeUrl = URL.createObjectURL(blob); // Create a URL for the Blob
      setQrCodeUrl(qrCodeUrl); // Set the image URL for displaying in the UI
      setShowForm(false); // Hide the form after QR code is generated
    } else {
      const errorData = await response.json();
      console.error('Error generating QR code:', errorData);
    }
  };

  const handleCancel = () => {
    setShowForm(false); // Hide form and show cards again
  };

  return (
    <div className={styles.professorPage}>
      <h1>Professor's Dashboard</h1>
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

      {/* QR Code Section: Display QR code if generated */}
      {qrCodeUrl && (
        <div className={styles.qrCodeContainer}>
          <img src={qrCodeUrl} alt="QR Code" className={styles.qrImage} />
        </div>
      )}

      {/* Form Section: Display form when showForm is true */}
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
              <label>Session Name:</label>
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
