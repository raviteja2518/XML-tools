"use client";

import React, { useEffect, useState } from 'react';
import { useAuth, User } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import api from '@/utils/api';
import { Loader2, UserCheck, Shield, Users, UserX } from 'lucide-react';

export default function AdminDashboard() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    if (!loading && user?.role !== 'admin') {
      router.push('/');
    }
  }, [user, loading, router]);

  const fetchUsers = async () => {
    try {
      const res = await api.get('/admin/users');
      setUsers(res.data);
    } catch (err) {
      console.error("Failed to fetch users", err);
    } finally {
      setFetching(false);
    }
  };

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchUsers();
    }
  }, [user]);

  const handleApprove = async (userId: number, role: string) => {
    try {
      await api.put(`/admin/users/${userId}/approve?role=${role}`);
      fetchUsers(); // Refresh list
    } catch (err) {
      console.error("Failed to approve user", err);
      alert("Failed to update user role");
    }
  };

  const handleDelete = async (userId: number) => {
    if (!confirm("Are you sure you want to delete this user?")) return;
    try {
      await api.delete(`/admin/users/${userId}`);
      fetchUsers();
    } catch (err) {
      console.error("Failed to delete user", err);
    }
  };

  if (loading || fetching || user?.role !== 'admin') {
    return (
      <div style={styles.loaderContainer}>
        <Loader2 className="animate-spin" size={40} color="#38bdf8" />
      </div>
    );
  }

  const pendingUsers = users.filter(u => u.role === 'pending');
  const activeUsers = users.filter(u => u.role !== 'pending');

  return (
    <div style={styles.container}>
      <h1 style={styles.pageTitle}>Admin Dashboard</h1>
      
      <div style={styles.statsGrid}>
         <div style={styles.statCard}>
            <Users size={24} color="#38bdf8"/>
            <h3 style={styles.statValue}>{users.length}</h3>
            <p style={styles.statLabel}>Total Users</p>
         </div>
         <div style={styles.statCard}>
            <Shield size={24} color="#34d399"/>
            <h3 style={styles.statValue}>{activeUsers.length}</h3>
            <p style={styles.statLabel}>Active Users</p>
         </div>
         <div style={styles.statCard}>
            <UserCheck size={24} color="#fbbf24"/>
            <h3 style={styles.statValue}>{pendingUsers.length}</h3>
            <p style={styles.statLabel}>Pending Requests</p>
         </div>
      </div>

      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>Pending Approvals</h2>
        {pendingUsers.length === 0 ? (
          <div style={styles.emptyState}>No pending users right now.</div>
        ) : (
          <div style={styles.tableContainer}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Name</th>
                  <th style={styles.th}>Email</th>
                  <th style={styles.th}>Role Requested</th>
                  <th style={styles.th}>Action</th>
                </tr>
              </thead>
              <tbody>
                {pendingUsers.map(u => (
                  <tr key={u.id} style={styles.tr}>
                    <td style={styles.td}>{u.name}</td>
                    <td style={styles.td}>{u.email}</td>
                    <td style={styles.td}>
                      <span style={{
                        ...styles.roleBadge,
                        background: u.requested_role === 'subscriber' ? 'rgba(129, 140, 248, 0.2)' : 'rgba(52, 211, 153, 0.2)',
                        color: u.requested_role === 'subscriber' ? '#a5b4fc' : '#6ee7b7'
                      }}>
                        {u.requested_role || 'employee'}
                      </span>
                    </td>
                    <td style={styles.td}>
                      <div style={styles.actions}>
                        <button style={u.requested_role === 'subscriber' ? styles.subscriberBtn : styles.approveBtn} 
                                onClick={() => handleApprove(u.id, u.requested_role || 'employee')}>
                          Approve Request
                        </button>
                        <button style={styles.deleteBtn} onClick={() => handleDelete(u.id)}>
                          <UserX size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>Active Users</h2>
        <div style={styles.tableContainer}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Name</th>
                  <th style={styles.th}>Email</th>
                  <th style={styles.th}>Role</th>
                  <th style={styles.th}>Action</th>
                </tr>
              </thead>
              <tbody>
                {activeUsers.map(u => (
                  <tr key={u.id} style={styles.tr}>
                    <td style={styles.td}>{u.name}</td>
                    <td style={styles.td}>{u.email}</td>
                    <td style={styles.td}>
                      <span style={{
                        ...styles.roleBadge,
                        background: u.role === 'admin' ? 'rgba(239, 68, 68, 0.2)' : 
                                    u.role === 'subscriber' ? 'rgba(129, 140, 248, 0.2)' : 'rgba(52, 211, 153, 0.2)',
                        color: u.role === 'admin' ? '#fca5a5' : 
                               u.role === 'subscriber' ? '#a5b4fc' : '#6ee7b7'
                      }}>
                        {u.role}
                      </span>
                    </td>
                    <td style={styles.td}>
                      {u.role !== 'admin' && (
                        <button style={styles.deleteBtn} onClick={() => handleDelete(u.id)}>
                           Delete
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
      </div>
    </div>
  );
}

const styles: any = {
  container: {
    padding: '40px 24px',
    maxWidth: '1200px',
    margin: '0 auto',
    color: '#f8fafc'
  },
  loaderContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '60vh'
  },
  pageTitle: {
    fontSize: '32px',
    fontWeight: 'bold',
    marginBottom: '32px',
    background: 'linear-gradient(to right, #38bdf8, #818cf8)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '24px',
    marginBottom: '40px'
  },
  statCard: {
    background: '#0f172a',
    border: '1px solid #1e293b',
    borderRadius: '12px',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.5)'
  },
  statValue: {
    fontSize: '36px',
    fontWeight: 'bold',
    margin: 0
  },
  statLabel: {
    color: '#94a3b8',
    margin: 0,
    fontSize: '14px'
  },
  section: {
    background: '#0f172a',
    border: '1px solid #1e293b',
    borderRadius: '16px',
    padding: '24px',
    marginBottom: '32px',
    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)'
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: '600',
    marginBottom: '20px',
    color: '#e2e8f0',
    borderBottom: '1px solid #1e293b',
    paddingBottom: '12px'
  },
  tableContainer: {
    overflowX: 'auto'
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    textAlign: 'left'
  },
  th: {
    padding: '12px 16px',
    color: '#94a3b8',
    fontWeight: '500',
    fontSize: '14px',
    borderBottom: '1px solid #1e293b'
  },
  tr: {
    borderBottom: '1px solid #1e293b',
    transition: 'background 0.2s'
  },
  td: {
    padding: '16px',
    fontSize: '15px'
  },
  actions: {
    display: 'flex',
    gap: '8px'
  },
  approveBtn: {
    background: 'rgba(52, 211, 153, 0.1)',
    color: '#34d399',
    border: '1px solid rgba(52, 211, 153, 0.2)',
    padding: '6px 12px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '500'
  },
  subscriberBtn: {
    background: 'rgba(129, 140, 248, 0.1)',
    color: '#818cf8',
    border: '1px solid rgba(129, 140, 248, 0.2)',
    padding: '6px 12px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '500'
  },
  deleteBtn: {
    background: 'rgba(239, 68, 68, 0.1)',
    color: '#f87171',
    border: '1px solid rgba(239, 68, 68, 0.2)',
    padding: '6px 12px',
    borderRadius: '6px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '4px'
  },
  emptyState: {
    textAlign: 'center',
    padding: '40px',
    color: '#94a3b8',
    fontStyle: 'italic'
  },
  roleBadge: {
    padding: '4px 10px',
    borderRadius: '9999px',
    fontSize: '12px',
    fontWeight: 'bold',
    textTransform: 'uppercase',
    letterSpacing: '0.05em'
  }
};
