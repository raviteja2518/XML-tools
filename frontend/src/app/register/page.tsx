"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/utils/api';
import Link from 'next/link';
import { Loader2, CheckCircle2 } from 'lucide-react';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
    requested_role: 'employee'
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await api.post('/auth/register', formData);
      setIsSuccess(true);
    } catch (err: any) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Failed to register. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (isSuccess) {
    return (
      <div style={styles.container}>
        <div style={{...styles.card, textAlign: 'center'}}>
          <CheckCircle2 color="#34d399" size={64} style={{margin: '0 auto 20px'}} />
          <h2 style={{...styles.title, marginBottom: '16px'}}>Registration Successful!</h2>
          <p style={{...styles.subtitle, lineHeight: '1.6', marginBottom: '30px'}}>
            Your account has been created and is currently <b style={{color: '#fbbf24'}}>Pending Approval</b>. 
            An administrator must accept your request before you can log in.
          </p>
          <Link href="/login">
            <button style={styles.button}>Return to Login</button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <h1 style={styles.title}>Request Access</h1>
          <p style={styles.subtitle}>Register to use our premium conversion tools</p>
        </div>

        {error && <div style={styles.error}>{error}</div>}

        <form onSubmit={handleRegister} style={styles.form}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Full Name</label>
            <input 
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              style={styles.input}
              required 
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Email Address</label>
            <input 
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              style={styles.input}
              required 
            />
          </div>
          
          <div style={styles.inputGroup}>
            <label style={styles.label}>Phone Number</label>
            <input 
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              style={styles.input}
              required 
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Password</label>
            <input 
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              style={styles.input}
              required 
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Requested Account Type</label>
            <select
              name="requested_role"
              value={formData.requested_role}
              onChange={handleChange as any}
              style={styles.input}
              required
            >
              <option value="employee">Employee (Free Internal Access)</option>
              <option value="subscriber">Subscriber (Paid Premium Access)</option>
            </select>
          </div>

          <button type="submit" style={styles.button} disabled={isLoading}>
            {isLoading ? <Loader2 className="animate-spin" size={20} /> : 'Submit Request'}
          </button>
        </form>

        <div style={styles.footer}>
          <span>Already have an account? </span>
          <Link href="/login" style={styles.link}>Sign In</Link>
        </div>
      </div>
    </div>
  );
}

const styles: any = {
  container: {
    minHeight: 'calc(100vh - 60px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#020617', // Match slate-950 dark theme
    color: 'white',
    padding: '20px'
  },
  card: {
    background: '#0f172a', // Match slate-900 
    border: '1px solid #1e293b',
    borderRadius: '16px',
    padding: '40px',
    width: '100%',
    maxWidth: '500px',
    boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.5), 0 8px 10px -6px rgb(0 0 0 / 0.5)'
  },
  header: {
    textAlign: 'center',
    marginBottom: '32px'
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    margin: '0 0 8px 0',
    background: 'linear-gradient(to right, #38bdf8, #818cf8)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  subtitle: {
    color: '#94a3b8',
    margin: 0,
    fontSize: '15px'
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px'
  },
  inputGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  label: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#cbd5e1'
  },
  input: {
    padding: '12px 16px',
    borderRadius: '8px',
    background: '#1e293b',
    border: '1px solid #334155',
    color: 'white',
    fontSize: '15px',
    outline: 'none',
    transition: 'border-color 0.2s'
  },
  button: {
    background: '#38bdf8',
    color: '#0f172a',
    border: 'none',
    padding: '14px',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    marginTop: '10px',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    transition: 'opacity 0.2s',
    width: '100%'
  },
  error: {
    background: 'rgba(239, 68, 68, 0.1)',
    color: '#f87171',
    padding: '12px',
    borderRadius: '8px',
    fontSize: '14px',
    marginBottom: '20px',
    border: '1px solid rgba(239, 68, 68, 0.2)',
    textAlign: 'center'
  },
  footer: {
    marginTop: '32px',
    textAlign: 'center',
    fontSize: '14px',
    color: '#94a3b8'
  },
  link: {
    color: '#38bdf8',
    textDecoration: 'none',
    fontWeight: '600'
  }
};
