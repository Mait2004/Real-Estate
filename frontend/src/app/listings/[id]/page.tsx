"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { MapPin, Maximize, BedDouble, Info, Heart, Edit } from "lucide-react";

export default function ListingDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [listing, setListing] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [inWishlist, setInWishlist] = useState(false);
  const [wishing, setWishing] = useState(false);
  const [brokerContact, setBrokerContact] = useState<any>(null);
  const [contactLoading, setContactLoading] = useState(false);

  useEffect(() => {
    const fetchListing = async () => {
      try {
        const res = await api.get(`/listings/${id}`);
        setListing(res.data.data);
      } catch (e) {
        console.error("Listing not found", e);
      }
      setLoading(false);
    };

    const checkWishlist = async () => {
      if (!user) return;
      try {
        const res = await api.get(`/wishlist`);
        const item = res.data.data.find((w: any) => w.listing_id === id);
        if (item) setInWishlist(true);
      } catch (e) {
        // ignore
      }
    };

    fetchListing();
    checkWishlist();
  }, [id, user]);

  const toggleWishlist = async () => {
    if (!user) return alert("Please log in first");
    setWishing(true);
    try {
      if (inWishlist) {
        await api.delete(`/wishlist/${id}`);
        setInWishlist(false);
      } else {
        await api.post(`/wishlist/${id}`);
        setInWishlist(true);
      }
    } catch (e) {
      alert("Error updating wishlist");
    }
    setWishing(false);
  };

  if (loading) return <div className="text-center py-20 text-gray-500">Loading...</div>;
  if (!listing) return <div className="text-center py-20 text-red-500 font-bold">Listing not found.</div>;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{listing.title}</h1>
          <div className="mt-2 flex items-center text-gray-600">
            <MapPin className="w-5 h-5 mr-1" />
            <span className="text-lg">{listing.address || listing.city}</span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-4xl font-extrabold text-blue-600">₹{listing.price.toLocaleString("en-IN")}</div>
          <div className="mt-1 inline-block px-3 py-1 bg-green-100 text-green-800 text-sm font-bold rounded-full uppercase tracking-wide">
            For {listing.purpose}
          </div>
        </div>
      </div>

      {/* Hero Image */}
      <div className="bg-gray-200 rounded-2xl h-96 w-full mb-8 overflow-hidden relative shadow-inner">
        {listing.images && listing.images.length > 0 ? (
          <img src={listing.images[0]} alt={listing.title} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
             No images available
          </div>
        )}
        
        {/* Wishlist button over image */}
        <div className="absolute top-4 right-4 flex gap-2">
           <button 
             onClick={toggleWishlist}
             disabled={wishing}
             className="bg-white/90 backdrop-blur-sm p-3 rounded-full shadow-lg hover:scale-110 transition-transform disabled:opacity-50"
             title="Add to wishlist"
           >
              <Heart className={`w-6 h-6 ${inWishlist ? 'fill-red-500 text-red-500' : 'text-gray-600'}`} />
           </button>
        </div>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        {/* Main Info */}
        <div className="md:col-span-2 space-y-8">
           <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
             <h2 className="text-xl font-bold border-b pb-4 mb-4 text-gray-900">Property Overview</h2>
             <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
               <div className="flex flex-col">
                  <span className="text-gray-500 flex items-center gap-1 text-sm"><Info className="w-4 h-4"/> Type</span>
                  <span className="font-semibold text-lg capitalize">{listing.type}</span>
               </div>
               <div className="flex flex-col">
                  <span className="text-gray-500 flex items-center gap-1 text-sm"><Maximize className="w-4 h-4"/> Area</span>
                  <span className="font-semibold text-lg">{listing.area_sqft} sqft</span>
               </div>
               <div className="flex flex-col">
                  <span className="text-gray-500 flex items-center gap-1 text-sm"><BedDouble className="w-4 h-4"/> Bedrooms</span>
                  <span className="font-semibold text-lg">{listing.bedrooms || "-"}</span>
               </div>
               <div className="flex flex-col">
                  <span className="text-gray-500 flex items-center gap-1 text-sm"><Info className="w-4 h-4"/> Status</span>
                  <span className="font-semibold text-lg capitalize">{listing.status}</span>
               </div>
             </div>
           </div>

           <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
              <h2 className="text-xl font-bold border-b pb-4 mb-4 text-gray-900">Description</h2>
              <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                 {listing.description || "No description provided."}
              </p>
           </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
           <div className="bg-blue-50 p-6 rounded-xl border border-blue-100">
              <h3 className="font-bold text-lg text-blue-900 mb-2">Interested?</h3>
              <p className="text-blue-800 text-sm mb-4">Contact the assigned broker for a viewing.</p>
              
              {!listing.broker_id ? (
                <div className="p-3 bg-white rounded text-sm text-gray-500 border text-center">
                  Locality broker assignment pending.
                </div>
              ) : brokerContact ? (
                <div className="bg-white p-4 rounded-lg border border-blue-200 shadow-sm animate-in fade-in zoom-in duration-300">
                  <div className="font-bold text-gray-900 text-lg mb-1">{brokerContact.name}</div>
                  <div className="text-sm text-gray-500 mb-3">{brokerContact.locality} Expert • ⭐ {brokerContact.rating}/5</div>
                  <a 
                    href={`mailto:${brokerContact.email}?subject=Inquiry about ${listing.title}`}
                    className="flex justify-center items-center w-full py-2 bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-lg font-bold transition-colors"
                  >
                    Email Broker
                  </a>
                </div>
              ) : (
                <button 
                  onClick={async () => {
                    if (!user) return alert("Please log in to contact the broker.");
                    setContactLoading(true);
                    try {
                      const res = await api.get(`/brokers/${listing.broker_id}/contact`);
                      setBrokerContact(res.data.data);
                    } catch (e) {
                      alert("Failed to fetch broker contact info");
                    }
                    setContactLoading(false);
                  }}
                  disabled={contactLoading}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold shadow-md transition-colors disabled:opacity-50"
                  title={!user ? "Please log in first" : ""}
                >
                  {contactLoading ? "Loading..." : "Contact Broker"}
                </button>
              )}
           </div>
           
           {(user?.id === listing.user_id || user?.role === "admin") && (
               <div className="bg-white p-6 rounded-xl border border-gray-200">
                  <h3 className="font-bold text-gray-900 mb-4 flex gap-2 items-center">
                    <Edit className="w-5 h-5 text-gray-500"/> Owner Actions
                  </h3>
                  <p className="text-sm text-gray-500 mb-4">You own this listing. You can update its details or upload new images.</p>
                  <button className="w-full py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg font-medium border border-gray-300">
                    Edit Listing
                  </button>
               </div>
           )}
        </div>
      </div>
    </div>
  );
}
