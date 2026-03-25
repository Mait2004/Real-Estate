"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Trash2, ExternalLink } from "lucide-react";

export default function WishlistPage() {
  const { user, loading: authLoading } = useAuth();
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading || !user) {
        if (!authLoading && !user) setLoading(false);
        return;
    }

    const fetchWishlist = async () => {
      try {
        const res = await api.get(`/wishlist`);
        setItems(res.data.data);
      } catch (e) {
        console.error("Failed to load wishlist", e);
      }
      setLoading(false);
    };
    fetchWishlist();
  }, [user, authLoading]);

  const remove = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    try {
      await api.delete(`/wishlist/${id}`);
      setItems(items.filter((item) => item.listing_id !== id));
    } catch (e) {
      alert("Error removing item");
    }
  };

  if (authLoading || loading) return <div className="text-center py-20">Loading...</div>;
  if (!user) return <div className="text-center py-20 text-red-500">Please log in to view wishlist.</div>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">My Wishlist</h1>
      {items.length === 0 ? (
          <div className="bg-white p-8 rounded-xl border border-gray-100 shadow-sm text-center text-gray-500">
             Your wishlist is empty. 
             <Link href="/listings" className="text-blue-600 font-bold ml-2">Browse listings</Link>
          </div>
      ) : (
          <div className="space-y-4">
            {items.map((item) => (
                <Link href={`/listings/${item.listing_id}`} key={item.id} className="block group">
                    <div className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-xl shadow-sm hover:border-blue-300 transition-colors">
                        <div className="flex flex-col">
                            <span className="font-bold text-lg text-gray-900 group-hover:text-blue-600 transition-colors">
                                {item.listing?.title || "Unknown Listing"}
                            </span>
                            <span className="text-gray-500 text-sm">{item.listing?.city} • ₹{item.listing?.price?.toLocaleString("en-IN")}</span>
                        </div>
                        <div className="flex items-center gap-4">
                            <button onClick={(e) => remove(item.listing_id, e)} className="text-red-400 hover:text-red-600 p-2">
                                <Trash2 className="w-5 h-5" />
                            </button>
                            <ExternalLink className="w-5 h-5 text-gray-400 group-hover:text-blue-600" />
                        </div>
                    </div>
                </Link>
            ))}
          </div>
      )}
    </div>
  );
}
