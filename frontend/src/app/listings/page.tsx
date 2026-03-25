"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { MapPin, Home, IndianRupee } from "lucide-react";

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
}

export default function ListingsPage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ purpose: "", city: "", type: "" });

  useEffect(() => {
    const fetchListings = async () => {
      setLoading(true);
      try {
        const query = new URLSearchParams();
        if (filters.purpose) query.append("purpose", filters.purpose);
        if (filters.city) query.append("city", filters.city);
        if (filters.type) query.append("type", filters.type);

        const res = await api.get(`/listings?${query.toString()}`);
        if (res.data?.data) {
           setListings(res.data.data);
        } else {
           setListings([]);
        }
      } catch (e) {
        console.error("Failed to fetch listings", e);
      }
      setLoading(false);
    };
    fetchListings();
  }, [filters]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <h1 className="text-3xl font-bold text-gray-900">Browse Properties</h1>
        
        {/* Filters */}
        <div className="flex gap-2 w-full md:w-auto overflow-x-auto">
          <select 
            className="border-gray-300 rounded-md shadow-sm text-sm border p-2"
            value={filters.purpose}
            onChange={(e) => setFilters({ ...filters, purpose: e.target.value })}
          >
            <option value="">Any Purpose</option>
            <option value="buy">Buy</option>
            <option value="rent">Rent</option>
          </select>

          <select 
            className="border-gray-300 rounded-md shadow-sm text-sm border p-2"
            value={filters.type}
            onChange={(e) => setFilters({ ...filters, type: e.target.value })}
          >
            <option value="">Any Type</option>
            <option value="flat">Flat</option>
            <option value="villa">Villa</option>
            <option value="land">Land</option>
            <option value="bungalow">Bungalow</option>
          </select>

          <input 
            type="text"
            placeholder="City..."
            className="border-gray-300 rounded-md shadow-sm text-sm border p-2 w-32"
            value={filters.city}
            onChange={(e) => setFilters({ ...filters, city: e.target.value })}
          />
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : listings.length === 0 ? (
        <div className="text-center py-20 text-gray-500 bg-white rounded-lg border border-gray-100">
           No listings found matching your criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {listings.map((listing) => (
            <Link href={`/listings/${listing.id}`} key={listing.id} className="group">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
                <div className="aspect-w-16 aspect-h-10 w-full overflow-hidden bg-gray-200">
                  {listing.images && listing.images.length > 0 ? (
                    <img
                      src={listing.images[0]}
                      alt={listing.title}
                      className="h-48 w-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  ) : (
                    <div className="h-48 w-full flex items-center justify-center bg-gray-100 text-gray-400">
                      <Home className="w-12 h-12 opacity-50" />
                    </div>
                  )}
                  <div className="absolute top-2 left-2">
                    <span className={`px-2 py-1 text-xs font-bold rounded shadow-sm ${listing.purpose === 'rent' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'}`}>
                        For {listing.purpose.charAt(0).toUpperCase() + listing.purpose.slice(1)}
                    </span>
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="text-lg font-bold text-gray-900 truncate" title={listing.title}>
                    {listing.title}
                  </h3>
                  <div className="mt-1 flex items-center text-sm text-gray-500">
                    <MapPin className="w-4 h-4 mr-1 shrink-0" />
                    <span className="truncate">{listing.city}</span>
                  </div>
                  <div className="mt-3 flex items-center justify-between">
                    <div className="flex items-center text-lg font-bold text-blue-600">
                        <IndianRupee className="w-5 h-5 mr-0.5" />
                        {listing.price.toLocaleString("en-IN")}
                    </div>
                    <div className="text-sm font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {listing.area_sqft} sqft
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
