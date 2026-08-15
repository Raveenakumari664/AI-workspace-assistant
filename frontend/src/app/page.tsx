"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "ai";
  text: string;
  time: string;
  failed?: boolean;
}

const suggestedPrompts = [
  "What's on my calendar today?",
  "Show my unread emails",
  "Find files in my Drive",
];

export default function Home() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOnline, setIsOnline] = useState<boolean | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, loading]);

  // Backend health check — har 10 second mein check karta hai
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/health");
        setIsOnline(res.ok);
      } catch {
        setIsOnline(false);
      }
    };
    checkBackend();
    const interval = setInterval(checkBackend, 10000);
    return () => clearInterval(interval);
  }, []);

  // Textarea auto-resize
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const getTime = () =>
    new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  const sendMessage = async (customText?: string) => {
    const textToSend = customText ?? message;
    if (!textToSend.trim() || loading) return;

    const userMessage: Message = { role: "user", text: textToSend, time: getTime() };
    setChatHistory((prev) => [...prev, userMessage]);
    setMessage("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage.text }),
      });

      if (!response.ok) throw new Error("Backend error");

      const data = await response.json();
      setChatHistory((prev) => [...prev, { role: "ai", text: data.response, time: getTime() }]);
    } catch (error) {
      setChatHistory((prev) => [
        ...prev,
        {
          role: "ai",
          text: "⚠️ Something went wrong. The AI service might be busy.",
          time: getTime(),
          failed: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const retryLastMessage = () => {
    const lastUserMessage = [...chatHistory].reverse().find((m) => m.role === "user");
    if (lastUserMessage) {
      setChatHistory((prev) => prev.filter((m) => !m.failed));
      sendMessage(lastUserMessage.text);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const clearChat = () => setChatHistory([]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-gray-950 to-gray-900 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4 bg-gray-950/80 backdrop-blur flex justify-between items-center">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">🤖 AI Workspace Assistant</h1>
          <div className="flex items-center gap-2 mt-1">
            <span
              className={`w-2 h-2 rounded-full ${
                isOnline === null ? "bg-gray-500" : isOnline ? "bg-green-500" : "bg-red-500"
              }`}
            ></span>
            <p className="text-sm text-gray-500">
              {isOnline === null ? "Checking..." : isOnline ? "Backend connected" : "Backend offline"}
            </p>
          </div>
        </div>
        {chatHistory.length > 0 && (
          <button
            onClick={clearChat}
            className="text-xs text-gray-400 hover:text-red-400 border border-gray-700 hover:border-red-400 px-3 py-1.5 rounded-lg transition"
          >
            Clear chat
          </button>
        )}
      </header>

      {/* Chat area */}
      <main className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-2xl mx-auto flex flex-col gap-4">
          {chatHistory.length === 0 && (
            <div className="text-center text-gray-500 mt-16">
              <p className="text-lg mb-4">👋 Say hello to get started</p>
              <div className="flex flex-col gap-2 items-center">
                {suggestedPrompts.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => sendMessage(prompt)}
                    className="text-sm bg-gray-800 hover:bg-gray-700 text-gray-300 px-4 py-2 rounded-full transition"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          <AnimatePresence>
            {chatHistory.map((msg, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
                className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
              >
                <div
                  className={`group max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white rounded-br-sm"
                      : msg.failed
                      ? "bg-red-950/50 border border-red-900 text-red-200 rounded-bl-sm"
                      : "bg-gray-800 text-gray-100 rounded-bl-sm"
                  }`}
                >
                  {msg.role === "ai" ? (
                    <div className="prose prose-invert prose-sm max-w-none">
                      <ReactMarkdown>{msg.text}</ReactMarkdown>
                    </div>
                  ) : (
                    <span className="whitespace-pre-wrap">{msg.text}</span>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-1 px-1">
                  <span className="text-[11px] text-gray-500">{msg.time}</span>
                  {msg.role === "ai" && !msg.failed && (
                    <button
                      onClick={() => copyToClipboard(msg.text)}
                      className="text-[11px] text-gray-500 hover:text-gray-300 transition"
                    >
                      Copy
                    </button>
                  )}
                  {msg.failed && (
                    <button
                      onClick={retryLastMessage}
                      className="text-[11px] text-blue-400 hover:text-blue-300 transition font-medium"
                    >
                      ↻ Retry
                    </button>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="bg-gray-800 px-4 py-3 rounded-2xl rounded-bl-sm flex gap-1 items-center">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input area */}
      <footer className="border-t border-gray-800 px-4 py-4 bg-gray-950/80 backdrop-blur">
        <div className="max-w-2xl mx-auto flex gap-2 items-end">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message... (Shift+Enter for new line)"
            rows={1}
            className="flex-1 bg-gray-800 text-gray-100 placeholder-gray-500 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-blue-600 transition resize-none max-h-32 overflow-y-auto"
          />
          <button
            onClick={() => sendMessage()}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-5 py-3 rounded-xl font-medium transition"
          >
            Send
          </button>
        </div>
      </footer>
    </div>
  );
}