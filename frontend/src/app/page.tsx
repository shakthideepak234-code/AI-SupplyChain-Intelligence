
"use client";

import { useState } from "react";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function askAssistant() {
    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question }),
        }
      );

      if (!response.ok) throw new Error("API request failed");

      const data = await response.json();
      setAnswer(data.answer);
    } catch {
      setAnswer("Unable to connect to the backend. Please check the API server.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white p-6 md:p-10">
      <div className="max-w-7xl mx-auto">
        <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-10">
          <div>
            <p className="text-cyan-400 text-sm font-semibold tracking-widest">
              SUPPLY CHAIN ANALYTICS
            </p>
            <h1 className="text-3xl md:text-4xl font-bold mt-2">
              AI Supply Chain Intelligence
            </h1>
            <p className="text-slate-400 mt-2">
              Demand insights powered by machine learning and AI
            </p>
          </div>
          <span className="bg-emerald-500/10 text-emerald-400 px-4 py-2 rounded-full text-sm">
            ● System Dashboard
          </span>
        </header>

        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <p className="text-slate-400 text-sm">Recorded Demand</p>
            <h2 className="text-3xl font-bold mt-3">3,155,647</h2>
            <p className="text-xs text-slate-500 mt-2">
              Loaded database records
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <p className="text-slate-400 text-sm">Products</p>
            <h2 className="text-3xl font-bold mt-3">3,049</h2>
            <p className="text-xs text-slate-500 mt-2">
              M5 product master data
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <p className="text-slate-400 text-sm">Stores Covered</p>
            <h2 className="text-3xl font-bold mt-3">1</h2>
            <p className="text-xs text-slate-500 mt-2">
              Current demand data: CA_1
            </p>
          </div>
        </section>

        <section className="bg-slate-900 border border-slate-800 rounded-xl p-6 mb-8">
          <h2 className="text-xl font-semibold mb-2">AI Supply Chain Assistant</h2>
          <p className="text-slate-400 text-sm mb-5">
            Ask questions about recorded supply chain demand.
          </p>

          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Example: What is the total recorded demand?"
            className="w-full min-h-28 bg-slate-950 border border-slate-700 rounded-lg p-4 outline-none focus:border-cyan-500"
          />

          <button
            onClick={askAssistant}
            disabled={loading || !question.trim()}
            className="mt-4 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 px-6 py-3 rounded-lg font-semibold"
          >
            {loading ? "Thinking..." : "Ask Assistant"}
          </button>

          {answer && (
            <div className="mt-5 bg-slate-950 border border-slate-700 rounded-lg p-5">
              <h3 className="text-cyan-400 font-semibold mb-2">AI Response</h3>
              <p className="text-slate-200 whitespace-pre-wrap">{answer}</p>
            </div>
          )}
        </section>

        <footer className="text-center text-slate-500 text-sm py-6">
          AI-Powered Supply Chain Intelligence | M5 Dataset
        </footer>
      </div>
    </main>
  );
}
