"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import api from '@/utils/api';
import { Loader2, CreditCard, ShieldCheck } from 'lucide-react';

export default function PaymentPage() {
  const { user, loading, login, token } = useAuth();
  const router = useRouter();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.push('/login');
      } else if (user.role !== 'subscriber') {
        router.push('/');
      } else if (user.has_paid) {
        router.push('/');
      }
    }
  }, [user, loading, router]);

  const handlePayment = async () => {
    setIsProcessing(true);
    setError('');
    
    try {
      // Simulate network delay for effect
      await new Promise(r => setTimeout(r, 1500));
      
      const res = await api.post('/payment/checkout');
      // Update the local context user object
      if (token) {
         login(token, res.data); // This overwrites the user in context/localStorage with has_paid=1
      }
      
      // Navigate to dashboard/tools
      router.push('/');
    } catch (err) {
      console.error(err);
      setError('Payment gateway error. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  if (loading || !user || user.has_paid) {
    return (
      <div style={styles.loaderContainer}>
        <Loader2 className="animate-spin" size={40} color="#38bdf8" />
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <div style={styles.iconWrapper}>
            <CreditCard size={32} color="#38bdf8" />
          </div>
          <h1 style={styles.title}>Activate Subscription</h1>
          <p style={styles.subtitle}>
            Your account has been approved! Complete your payment to unlock all premium XML conversion tools.
          </p>
        </div>

        {error && <div style={styles.error}>{error}</div>}

        <div style={styles.planBox}>
          <div style={styles.planHeader}>
            <span style={styles.planName}>Premium Subscriber</span>
            <span style={styles.planPrice}>$49<span style={styles.planMonth}>/mo</span></span>
          </div>
          <ul style={styles.featureList}>
            <li>✓ Unlimited PDF to XML conversions</li>
            <li>✓ Advanced OCR capabilities</li>
            <li>✓ Retain layout structures</li>
            <li>✓ Priority Processing</li>
          </ul>
        </div>

        <button 
          style={styles.payButton} 
          onClick={handlePayment} 
          disabled={isProcessing}
        >
          {isProcessing ? (
            <><Loader2 className="animate-spin" size={20} /> Processing...</>
          ) : (
            <>Pay $49.00 <ShieldCheck size={18} /></>
          )}
        </button>
        
        <p style={styles.mockDisclaimer}>
          * This is a secure mock payment gateway for demonstration purposes. No real charges will be processed.
        </p>
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
    background: '#020617',
    padding: '20px'
  },
  loaderContainer: {
    height: '60vh',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    background: '#020617'
  },
  card: {
    background: '#0f172a',
    border: '1px solid #1e293b',
    borderRadius: '16px',
    padding: '40px',
    maxWidth: '500px',
    width: '100%',
    boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.5), 0 8px 10px -6px rgb(0 0 0 / 0.5)'
  },
  header: {
    textAlign: 'center',
    marginBottom: '32px'
  },
  iconWrapper: {
    background: 'rgba(56, 189, 248, 0.1)',
    width: '64px',
    height: '64px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 16px'
  },
  title: {
    fontSize: '26px',
    fontWeight: 'bold',
    color: '#f8fafc',
    margin: '0 0 12px 0'
  },
  subtitle: {
    color: '#94a3b8',
    margin: 0,
    fontSize: '15px',
    lineHeight: '1.5'
  },
  planBox: {
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '12px',
    padding: '24px',
    marginBottom: '32px'
  },
  planHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
    borderBottom: '1px solid #334155',
    paddingBottom: '16px'
  },
  planName: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#f8fafc'
  },
  planPrice: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#38bdf8'
  },
  planMonth: {
    fontSize: '14px',
    color: '#94a3b8',
    fontWeight: 'normal'
  },
  featureList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
    color: '#cbd5e1',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    fontSize: '14px'
  },
  payButton: {
    background: '#38bdf8',
    color: '#0f172a',
    border: 'none',
    padding: '16px',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '8px',
    width: '100%',
    transition: 'opacity 0.2s',
    boxShadow: '0 4px 6px -1px rgba(56, 189, 248, 0.3)'
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
  mockDisclaimer: {
    marginTop: '24px',
    color: '#64748b',
    fontSize: '12px',
    textAlign: 'center',
    fontStyle: 'italic'
  }
};
