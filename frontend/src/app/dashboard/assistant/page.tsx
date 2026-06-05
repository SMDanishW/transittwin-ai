"use client";
import { useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const EXAMPLE_QUESTIONS = [
  "What active disruptions are there right now?",
  "How many live vehicles are running and how many are late?",
  "Simulate tram line 7 delay near Pasila during morning peak.",
  "What are alternative routes if metro is disrupted near Kamppi?",
];

interface Message {
  role: "user" | "assistant";
  text: string;
  toolCalls?: string[];
}

export default function AssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      text: "Hello! I'm TransitTwin AI. I can help you analyse HSL disruptions, simulate route impacts, and find alternatives. Ask me anything about public transport in Helsinki, Espoo, or Vantaa.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  async function sendMessage() {
    if (!input.trim() || loading) return;
    const question = input.trim();
    setInput("");

    // Build history from all messages except the initial greeting
    const history = messages.slice(1).map((m) => ({
      role: m.role,
      content: m.text,
    }));

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setLoading(true);
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);

    try {
      const res = await fetch(`${API_URL}/api/agent/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, history }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.detail ?? `Server error ${res.status}`);
      }
      const data: { answer: string; tool_calls_made: string[] } = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer,
          toolCalls: data.tool_calls_made,
        },
      ]);
    } catch (err: unknown) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: `⚠️ ${err instanceof Error ? err.message : "Request failed. Is the backend running?"}`,
        },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    }
  }

  return (
    <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full p-4 gap-4">
      <h1 className="text-lg font-semibold text-white shrink-0">AI Assistant</h1>

      {/* Message thread */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div className={`max-w-[80%] space-y-1 ${m.role === "user" ? "flex flex-col items-end" : ""}`}>
              <div
                className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
                  m.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-800 text-gray-200"
                }`}
              >
                {m.text}
              </div>

              {/* Tool call badges */}
              {m.toolCalls && m.toolCalls.length > 0 && (
                <div className="flex flex-wrap gap-1 px-1">
                  {m.toolCalls.map((tc, j) => (
                    <span
                      key={j}
                      className="text-[10px] bg-gray-700 text-gray-400 rounded px-1.5 py-0.5"
                    >
                      ⚙ {tc}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 rounded-2xl px-4 py-3 flex gap-1 items-center">
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Example prompts */}
      <div className="shrink-0 flex flex-wrap gap-2">
        {EXAMPLE_QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => setInput(q)}
            className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-full px-3 py-1 transition-colors"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input row */}
      <div className="shrink-0 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          disabled={loading}
          placeholder="Ask about HSL routes, disruptions, or simulations…"
          className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm
                     text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500
                     disabled:opacity-50"
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500
                     text-white rounded-xl px-4 py-2.5 text-sm font-medium transition-colors min-w-[64px]"
        >
          {loading ? "…" : "Send"}
        </button>
      </div>
    </div>
  );
}
