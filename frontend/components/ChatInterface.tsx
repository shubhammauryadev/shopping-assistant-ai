"use client";

import React, { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import ProductCards from "./ProductCards";
import CartSummary from "./CartSummary";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  parsed?: {
    type: "text" | "products" | "comparison" | "cart";
    data: any;
  };
}

interface ChatInterfaceProps {
  sessionId: string;
  backendUrl: string;
  onClearChat: () => void;
}

export default function ChatInterface({
  sessionId,
  backendUrl,
  onClearChat,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${backendUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantContent = "";
      const assistantId = (Date.now() + 1).toString();
      let assistantMessage: Message = {
        id: assistantId,
        role: "assistant",
        content: "",
      };

      setMessages((prev) => [...prev, assistantMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const jsonStr = line.slice(6);
            try {
              const data = JSON.parse(jsonStr);

              if (data.done) {
                break;
              }

              if (data.error) {
                setError(data.error);
                break;
              }

              if (data.text) {
                assistantContent += data.text;
                assistantMessage.content = assistantContent;

                // Try to parse complete JSON responses
                try {
                  const parsed = JSON.parse(assistantContent);
                  if (parsed.type && parsed.data) {
                    assistantMessage.parsed = parsed;
                  }
                } catch {
                  // Not complete JSON yet, will retry on next chunk
                }

                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantId ? { ...assistantMessage } : m
                  )
                );
              }
            } catch {
              // Invalid JSON in this line, skip
            }
          }
        }
      }

      // Final attempt to parse as JSON
      if (!assistantMessage.parsed) {
        try {
          const parsed = JSON.parse(assistantContent);
          if (parsed.type && parsed.data) {
            assistantMessage.parsed = parsed;
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId ? { ...assistantMessage } : m
              )
            );
          }
        } catch {
          // Not JSON, will display as plain text
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header - sticky on mobile */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-3 sm:px-6 sm:py-4 flex-shrink-0 flex justify-between items-center">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold">Shopping Assistant</h1>
          <p className="text-xs sm:text-sm opacity-90">Find & manage products</p>
        </div>
        <Button 
          variant="secondary" 
          size="sm" 
          onClick={onClearChat}
          className="text-white bg-white/20 hover:bg-white/30 border-0"
        >
          Clear Chat
        </Button>
      </div>

      {/* Jumbotron Container - centered with responsive margins */}
      <div className="flex-1 overflow-y-auto flex flex-col">
        <div className="mx-auto w-full max-w-4xl flex flex-col h-full px-3 sm:px-4 lg:px-6">
          {/* Messages area - scrollable with safe padding for input */}
      <div className="flex-1 overflow-y-auto py-4 space-y-3 sm:space-y-4 pb-2">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-12">
            <p className="text-sm sm:text-base">
              Ask me to search for products or manage your cart!
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-xs sm:max-w-md lg:max-w-2xl ${
                message.role === "user"
                  ? "bg-blue-500 text-white rounded-2xl"
                  : "bg-white text-gray-900 rounded-lg border border-gray-200 shadow-sm"
              } px-4 py-2 sm:px-4 sm:py-3 shadow-sm`}
            >
              {message.parsed ? (
                <RenderMessage message={message} onSetInput={setInput} />
              ) : (
                <p className="whitespace-pre-wrap text-sm sm:text-base break-words">
                  {message.content}
                </p>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-600 rounded-lg px-4 py-3 text-sm border border-gray-200 shadow-sm">
              <div className="flex gap-1">
                <span>Assistant is typing</span>
                <span className="animate-bounce">.</span>
                <span className="animate-bounce" style={{ animationDelay: "0.1s" }}>.</span>
                <span className="animate-bounce" style={{ animationDelay: "0.2s" }}>.</span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-sm">
            ⚠️ Error: {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area - sticky at bottom with safe keyboard spacing */}
      <div className="border-t border-gray-200 bg-gradient-to-b from-white to-gray-50 py-3 sm:py-4 flex-shrink-0">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <Input
            type="text"
            placeholder="Message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            className="flex-1 text-sm h-10 sm:h-11"
            autoComplete="off"
          />
          <Button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-3 sm:px-6 h-10 sm:h-11 text-sm sm:text-base font-medium"
          >
            {loading ? "..." : "Send"}
          </Button>
        </form>
      </div>
        </div>
      </div>
    </div>
  );
}

function RenderMessage({ message, onSetInput }: { message: Message; onSetInput: (value: string) => void }) {
  const parsed = message.parsed;

  if (!parsed) {
    return <p className="whitespace-pre-wrap text-sm sm:text-base break-words">{message.content}</p>;
  }

  switch (parsed.type) {
    case "products":
      return (
        <div className="space-y-2 sm:space-y-3">
          {parsed.data.text && (
            <p className="whitespace-pre-wrap text-sm sm:text-base break-words">{parsed.data.text}</p>
          )}
          {parsed.data.results && (
            <ProductCards products={parsed.data.results} />
          )}
        </div>
      );

    case "cart":
      return (
        <div className="space-y-2 sm:space-y-3">
          {parsed.data.text && (
            <p className="whitespace-pre-wrap text-sm sm:text-base break-words">{parsed.data.text}</p>
          )}
          {parsed.data.items && (
            <CartSummary
              cart={parsed.data}
              onClearCart={() => onSetInput("Clear my cart")}
            />
          )}
        </div>
      );

    case "comparison":
      return (
        <div className="space-y-2 sm:space-y-3">
          {parsed.data.text && (
            <p className="whitespace-pre-wrap text-sm sm:text-base break-words">{parsed.data.text}</p>
          )}
          {parsed.data.products && (
            <ProductCards products={parsed.data.products} />
          )}
        </div>
      );

    case "text":
    default:
      return <p className="whitespace-pre-wrap text-sm sm:text-base break-words">{parsed.data.text}</p>;
  }
}
