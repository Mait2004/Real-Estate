"use client";

import { useAuth } from "@/context/AuthContext";
import Link from "next/link";
import { Search, Home, Building } from "lucide-react";

export default function HomePage() {
  const { user, loading } = useAuth();

  return (
    <div className="bg-white">
      {/* Hero section */}
      <div className="relative bg-gray-900">
        <div className="absolute inset-0 overflow-hidden">
          <img
            src="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=2075&q=80"
            alt="Modern house"
            className="h-full w-full object-cover opacity-40"
          />
        </div>
        <div className="relative max-w-7xl mx-auto py-24 px-4 sm:py-32 sm:px-6 lg:px-8 flex flex-col items-center text-center">
          <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl">
            Find your dream property
          </h1>
          <p className="mt-6 text-xl text-gray-300 max-w-3xl">
            Discover the perfect place to call home from our vast collection of verified listings across the city.
          </p>
          <div className="mt-10 flex gap-4">
            <Link
              href="/listings?purpose=buy"
              className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-gray-900 bg-white hover:bg-gray-50 md:text-lg"
            >
              Buy
            </Link>
            <Link
              href="/listings?purpose=rent"
              className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:text-lg"
            >
              Rent
            </Link>
          </div>
        </div>
      </div>

      {/* Feature section */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center">
              <div className="p-3 bg-blue-100 rounded-full mb-4">
                <Search className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Smart Search</h3>
              <p className="text-gray-500">Filter by location, budget, and property type to find exactly what you need.</p>
            </div>
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center">
              <div className="p-3 bg-blue-100 rounded-full mb-4">
                <Building className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Verified Listings</h3>
              <p className="text-gray-500">Every listing is verified by our network of trusted local brokers.</p>
            </div>
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center">
              <div className="p-3 bg-blue-100 rounded-full mb-4">
                <Home className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">AI Assistant</h3>
              <p className="text-gray-500">Chat with our AI bot to get personalized property recommendations based on your profile.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
