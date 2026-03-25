"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Send, Bot, User as UserIcon } from "lucide-react";

interface Message {
  role: "user" | "model";
  content: string;
}

export default function ChatPage() {
  const { user } = useAuth();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
      { role: "model", content: "Hi! I'm your AI property assistant. Tell me what kind of property you're looking for, or ask me about your wishlist!" }
  ]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading || !user) return;

    const userMsg = input.trim();
    setInput("");
    const newMessages = [...messages, { role: "user" as const, content: userMsg }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const res = await api.post("/chat", {
        message: userMsg,
        conversation_history: messages.slice(1).map(m => ({ role: m.role, content: m.content })),
      });
      setMessages([...newMessages, { role: "model", content: res.data.data.reply }]);
    } catch (e) {
      setMessages([...newMessages, { role: "model", content: "Sorry, I'm having trouble connecting right now." }]);
    }
    setLoading(false);
  };

  if (!user) return <div className="text-center py-20">Please log in to chat with the assistant.</div>;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 h-[85vh] flex flex-col">
      <h1 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Bot className="w-8 h-8 text-blue-600" /> Real Estates AI
      </h1>
      
      <div className="flex-1 bg-white border border-gray-200 rounded-t-xl overflow-y-auto p-4 flex flex-col gap-4 shadow-sm">
         {messages.map((msg, idx) => (
             <div key={idx} className={`flex gap-3 max-w-[85%] ${msg.role === 'user' ? 'self-end flex-row-reverse' : 'self-start'}`}>
                 <div className={`w-8 h-8 shrink-0 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-gray-100' : 'bg-blue-100 text-blue-600'}`}>
                     {msg.role === 'user' ? <UserIcon size={16}/> : <Bot size={16}/>}
                 </div>
                 <div className={`p-3 rounded-2xl ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-gray-100 text-gray-800 rounded-tl-none whitespace-pre-wrap'}`}>
                     {msg.content}
                 </div>
             </div>
         ))}
         {loading && (
             <div className="self-start flex gap-3 max-w-[85%]">
                 <div className="w-8 h-8 shrink-0 rounded-full bg-blue-100 flex items-center justify-center text-blue-600"><Bot size={16}/></div>
                 <div className="p-3 rounded-2xl bg-gray-100 text-gray-500 rounded-tl-none animate-pulse">Thinking...</div>
             </div>
         )}
      </div>

      <form onSubmit={sendMessage} className="bg-white border text-black border-t-0 border-gray-200 rounded-b-xl p-3 flex gap-2">
         <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder="Ask about properties in Mumbai under 50k..."
            className="flex-1 border-0 focus:ring-0 px-4 py-2 bg-gray-50 rounded-lg text-black placeholder-gray-400"
         />
         <button 
            type="submit" 
            disabled={loading || !input.trim()}
            className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
         >
             <Send size={20} />
         </button>
      </form>
    </div>
  );
}
