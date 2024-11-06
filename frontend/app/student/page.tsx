"use client";
import React, { useState, useEffect } from "react";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
import styles from "../../styles/calendar.module.css";

export default function CalendarGfg() {
  const [value, onChange] = useState<Date | Date[]>(new Date());
  const [absentDates, setAbsentDates] = useState<string[]>([]);
  const [mounted, setMounted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionDetails, setSessionDetails] = useState<{
    session: string;
    professor: string;
  } | null>(null);

  useEffect(() => {
    setMounted(true);
    const fetchAbsentDates = async () => {
      try {
        const response = await fetch("http://localhost:8080/api/absent-dates");
        if (!response.ok) {
          throw new Error(`Failed to fetch absent dates. Status: ${response.status}`);
        }
        const data = await response.json();

        // Check if absentDates is present and valid in the response
        if (data && Array.isArray(data.absentDates)) {
          setAbsentDates(data.absentDates);
        } else {
          throw new Error("Absent dates data is missing or invalid.");
        }
      } catch (error) {
        console.error("Error fetching absent dates:", error);
        setError("Failed to load absence data.");
      }
    };

    fetchAbsentDates();
  }, []);

  const fetchSessionDetails = async (date: string) => {
    try {
      const response = await fetch(`http://localhost:8080/api/session-details?date=${date}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch session details. Status: ${response.status}`);
      }
      const data = await response.json();
      if (data.session && data.professor) {
        setSessionDetails(data);
      } else {
        setSessionDetails({ session: "Not Found", professor: "N/A" });
      }
    } catch (error) {
      console.error("Error fetching session details:", error);
      setSessionDetails({ session: "Error", professor: "N/A" });
    }
  };

  if (!mounted) {
    return null; // Avoid rendering before the component is mounted
  }

  return (
    <div className={styles.calendarContainer}>
      <h1 className={styles.title}>Student Absence Calendar</h1>
      {error && <div className={styles.errorMessage}>{error}</div>}

      <Calendar
        onChange={onChange}
        value={value}
        tileClassName={({ date }) => {
          const dateString = date.toISOString().split("T")[0];
          return absentDates.includes(dateString) ? styles.absentTile : "";
        }}
        onClickDay={(date) => {
          const dateString = date.toISOString().split("T")[0];
          if (absentDates.includes(dateString)) {
            fetchSessionDetails(dateString);
          }
        }}
      />

      {sessionDetails && (
        <div className={styles.sessionDetails}>
          <h2>Session Information</h2>
          <p>
            <strong>Session:</strong> {sessionDetails.session}
          </p>
          <p>
            <strong>Professor:</strong> {sessionDetails.professor}
          </p>
        </div>
      )}
    </div>
  );
}
