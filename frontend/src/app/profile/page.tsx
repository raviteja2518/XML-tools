"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import api from "@/utils/api";
import Navbar from "@/components/Navbar";
import { User, Mail, Phone, ShieldCheck, Zap, AlertCircle, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

const ProfilePage = () => {
  const { user, updateUser, logout } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || "",
    phone: user?.phone || "",
  });

  useEffect(() => {
    if (user) {
      setFormData({ name: user.name, phone: user.phone });
    }
  }, [user]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.put("/profile/update", formData);
      updateUser(response.data);
      alert("Profile updated successfully!");
    } catch (error) {
      console.error("Update failed:", error);
      alert("Failed to update profile.");
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = () => {
    router.push("/payment");
  };

  if (!user) return null;

  const daysLeft = user.subscription_expiry 
    ? Math.max(0, Math.ceil((new Date(user.subscription_expiry).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)))
    : 0;

  return (
    <div className="min-h-screen bg-black text-white selection:bg-indigo-500/30">
      <main className="max-w-4xl mx-auto px-6 py-12">
        <div className="space-y-8">
          {/* Header */}
          <div className="flex flex-col md:flex-row items-center gap-8 bg-gray-900/50 p-8 rounded-3xl border border-white/5">
            <div className="w-24 h-24 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
              <User className="w-10 h-10 text-indigo-400" />
            </div>
            <div className="text-center md:text-left">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
                {user.name}
              </h1>
              <p className="text-gray-400 mt-1 flex items-center justify-center md:justify-start gap-2">
                <ShieldCheck className="w-4 h-4 text-indigo-400" />
                {user.role.charAt(0).toUpperCase() + user.role.slice(1)} Account
              </p>
              <div className="mt-4 flex flex-wrap gap-2 justify-center md:justify-start">
                <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs text-gray-400">
                  Member since {new Date(user.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Info Card */}
            <div className="md:col-span-2 bg-gray-900/50 rounded-3xl border border-white/5 overflow-hidden">
              <div className="p-8 border-b border-white/5">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <User className="w-5 h-5 text-indigo-400" />
                  Account Information
                </h2>
              </div>
              <form onSubmit={handleUpdate} className="p-8 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm text-gray-400 ml-1">Full Name</label>
                    <div className="relative">
                      <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full bg-black border border-white/10 rounded-xl py-3 pl-12 pr-4 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all outline-none"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm text-gray-400 ml-1">Phone Number</label>
                    <div className="relative">
                      <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                      <input
                        type="text"
                        value={formData.phone}
                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                        className="w-full bg-black border border-white/10 rounded-xl py-3 pl-12 pr-4 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all outline-none"
                      />
                    </div>
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm text-gray-400 ml-1">Email Address (Read-only)</label>
                  <div className="relative opacity-60">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                      type="email"
                      value={user.email}
                      disabled
                      className="w-full bg-gray-900/50 border border-white/10 rounded-xl py-3 pl-12 pr-4 outline-none cursor-not-allowed"
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full md:w-auto px-8 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-600/50 text-white font-semibold rounded-xl transition-all shadow-lg shadow-indigo-500/20 flex items-center justify-center gap-2"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                  Save Changes
                </button>
              </form>
            </div>

            {/* Subscription Card */}
            <div className="bg-gray-900/50 rounded-3xl border border-white/5 overflow-hidden flex flex-col">
              <div className="p-8 border-b border-white/5">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <Zap className="w-5 h-5 text-indigo-400" />
                  Subscription
                </h2>
              </div>
              <div className="p-8 flex-1 flex flex-col justify-between">
                <div>
                  {user.role === "subscriber" ? (
                    <div className="space-y-6">
                      <div className="bg-indigo-500/10 border border-indigo-500/20 p-4 rounded-2xl text-center">
                        <span className="text-4xl font-bold text-indigo-400">{daysLeft}</span>
                        <p className="text-sm text-gray-400 mt-1 uppercase tracking-wider">Days Remaining</p>
                      </div>
                      <div className="space-y-3">
                        <p className="text-sm text-gray-400 flex items-center gap-2">
                          <ShieldCheck className="w-4 h-4 text-green-400" />
                          Full Tool Access
                        </p>
                        <p className="text-sm text-gray-400 flex items-center gap-2">
                          <Zap className="w-4 h-4 text-indigo-400" />
                          Premium Support
                        </p>
                      </div>
                    </div>
                  ) : user.role === "employee" ? (
                    <div className="space-y-6">
                      <div className="bg-white/5 border border-white/10 p-4 rounded-2xl text-center">
                        <span className="text-2xl font-bold text-gray-300">Employee</span>
                        <p className="text-sm text-gray-400 mt-1 uppercase tracking-wider">Internal Access</p>
                      </div>
                      <p className="text-sm text-gray-400 leading-relaxed italic">
                        Want premium features and priority processing? Upgrade to a Subscriber account today.
                      </p>
                    </div>
                  ) : (
                    <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl text-amber-500 flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 shrink-0" />
                      <p className="text-sm">Your account is pending admin approval.</p>
                    </div>
                  )}
                </div>

                {user.role !== "admin" && (
                  <button 
                    onClick={handleUpgrade}
                    className="mt-8 w-full py-4 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-bold rounded-2xl transition-all shadow-xl shadow-indigo-500/25 active:scale-95 flex items-center justify-center gap-2"
                  >
                    <Zap className="w-4 h-4 fill-current" />
                    {user.role === "subscriber" ? "Renew Subscription" : "Upgrade to Pro"}
                  </button>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex justify-center pt-8">
            <button 
              onClick={logout}
              className="text-gray-500 hover:text-red-400 transition-colors text-sm font-medium flex items-center gap-2"
            >
              Sign out of your account
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ProfilePage;
