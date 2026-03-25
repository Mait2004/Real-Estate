"use client";

import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { Home, User, LogOut, PlusCircle, MessageCircle } from "lucide-react";

export default function Navbar() {
  const { user, loading, logout } = useAuth();

  return (
    <nav className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link href="/" className="flex-shrink-0 flex items-center gap-2">
              <Home className="w-6 h-6 text-blue-600" />
              <span className="font-bold text-xl text-gray-900">RealEstates</span>
            </Link>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <Link href="/listings" className="text-gray-900 border-transparent hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Browse
              </Link>
            </div>
          </div>
          <div className="flex items-center">
            {!loading && (
              <>
                {user ? (
                  <div className="flex items-center space-x-4">
                    {user.role === "broker" && (
                       <Link href="/broker" className="text-sm font-medium text-gray-700 hover:text-blue-600">Broker Panel</Link>
                    )}
                    {user.role === "admin" && (
                       <Link href="/admin" className="text-sm font-medium text-red-600 hover:text-red-800">Admin</Link>
                    )}
                    <Link href="/wishlist" className="text-sm font-medium text-gray-700 hover:text-blue-600">Wishlist</Link>
                    {user.role === "user" && (
                       <Link href="/broker/register" className="text-sm font-medium text-gray-700 hover:text-blue-600">Become a Broker</Link>
                    )}
                    {user.role === "user" && (
                       <Link href="/chat" className="text-sm font-medium text-purple-600 hover:text-purple-800 flex items-center gap-1">
                          <MessageCircle className="w-4 h-4" /> AI Chat
                       </Link>
                    )}
                    <Link href="/listings/add" className="text-sm font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1 bg-blue-50 px-3 py-1.5 rounded-full">
                       <PlusCircle className="w-4 h-4" /> Add Listing
                    </Link>
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold overflow-hidden">
                        {user.avatar_url ? (
                            <img src={user.avatar_url} alt="Avatar" className="w-full h-full object-cover" />
                        ) : (
                            <User className="w-4 h-4" />
                        )}
                      </div>
                      <span className="text-sm font-medium text-gray-700">{user.name || "User"}</span>
                    </div>
                    <button onClick={logout} className="text-gray-500 hover:text-gray-700 p-1">
                      <LogOut className="w-5 h-5" />
                    </button>
                  </div>
                ) : (
                  <div className="flex gap-2">
                    <a
                      href="http://localhost:8000/auth/google?role=user"
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
                    >
                      Login with Google
                    </a>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
