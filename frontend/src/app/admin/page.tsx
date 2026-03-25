"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Users, Building2, CheckCircle, RefreshCw, BadgeCheck } from "lucide-react";

export default function AdminPanel() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<"users" | "listings" | "brokers">("users");
  const [users, setUsers] = useState<any[]>([]);
  const [listings, setListings] = useState<any[]>([]);
  const [brokers, setBrokers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [assigningId, setAssigningId] = useState<string | null>(null);
  const [verifyingId, setVerifyingId] = useState<string | null>(null);

  useEffect(() => {
      const fetchAdminData = async () => {
         if (user?.role !== "admin") return;
         setLoading(true);
         try {
             const [uRes, lRes, bRes] = await Promise.all([
                 api.get("/admin/users"),
                 api.get("/admin/listings?page_size=100"),
                 api.get("/admin/brokers")
             ]);
             setUsers(uRes.data.data);
             setListings(lRes.data.data);
             setBrokers(bRes.data.data); // Keep all brokers, verified or not
         } catch (e) {
             console.log("Admin fetch error", e);
         }
         setLoading(false);
      };
      fetchAdminData();
  }, [user]);

  const handleBrokerChange = async (listingId: string, brokerId: string) => {
      if (!brokerId) return;
      setAssigningId(listingId);
      try {
          const res = await api.put(`/admin/listings/${listingId}/broker/${brokerId}`);
          setListings(listings.map(l => l.id === listingId ? { ...l, broker_id: brokerId } : l));
          alert("Broker assigned successfully!");
      } catch (e: any) {
          alert("Failed to assign broker: " + (e.response?.data?.detail || e.message));
      }
      setAssigningId(null);
  };

  const handleVerifyBroker = async (brokerId: string) => {
      setVerifyingId(brokerId);
      try {
          await api.put(`/brokers/${brokerId}/verify`);
          setBrokers(brokers.map(b => b.id === brokerId ? { ...b, verified: true } : b));
          alert("Broker verified successfully!");
      } catch (e: any) {
          alert("Failed to verify broker: " + (e.response?.data?.detail || e.message));
      }
      setVerifyingId(null);
  };

  const handleChangeListingStatus = async (listingId: string, status: string) => {
      try {
          await api.put(`/admin/listings/${listingId}/status?status=${status}`);
          setListings(listings.map(l => l.id === listingId ? { ...l, status } : l));
      } catch (e: any) {
          alert("Failed to change listing status: " + (e.response?.data?.detail || e.message));
      }
  };

  if (user?.role !== "admin") return <div className="text-center py-20 text-red-500">Access Denied. Admin role required.</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Control Panel</h1>
      
      {/* Tabs */}
      <div className="flex space-x-4 mb-6 border-b border-gray-200">
         <button 
            onClick={() => setActiveTab("users")}
            className={`pb-4 flex items-center gap-2 font-bold transition-colors ${activeTab === 'users' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
         >
            <Users className="w-5 h-5"/> Users
         </button>
         <button 
            onClick={() => setActiveTab("brokers")}
            className={`pb-4 flex items-center gap-2 font-bold transition-colors ${activeTab === 'brokers' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
         >
            <BadgeCheck className="w-5 h-5"/> Brokers
         </button>
         <button 
            onClick={() => setActiveTab("listings")}
            className={`pb-4 flex items-center gap-2 font-bold transition-colors ${activeTab === 'listings' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
         >
            <Building2 className="w-5 h-5"/> Property Listings
         </button>
      </div>

      <div className="bg-white rounded-xl shadow border border-gray-200 overflow-hidden">
        
        {loading ? (
            <div className="p-10 flex justify-center text-gray-400">
                <RefreshCw className="w-6 h-6 animate-spin" />
            </div>
        ) : activeTab === "users" ? (
            /* Users Tab */
            <>
                <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 font-bold text-gray-700">
                Registered Users ({users.length})
                </div>
                <div className="divide-y">
                {users.length === 0 ? (
                    <div className="p-6 text-center text-gray-500">No users found</div>
                ) : (
                    users.map(u => (
                        <div key={u.id} className="p-4 flex justify-between items-center hover:bg-gray-50 transition-colors">
                            <div className="flex flex-col">
                                <span className="font-bold text-gray-900">{u.name || "Unnamed User"}</span>
                                <span className="text-sm text-gray-900 font-medium">{u.email}</span>
                            </div>
                            <div className="flex gap-4 items-center">
                                <span className={`px-2 py-1 text-xs rounded uppercase font-bold tracking-wide
                                    ${u.role === 'admin' ? 'bg-red-100 text-red-800' : 
                                    u.role === 'broker' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'}`}>
                                    {u.role}
                                </span>
                                <button className="text-red-500 hover:text-red-700 text-sm font-medium border border-red-200 px-3 py-1 rounded hover:bg-red-50">
                                    Suspend
                                </button>
                            </div>
                        </div>
                    ))
                )}
                </div>
            </>
        ) : activeTab === "brokers" ? (
            /* Brokers Tab */
            <>
               <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 font-bold text-gray-700 flex justify-between">
                   <span>Broker Applications ({brokers.length})</span>
                   <span className="text-sm font-normal">Approve pending brokers</span>
                </div>
                <div className="divide-y">
                {brokers.length === 0 ? (
                    <div className="p-6 text-center text-gray-500">No brokers found</div>
                ) : (
                    brokers.map(b => (
                        <div key={b.id} className="p-4 flex justify-between items-center hover:bg-gray-50 transition-colors">
                            <div className="flex flex-col">
                                <span className="font-bold flex items-center gap-2 text-gray-900">
                                  {b.user_name || "Unnamed Broker"}
                                  {b.verified && <CheckCircle className="w-4 h-4 text-green-500" />}
                                </span>
                                <span className="text-sm text-gray-900 font-medium">{b.user_email} • Specializes in: {b.locality_name}</span>
                            </div>
                            <div className="flex gap-4 items-center">
                                {b.verified ? (
                                    <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-bold rounded-full uppercase">
                                        Verified
                                    </span>
                                ) : (
                                    <button 
                                      onClick={() => handleVerifyBroker(b.id)}
                                      disabled={verifyingId === b.id}
                                      className="py-1 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold shadow-md transition-colors disabled:opacity-50"
                                    >
                                        Verify Broker
                                    </button>
                                )}
                            </div>
                        </div>
                    ))
                )}
                </div>
            </>
        ) : (
            /* Listings Tab */
            <>
                <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 font-bold text-gray-700 flex justify-between">
                   <span>All Property Listings ({listings.length})</span>
                   <span className="text-sm font-normal">Manage Broker Assignments & Status</span>
                </div>
                <div className="overflow-x-auto">
                   <table className="w-full text-left border-collapse">
                      <thead>
                         <tr className="bg-gray-50 border-b border-gray-200 text-xs uppercase tracking-wider text-gray-500">
                            <th className="p-4">Property</th>
                            <th className="p-4">Location</th>
                            <th className="p-4">Status</th>
                            <th className="p-4">Assigned Broker</th>
                         </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                         {listings.map(l => (
                             <tr key={l.id} className="hover:bg-gray-50">
                                 <td className="p-4">
                                     <div className="font-bold text-gray-900">{l.title}</div>
                                     <div className="text-xs text-gray-900 font-medium capitalize">{l.type} - ₹{l.price.toLocaleString('en-IN')}</div>
                                 </td>
                                 <td className="p-4 text-sm text-gray-900 font-medium">
                                     {l.city}
                                 </td>
                                 <td className="p-4">
                                     <select
                                         value={l.status}
                                         onChange={(e) => handleChangeListingStatus(l.id, e.target.value)}
                                         className={`text-xs font-bold uppercase rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 
                                            ${l.status === 'verified' ? 'bg-green-50 text-green-800' : 
                                              l.status === 'active' ? 'bg-blue-50 text-blue-800' : 'bg-yellow-50 text-yellow-800'}`}
                                     >
                                         <option value="pending">Pending</option>
                                         <option value="active">Active</option>
                                         <option value="verified">Verified</option>
                                         <option value="suspended">Suspended</option>
                                     </select>
                                 </td>
                                 <td className="p-4">
                                     <select 
                                         value={l.broker_id || ""} 
                                         onChange={(e) => handleBrokerChange(l.id, e.target.value)}
                                         disabled={assigningId === l.id}
                                         className={`w-full text-sm border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 ${!l.broker_id ? 'border-red-300 bg-red-50' : ''}`}
                                     >
                                         <option value="" disabled>-- Assign a Broker --</option>
                                         {brokers.filter(b => b.verified).map(b => (
                                             <option key={b.id} value={b.id}>
                                                {b.user_name} ({b.locality_name})
                                             </option>
                                         ))}
                                     </select>
                                     {assigningId === l.id && <span className="text-xs text-blue-500 mt-1 block">Assigning...</span>}
                                 </td>
                             </tr>
                         ))}
                      </tbody>
                   </table>
                   {listings.length === 0 && <div className="p-6 text-center text-gray-500">No listings found</div>}
                </div>
            </>
        )}
      </div>
    </div>
  );
}
