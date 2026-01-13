"use client";

import React, { useState, useEffect } from "react";
import ChatInterface from "@/components/ChatInterface";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";
const SESSION_STORAGE_KEY = "shopping_assistant_session_id";

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);

    // Get or create session ID
    let id = sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (!id) {
      // Generate new session ID
      id = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
      sessionStorage.setItem(SESSION_STORAGE_KEY, id);
    }
    setSessionId(id);
  }, []);

  const handleClearChat = () => {
    const newId = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    sessionStorage.setItem(SESSION_STORAGE_KEY, newId);
    setSessionId(newId);
  };

  if (!isClient || !sessionId) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-blue-50 to-gray-50">
        <div className="text-center">
          <div className="text-5xl mb-4">🛍️</div>
          <p className="text-gray-600 text-lg font-medium">Loading Shopping Assistant...</p>
          <div className="mt-4 flex justify-center gap-1">
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ChatInterface 
      key={sessionId}
      sessionId={sessionId} 
      backendUrl={BACKEND_URL} 
      onClearChat={handleClearChat}
    />
  );
}
