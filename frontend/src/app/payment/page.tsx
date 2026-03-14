"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import api from "@/utils/api";
import { Loader2, ShieldCheck, Zap, CheckCircle2 } from "lucide-react";
import Navbar from "@/components/Navbar";

const plans = [
  {
    type: 1,
    name: "Monthly",
    price: 499,
    period: "month",
    description: "Perfect for a single project or short-term needs.",
    features: ["Full OCR Access", "30-Day Duration", "Priority Processing", "Standard Email Support"],
  },
  {
    type: 6,
    name: "Half-Yearly",
    price: 2499,
    period: "6 months",
    description: "The most popular choice for professionals.",
    popular: true,
    features: ["All Monthly Features", "180-Day Duration", "Cost Effective", "Priority Support"],
  },
  {
    type: 12,
    name: "Annual",
    price: 4499,
    period: "year",
    description: "Best for power users and long-term workflows.",
    features: ["All Professional Features", "365-Day Duration", "Lowest Pricing", "24/7 Priority Support"],
  },
];

export default function PaymentPage() {
  const { user, loading, login, token } = useAuth();
  const router = useRouter();
  const [selectedPlan, setSelectedPlan] = useState<number | null>(6);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.push("/login");
      } else if (user.role === "pending") {
        router.push("/"); // Or where they wait for approval
      } else if (user.has_paid) {
        router.push("/");
      }
    }
  }, [user, loading, router]);

  const handlePayment = async () => {
    if (selectedPlan === null) return;
    setIsProcessing(true);
    setError("");

    try {
      await new Promise((r) => setTimeout(r, 1500)); // Mock network delay

      const res = await api.post("/payment/checkout", { plan_type: selectedPlan });
      if (token) {
        login(token, res.data);
      }
      router.push("/");
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Payment gateway error. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  if (loading || !user || user.has_paid) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <Loader2 className="animate-spin text-indigo-500 w-12 h-12" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white selection:bg-indigo-500/30">
      <Navbar />

      <main className="max-w-6xl mx-auto px-6 py-16">
        <div className="text-center mb-16 space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-white via-white to-white/40 bg-clip-text text-transparent">
            Unlock Premium Access
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Choose the subscription plan that fits your professional workflow. All tools, no limits.
          </p>
        </div>

        {error && (
          <div className="mb-8 p-4 bg-red-500/10 border border-red-500/20 text-red-500 rounded-2xl text-center">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan) => (
            <div
              key={plan.type}
              onClick={() => setSelectedPlan(plan.type)}
              className={`relative cursor-pointer group p-8 rounded-[2.5rem] border transition-all duration-300 flex flex-col justify-between ${
                selectedPlan === plan.type
                  ? "bg-indigo-600/10 border-indigo-500 ring-1 ring-indigo-500"
                  : "bg-gray-900/40 border-white/5 hover:border-white/20"
              }`}
            >
              {plan.popular && (
                <span className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-indigo-600 to-violet-600 text-white text-[10px] font-bold uppercase tracking-widest rounded-full shadow-lg shadow-indigo-500/20">
                  Most Popular
                </span>
              )}

              <div className="space-y-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-bold">{plan.name}</h3>
                    <p className="text-gray-500 text-sm mt-1">{plan.description}</p>
                  </div>
                  {selectedPlan === plan.type && (
                    <CheckCircle2 className="w-6 h-6 text-indigo-400" />
                  )}
                </div>

                <div className="py-6">
                  <span className="text-5xl font-extrabold strike">₹{plan.price.toLocaleString()}</span>
                  <span className="text-gray-500 text-sm italic ml-2">/ {plan.period}</span>
                </div>

                <ul className="space-y-4">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center gap-3 text-sm text-gray-300">
                      <Zap className="w-3.5 h-3.5 text-indigo-400 fill-indigo-400/20" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-12">
                <div
                  className={`w-full py-4 rounded-2xl font-bold transition-all text-center ${
                    selectedPlan === plan.type
                      ? "bg-white text-black"
                      : "bg-white/5 text-white group-hover:bg-white/10"
                  }`}
                >
                  {selectedPlan === plan.type ? "Selected Plan" : "Choose Logic"}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-16 max-w-md mx-auto">
          <button
            onClick={handlePayment}
            disabled={isProcessing || selectedPlan === null}
            className="w-full py-5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-bold rounded-2.5xl transition-all shadow-xl shadow-indigo-500/25 active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isProcessing ? (
              <>
                <Loader2 className="animate-spin w-5 h-5" />
                Processing Securely...
              </>
            ) : (
              <>
                Complete Payment <ShieldCheck className="w-5 h-5" />
              </>
            )}
          </button>
          <p className="text-center text-gray-500 text-xs mt-6 italic">
            * This is a secure mock payment gateway. No real INR charges will be applied for this demonstration.
          </p>
        </div>
      </main>
    </div>
  );
}
