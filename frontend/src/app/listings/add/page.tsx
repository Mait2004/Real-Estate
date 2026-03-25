"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { ImagePlus, MapPin, UploadCloud, CheckCircle } from "lucide-react";

export default function AddListingPage() {
  const router = useRouter();
  const { user } = useAuth();
  
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    price: "",
    city: "Mumbai",
    address: "",
    type: "flat",
    purpose: "rent",
    area_sqft: "",
    bedrooms: "",
    lat: 19.076,
    lng: 72.877
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return alert("Must be logged in.");
    setLoading(true);
    try {
      // 1. Create Listing
      const payload = {
        ...formData,
        price: parseInt(formData.price),
        area_sqft: parseInt(formData.area_sqft),
        bedrooms: formData.bedrooms ? parseInt(formData.bedrooms) : null,
      };

      const res = await api.post("/listings", payload);
      const newListingId = res.data.data.id;

      // 2. Upload Images if any
      if (files.length > 0) {
        const formDataUpload = new FormData();
        files.forEach(f => formDataUpload.append("files", f));
        
        await api.post(`/listings/${newListingId}/images`, formDataUpload, {
          headers: { "Content-Type": "multipart/form-data" }
        });
      }

      setSuccess(true);
      setTimeout(() => {
         router.push(`/listings/${newListingId}`);
      }, 2000);

    } catch (err: any) {
      console.error(err);
      alert("Failed to create listing: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  if (!user) return <div className="text-center py-20 text-red-500 font-bold">Please log in to add a listing.</div>;

  if (success) {
      return (
          <div className="max-w-2xl mx-auto py-20 px-4 text-center">
              <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-6" />
              <h1 className="text-3xl font-bold text-gray-900 mb-4">Listing Published!</h1>
              <p className="text-gray-600 mb-8">Your property has been listed and assigned a broker. Redirecting...</p>
          </div>
      );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="bg-white rounded-2xl shadow border border-gray-200 p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Create New Listing</h1>
        <p className="text-gray-600 mb-8">Fill out the details below to publish your property to the platform.</p>

        <form onSubmit={handleSubmit} className="space-y-6">
          
          <div className="space-y-4">
              <h2 className="text-xl font-bold text-gray-900 border-b pb-2">Basic Details</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                    <label className="block text-sm font-bold text-gray-900 mb-1">Title</label>
                    <input type="text" required value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} placeholder="e.g. Spacious 3BHK in Bandra" className="w-full border p-3 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div className="md:col-span-2">
                    <label className="block text-sm font-bold text-gray-900 mb-1">Description</label>
                    <textarea required rows={4} value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} placeholder="Describe the property..." className="w-full border p-3 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 outline-none"></textarea>
                </div>
                <div>
                    <label className="block text-sm font-bold text-gray-900 mb-1">Price (₹)</label>
                    <input type="number" required value={formData.price} onChange={e => setFormData({...formData, price: e.target.value})} placeholder="e.g. 50000" className="w-full border p-3 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                    <label className="block text-sm font-bold text-gray-900 mb-1">Area (sq.ft)</label>
                    <input type="number" required value={formData.area_sqft} onChange={e => setFormData({...formData, area_sqft: e.target.value})} placeholder="e.g. 1200" className="w-full border p-3 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                    <label className="block text-sm font-bold text-gray-900 mb-1">Bedrooms</label>
                    <input type="number" value={formData.bedrooms} onChange={e => setFormData({...formData, bedrooms: e.target.value})} placeholder="e.g. 3" className="w-full border p-3 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                    <label className="block text-sm font-bold text-gray-900 mb-1">Property Type</label>
                    <select value={formData.type} onChange={e => setFormData({...formData, type: e.target.value})} className="w-full border p-3 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 outline-none bg-white">
                        <option value="flat">Flat</option>
                        <option value="villa">Villa</option>
                        <option value="bungalow">Bungalow</option>
                        <option value="land">Land</option>
                    </select>
                </div>
                <div>
                    <label className="block text-sm font-bold text-gray-900 mb-1">Purpose</label>
                    <select value={formData.purpose} onChange={e => setFormData({...formData, purpose: e.target.value})} className="w-full border p-3 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 outline-none bg-white">
                        <option value="rent">For Rent</option>
                        <option value="buy">For Sale</option>
                    </select>
                </div>
              </div>
          </div>

          <div className="space-y-4">
              <h2 className="text-xl font-bold text-gray-900 border-b pb-2 pt-4">Location</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-bold text-gray-900 mb-1">City</label>
                    <input type="text" required value={formData.city} onChange={e => setFormData({...formData, city: e.target.value})} className="w-full border p-3 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div className="md:col-span-2">
                    <label className="block text-sm font-bold text-gray-900 mb-1">Detailed Address</label>
                    <input type="text" required value={formData.address} onChange={e => setFormData({...formData, address: e.target.value})} placeholder="Full address" className="w-full border p-3 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
              </div>
          </div>

          <div className="space-y-4">
              <h2 className="text-xl font-bold text-gray-900 border-b pb-2 pt-4">Photos</h2>
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:bg-gray-50 transition-colors">
                  <ImagePlus className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-900 font-medium mb-2">Upload property images</p>
                  <p className="text-gray-500 text-sm mb-4">Supported formats: JPG, PNG, WEBP</p>
                  <input 
                      type="file" 
                      multiple 
                      accept="image/*"
                      onChange={handleFileChange}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 mx-auto max-w-xs cursor-pointer"
                  />
                  {files.length > 0 && <div className="mt-4 text-sm font-bold text-green-600">{files.length} file(s) selected</div>}
              </div>
          </div>

          <button 
              type="submit" 
              disabled={loading}
              className="w-full py-4 bg-blue-600 text-white text-lg font-bold rounded-xl hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2 transition-transform active:scale-[0.98]"
          >
              {loading ? <span className="animate-pulse">Publishing...</span> : <><UploadCloud className="w-5 h-5" /> Publish Property</>}
          </button>
        </form>
      </div>
    </div>
  );
}
