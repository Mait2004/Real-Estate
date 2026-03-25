"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function AuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();

  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      login(token);
      router.push("/");
    } else {
      router.push("/?error=auth_failed");
    }
  }, [searchParams, login, router]);

  return (
    <div className="flex h-[80vh] items-center justify-center">
      <div className="text-xl font-medium text-gray-700">Logging you in...</div>
    </div>
  );
}
