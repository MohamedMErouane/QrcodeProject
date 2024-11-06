"use client";
import { useState } from 'react';
import { User } from '../types/user'
import { useRouter } from 'next/navigation'; // Import Next.js router for navigation
import styles from '../styles/login.module.css'; // Import your CSS styles

export default function Login() {
  const [user, setUser] = useState<User | null>(null);
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const router = useRouter(); // Next.js router
  

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
  
    try {
      // Send the request to your Python backend
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
  
      // Assuming the response contains user data with role and name
      setUser(data);
  
      // Check user role and redirect accordingly
      if (data.role === 1) {
        // Redirect to Professor page
        router.push('/professor');
      } else if (data.role === 0) {
        // Redirect to Student page
        router.push('/student');
      }
    } catch (error) {
      // Handle errors such as invalid credentials or server issues
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
    </div>
  );
}
