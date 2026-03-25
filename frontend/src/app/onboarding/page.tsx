"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function Onboarding() {
  const router = useRouter();
  const { user, login } = useAuth();
  const [roleSelection, setRoleSelection] = useState<"user" | "broker">("user");
  const [loading, setLoading] = useState(false);

  // User form data
  const [formData, setFormData] = useState({
    location_name: "Mumbai",
    lat: 19.076,
    lng: 72.877,
    budget_min: 10000,
    budget_max: 50000,
    preferred_type: "flat",
    purpose: "rent"
  });

  // Broker form data
  const [localityName, setLocalityName] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (roleSelection === "user") {
        // Complete regular user onboarding
        await api.post("/users/onboarding", formData);
        
        // Refresh token context
        const token = localStorage.getItem("token");
        if (token) await login(token);
        
        router.push("/");
      } else {
        // Broker registration flow
        // 1. Submit basic onboarding so the user isn't stuck in the onboarding loop
        await api.post("/users/onboarding", formData);

        // 2. Register as broker
        const defaultPolygon = {
          type: "Polygon",
          coordinates: [
            [
              [72.82, 19.04], [72.85, 19.04], [72.85, 19.07], [72.82, 19.07], [72.82, 19.04]
            ],
          ],
        };
        await api.post("/brokers/register", {
          locality_name: localityName,
          locality_polygon: defaultPolygon,
        });

        // Refresh token context to get the 'broker' role
        const token = localStorage.getItem("token");
        if (token) await login(token);
        
        router.push("/broker");
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to save preferences.");
    }
    setLoading(false);
  };

  if (!user) return <div className="p-8 text-center text-red-500">Not logged in</div>;

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-200">
        <h1 className="text-2xl font-bold mb-2">Welcome! Let's set up your profile</h1>
        <p className="text-gray-500 mb-8">Tell us how you plan to use RealEstates.</p>

        {/* Role Selection Tabs */}
        <div className="flex bg-gray-100 p-1 rounded-xl mb-8">
          <button
            type="button"
            onClick={() => setRoleSelection("user")}
            className={`flex-1 py-3 text-sm font-bold rounded-lg transition-colors ${
              roleSelection === "user" ? "bg-white text-blue-600 shadow-sm" : "text-gray-900 hover:text-black"
            }`}
          >
            I'm looking for a property
          </button>
          <button
            type="button"
            onClick={() => setRoleSelection("broker")}
            className={`flex-1 py-3 text-sm font-bold rounded-lg transition-colors ${
              roleSelection === "broker" ? "bg-white text-blue-600 shadow-sm" : "text-gray-900 hover:text-black"
            }`}
          >
            I'm a Broker
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {roleSelection === "user" ? (
            <div className="grid grid-cols-2 gap-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
               <div>
                  <label className="block text-sm font-medium text-black mb-1">City Location</label>
                  <input type="text" required value={formData.location_name} onChange={e => setFormData({...formData, location_name: e.target.value})} className="w-full border p-2 rounded outline-none focus:ring-2 focus:ring-blue-500 text-black font-medium" />
               </div>
               <div>
                  <label className="block text-sm font-medium text-black mb-1">Purpose</label>
                  <select value={formData.purpose} onChange={e => setFormData({...formData, purpose: e.target.value})} className="w-full border p-2 rounded outline-none focus:ring-2 focus:ring-blue-500 text-black font-medium">
                    <option value="rent">Rent</option>
                    <option value="buy">Buy</option>
                    <option value="both">Both</option>
                  </select>
               </div>
               <div>
                  <label className="block text-sm font-medium text-black mb-1">Min Budget (₹)</label>
                  <input type="number" required value={formData.budget_min} onChange={e => setFormData({...formData, budget_min: parseInt(e.target.value)})} className="w-full border p-2 rounded outline-none focus:ring-2 focus:ring-blue-500 text-black font-medium" />
               </div>
               <div>
                  <label className="block text-sm font-medium text-black mb-1">Max Budget (₹)</label>
                  <input type="number" required value={formData.budget_max} onChange={e => setFormData({...formData, budget_max: parseInt(e.target.value)})} className="w-full border p-2 rounded outline-none focus:ring-2 focus:ring-blue-500 text-black font-medium" />
               </div>
               <div className="col-span-2">
                  <label className="block text-sm font-medium text-black mb-1">Preferred Property Type</label>
                  <select value={formData.preferred_type} onChange={e => setFormData({...formData, preferred_type: e.target.value})} className="w-full border p-2 rounded outline-none focus:ring-2 focus:ring-blue-500 text-black font-medium">
                    <option value="flat">Flat</option>
                    <option value="villa">Villa</option>
                    <option value="bungalow">Bungalow</option>
                    <option value="land">Land</option>
                  </select>
               </div>
            </div>
          ) : (
            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div>
                <label className="block text-sm font-medium text-black mb-1">
                  Locality Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Bandra West, Mumbai"
                  value={localityName}
                  onChange={(e) => setLocalityName(e.target.value)}
                  className="w-full border border-gray-300 p-3 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-black"
                />
                <p className="text-sm text-gray-500 mt-2">
                  As a registered broker, you will receive assignment notifications for properties listed in this area.
                </p>
              </div>
            </div>
          )}
          
          <button type="submit" disabled={loading || (roleSelection === 'broker' && !localityName)} className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors">
            {loading ? "Saving..." : roleSelection === "user" ? "Save Preferences" : "Register as Broker"}
          </button>
        </form>
      </div>
    </div>
  );
}
