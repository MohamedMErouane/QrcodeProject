"use client";
import { useState } from 'react';
import { User } from '../types/user';
import { useRouter } from 'next/navigation'; // Import Next.js router for navigation
import styles from '../styles/login.module.css'; // Import your CSS styles

export default function Login() {
  const [user, setUser] = useState<User | null>(null);
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [sessionId, setSessionId] = useState<string | null>(null); // Add state for sessionId
  const router = useRouter(); // Next.js router

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
  
    try {
      const response = await fetch('http://localhost:8080/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          password,
        }),
      });
  
      if (!response.ok) {
        throw new Error('Invalid credentials');
      }
  
      const data = await response.json();
  
      // Store user data and session ID in localStorage
      localStorage.setItem('userData', JSON.stringify(data));
      sessionStorage.setItem('username', username);   // Save the username from the backend

      console.log(data)
  
      // Set user and sessionId in state
      setUser(data);
      setSessionId(data.sessionId);
  
      // Check user role and redirect accordingly
      if (data.role === "professor") {
        router.push('/professor');
      } else if (data.role === "student") {
        router.push('/student');
      }
    } catch (error) {
      console.error(error);
      alert('Invalid credentials or server error');
    }
  };
  

  return (
    <div className={styles.loginRoot}>
      <div className={styles.loginBackground}>
        <div className={styles.formContainer}>
          <h2 className={styles.header}>Login</h2>
          <form onSubmit={handleLogin}>
            <div className={styles.field}>
              <label className={styles.label} htmlFor="username">Username</label>
              <input
                className={styles.input}
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className={styles.field}>
              <label className={styles.label} htmlFor="password">Password</label>
              <input
                className={styles.input}
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <button className={styles.submitButton} type="submit">
              Log In
            </button>
          </form>
        </div>
      </div>
      {user && <p>Welcome, {user.name}</p>}
      {sessionId && <p>Your session ID: {sessionId}</p>} {/* Optional: Display session ID */}
    </div>
  );
}
