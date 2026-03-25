"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { CheckCircle, Bell, MapPin, Home, Clock, Eye } from "lucide-react";

interface Listing {
  id: string;
  title: string;
  price: number;
  city: string;
  type: string;
  purpose: string;
  area_sqft: number;
  bedrooms: number | null;
  images: string[] | null;
  status: string;
  broker_id: string | null;
}

interface Notification {
  id: string;
  broker_id: string;
  user_id: string | null;
  listing_id: string | null;
  type: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export default function BrokerDashboard() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("assignments");
  const [assignments, setAssignments] = useState<Listing[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loadingAssignments, setLoadingAssignments] = useState(true);
  const [loadingNotifications, setLoadingNotifications] = useState(true);
  const [verifyingId, setVerifyingId] = useState<string | null>(null);

  const fetchAssignments = useCallback(async () => {
    setLoadingAssignments(true);
    try {
      const res = await api.get("/brokers/my-listings");
      setAssignments(res.data?.data || []);
    } catch (e) {
      console.error("Failed to fetch assignments", e);
    }
    setLoadingAssignments(false);
  }, []);

  const fetchNotifications = useCallback(async () => {
    setLoadingNotifications(true);
    try {
      const [notifRes, countRes] = await Promise.all([
        api.get("/notifications"),
        api.get("/notifications/unread-count"),
      ]);
      setNotifications(notifRes.data?.data || []);
      setUnreadCount(countRes.data?.data || 0);
    } catch (e) {
      console.error("Failed to fetch notifications", e);
    }
    setLoadingNotifications(false);
  }, []);

  useEffect(() => {
    if (user?.role !== "broker") return;
    fetchAssignments();
    fetchNotifications();
  }, [user, fetchAssignments, fetchNotifications]);

  const markAsRead = async (notifId: string) => {
    try {
      await api.put(`/notifications/${notifId}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.id === notifId ? { ...n, is_read: true } : n))
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch (e) {
      console.error("Failed to mark as read", e);
    }
  };

  const handleVerifyListing = async (listingId: string, brokerId: string) => {
    setVerifyingId(listingId);
    try {
      await api.put(`/brokers/${brokerId}/listing/${listingId}/verify`);
      setAssignments(assignments.map(a => a.id === listingId ? { ...a, status: "verified" } : a));
      alert("Listing marked as verified!");
    } catch (e: any) {
      alert("Failed to verify listing: " + (e.response?.data?.detail || e.message));
    }
    setVerifyingId(null);
  };

  if (user?.role !== "broker")
    return (
      <div className="text-center py-20 text-red-500">
        Access Denied. Broker role required.
      </div>
    );

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Broker Dashboard</h1>
      </div>

      <div className="flex border-b mb-6 gap-6">
        <button
          className={`pb-4 text-sm font-bold ${
            activeTab === "assignments"
              ? "text-blue-600 border-b-2 border-blue-600"
              : "text-gray-500 hover:text-gray-700"
          }`}
          onClick={() => setActiveTab("assignments")}
        >
          My Assignments ({assignments.length})
        </button>
        <button
          className={`pb-4 text-sm font-bold relative ${
            activeTab === "notifications"
              ? "text-blue-600 border-b-2 border-blue-600"
              : "text-gray-500 hover:text-gray-700"
          }`}
          onClick={() => setActiveTab("notifications")}
        >
          <span className="flex items-center gap-1.5">
            <Bell className="w-4 h-4" />
            Notifications
            {unreadCount > 0 && (
              <span className="bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </span>
        </button>
        <button
          className={`pb-4 text-sm font-bold ${
            activeTab === "profile"
              ? "text-blue-600 border-b-2 border-blue-600"
              : "text-gray-500 hover:text-gray-700"
          }`}
          onClick={() => setActiveTab("profile")}
        >
          Locality Profile
        </button>
      </div>

      {/* Assignments Tab */}
      {activeTab === "assignments" && (
        <div>
          {loadingAssignments ? (
            <div className="flex justify-center py-16">
              <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : assignments.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center text-gray-500">
              <CheckCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-lg">No active assignments at the moment.</p>
              <p className="text-sm mt-2">
                When a user posts a listing in your managed locality, it will
                appear here.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {assignments.map((listing) => (
                <div
                  key={listing.id}
                  className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow flex flex-col"
                >
                  <div className="h-40 w-full bg-gray-200 overflow-hidden shrink-0">
                    {listing.images && listing.images.length > 0 ? (
                      <img
                        src={listing.images[0]}
                        alt={listing.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        <Home className="w-10 h-10 opacity-50" />
                      </div>
                    )}
                  </div>
                  <div className="p-4 flex flex-col flex-grow">
                    <h3
                      className="font-bold text-gray-900 truncate"
                      title={listing.title}
                    >
                      {listing.title}
                    </h3>
                    <div className="flex items-center text-sm text-gray-900 font-medium mt-1">
                      <MapPin className="w-3.5 h-3.5 mr-1" />
                      {listing.city}
                    </div>
                    <div className="flex justify-between items-center mt-3 mb-2">
                      <span className="text-blue-600 font-bold">
                        ₹{listing.price.toLocaleString("en-IN")}
                      </span>
                      <span
                        className={`text-xs font-bold px-2 py-1 rounded capitalize ${
                          listing.status === "active"
                            ? "bg-green-100 text-green-700"
                            : listing.status === "verified"
                            ? "bg-blue-100 text-blue-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}
                      >
                        {listing.status}
                      </span>
                    </div>

                    <div className="mt-auto pt-4 border-t border-gray-100">
                        {listing.status !== "verified" ? (
                            <button
                                onClick={() => handleVerifyListing(listing.id, listing.broker_id!)}
                                disabled={verifyingId === listing.id}
                                className="w-full py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded text-sm font-bold flex justify-center items-center gap-2 transition-colors disabled:opacity-50"
                            >
                                <CheckCircle className="w-4 h-4" />
                                {verifyingId === listing.id ? "Verifying..." : "Verify Listing"}
                            </button>
                        ) : (
                            <div className="w-full py-2 bg-gray-50 text-gray-400 rounded text-sm font-bold flex justify-center items-center gap-2">
                                <CheckCircle className="w-4 h-4 text-green-500" />
                                Verified Successfully
                            </div>
                        )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === "notifications" && (
        <div>
          {loadingNotifications ? (
            <div className="flex justify-center py-16">
              <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : notifications.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center text-gray-500">
              <Bell className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-lg">No notifications yet.</p>
              <p className="text-sm mt-2">
                You'll be notified when users request you as a broker or you're
                assigned new listings.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {notifications.map((notif) => (
                <div
                  key={notif.id}
                  className={`p-4 rounded-xl border flex items-start gap-4 transition-all ${
                    notif.is_read
                      ? "bg-white border-gray-200"
                      : "bg-blue-50 border-blue-200 shadow-sm"
                  }`}
                >
                  <div
                    className={`p-2 rounded-full shrink-0 ${
                      notif.type === "new_assignment"
                        ? "bg-green-100 text-green-600"
                        : notif.type === "broker_request"
                        ? "bg-purple-100 text-purple-600"
                        : "bg-blue-100 text-blue-600"
                    }`}
                  >
                    {notif.type === "new_assignment" ? (
                      <Home className="w-5 h-5" />
                    ) : (
                      <Bell className="w-5 h-5" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-gray-900 text-sm">{notif.message}</p>
                    <div className="flex items-center gap-2 mt-1 text-xs text-gray-500 font-medium">
                      <Clock className="w-3 h-3" />
                      {new Date(notif.created_at).toLocaleString()}
                    </div>
                  </div>
                  {!notif.is_read && (
                    <button
                      onClick={() => markAsRead(notif.id)}
                      className="shrink-0 text-blue-600 hover:text-blue-800 p-1.5 rounded-lg hover:bg-blue-100 transition-colors"
                      title="Mark as read"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Profile Tab */}
      {activeTab === "profile" && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 max-w-2xl">
          <h2 className="text-xl font-bold mb-4">Your Verified Locality</h2>
          <div className="bg-gray-50 p-4 rounded-lg border">
            <div className="flex justify-between mb-2">
              <span className="text-gray-500">Status</span>
              <span className="text-green-600 font-bold bg-green-100 px-2 rounded">
                Verified
              </span>
            </div>
            <div className="flex justify-between mb-2">
              <span className="text-gray-500">Total Assignments Handled</span>
              <span className="font-bold">{assignments.length}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
