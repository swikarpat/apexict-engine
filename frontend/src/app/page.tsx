"use client";

import React, { useState } from 'react';
import { Search, PlayCircle, Crosshair, Loader2, BookOpen, ExternalLink } from 'lucide-react';
import axios from 'axios';

export default function ICTCommandCenter() {
  const [query, setQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<any>(null);
  
  const [activeNote, setActiveNote] = useState<any>(null);

  const handleSearch = async () => {
    if (!query) return;
    setIsSearching(true);
    try {
      const response = await axios.post('http://localhost:8000/api/search', { text: query });
      setResults(response.data);
      if (response.data.results && response.data.results.length > 0) {
        setActiveNote(response.data.results[0]);
      }
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setIsSearching(false);
    }
  };

  // THE FIX: Open YouTube in a new tab at the exact timestamp!
  const playVideoOnYouTube = (videoId: string, startTime: number) => {
    const url = `https://www.youtube.com/watch?v=${videoId}&t=${Math.floor(startTime)}s`;
    window.open(url, '_blank');
  };

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-300 font-sans">
      
      {/* LEFT PANEL: SEARCH & RESULTS */}
      <div className="w-1/2 flex flex-col border-r border-zinc-800 bg-zinc-900/50">
        
        {/* Header & Search Bar */}
        <div className="p-6 border-b border-zinc-800 bg-zinc-950">
          <h1 className="text-2xl font-bold text-emerald-500 flex items-center gap-2 mb-4">
            <Crosshair className="w-6 h-6" /> ApexICT Engine
          </h1>
          
          <div className="flex items-center gap-2 bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 focus-within:border-emerald-500 transition">
            <Search className="w-5 h-5 text-zinc-500" />
            <input 
              type="text" 
              placeholder="Ask an ICT question (e.g., 'when market takes equal highs then reversal?')" 
              className="bg-transparent border-none outline-none w-full text-zinc-200 placeholder-zinc-600"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button 
              onClick={handleSearch}
              disabled={isSearching}
              className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-1.5 rounded-md text-sm font-medium flex items-center gap-2 transition disabled:opacity-50"
            >
              {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : "Search"}
            </button>
          </div>
        </div>

        {/* Results Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          
          {results?.error && (
            <div className="mb-6 bg-red-950/30 border border-red-900/50 p-4 rounded-lg">
              <p className="text-sm text-red-400">{results.error}</p>
            </div>
          )}

          {results && !results.error && (
            <div className="mb-6 bg-emerald-950/30 border border-emerald-900/50 p-4 rounded-lg">
              <p className="text-xs text-emerald-500 font-mono mb-1">Ollama Intent Normalizer:</p>
              <p className="text-sm text-emerald-300">"{results.optimized_query}"</p>
            </div>
          )}

          {results?.results.map((res: any, idx: number) => (
            <div 
              key={idx} 
              onClick={() => setActiveNote(res)}
              className={`cursor-pointer border p-4 rounded-lg transition ${activeNote?.url_link === res.url_link ? 'bg-zinc-800 border-emerald-500' : 'bg-zinc-900 border-zinc-800 hover:border-zinc-600'}`}
            >
              <h3 className="text-md font-bold text-zinc-100 mb-2">{res.title}</h3>
              <p className="text-sm text-zinc-400 mb-4 leading-relaxed border-l-2 border-zinc-700 pl-3">
                "...{res.text}..."
              </p>
              <button 
                onClick={(e) => { e.stopPropagation(); playVideoOnYouTube(res.video_id, res.start_time); }}
                className="flex items-center gap-2 text-sm bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-400 border border-emerald-800 px-4 py-2 rounded-md transition w-full justify-center"
              >
                <ExternalLink className="w-4 h-4" />
                Watch on YouTube ({Math.floor(res.start_time / 60)}m {Math.floor(res.start_time % 60)}s)
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* RIGHT PANEL: STUDY NOTES */}
      <div className="w-1/2 flex flex-col bg-zinc-950 p-8">
        {activeNote ? (
          <div className="animate-in fade-in slide-in-from-right-4">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <BookOpen className="w-6 h-6 text-emerald-500" /> Active Study Session
            </h2>
            
            <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-xl mb-6">
              <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Video Title</p>
              <p className="text-lg text-zinc-200 font-semibold">{activeNote.title}</p>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-xl mb-6">
              <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Exact Transcript</p>
              <p className="text-md text-zinc-300 leading-relaxed italic">
                "{activeNote.text}"
              </p>
            </div>

            <button 
              onClick={() => playVideoOnYouTube(activeNote.video_id, activeNote.start_time)}
              className="flex items-center justify-center gap-2 text-lg bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-4 rounded-xl transition w-full shadow-lg shadow-emerald-900/20"
            >
              <PlayCircle className="w-6 h-6" />
              Jump to {Math.floor(activeNote.start_time / 60)}:{Math.floor(activeNote.start_time % 60).toString().padStart(2, '0')} on YouTube
            </button>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-zinc-600">
            <BookOpen className="w-16 h-16 mb-4 opacity-20" />
            <p>Select a search result to view study notes.</p>
          </div>
        )}
      </div>

    </div>
  );
}