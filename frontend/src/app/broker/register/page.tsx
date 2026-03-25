"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, getAuthToken } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function BrokerRegistration() {
  const router = useRouter();
  const { user, login } = useAuth();
  const [localityName, setLocalityName] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Create a default rough polygon for the given locality (Mumbai area approx)
      // In a real app, this would use a map picker component
      const defaultPolygon = {
        type: "Polygon",
        coordinates: [
          [
            [72.82, 19.04],
            [72.85, 19.04],
            [72.85, 19.07],
            [72.82, 19.07],
            [72.82, 19.04],
          ],
        ],
      };

      await api.post("/brokers/register", {
        locality_name: localityName,
        locality_polygon: defaultPolygon,
      });

      // Refresh user context to get the new 'broker' role
      const token = getAuthToken();
      if (token) {
        await login(token);
      }
      
      router.push("/broker");
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to register as broker");
    }
    setLoading(false);
  };

  if (!user) return <div className="p-8 text-center text-red-500">Not logged in</div>;
  if (user.role === "broker") return <div className="p-8 text-center text-gray-600">You are already a broker.</div>;

  return (
    <div className="max-w-xl mx-auto px-4 py-12">
      <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-200">
        <h1 className="text-2xl font-bold mb-2">Become a Broker</h1>
        <p className="text-gray-500 mb-8">
          Join our network of verified brokers and start receiving property assignments in your area.
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Locality Name
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Bandra West, Mumbai"
              value={localityName}
              onChange={(e) => setLocalityName(e.target.value)}
              className="w-full border border-gray-300 p-3 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            />
            <p className="text-xs text-gray-400 mt-2">
              For this demo, a default geographical boundary will be assigned to this locality.
            </p>
          </div>

          <button
            type="submit"
            disabled={loading || !localityName.trim()}
            className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {loading ? "Registering..." : "Register as Broker"}
          </button>
        </form>
      </div>
    </div>
  );
}
