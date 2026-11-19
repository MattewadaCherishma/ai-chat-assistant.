import { useCallback, useEffect, useState } from "react";
import { api } from "./services/api";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";

export default function App() {
  const [chats, setChats] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState("");
  const [tone, setTone] = useState("professional");
  const [busy, setBusy] = useState(false);
  const [loadingChats, setLoadingChats] = useState(true);
  const [error, setError] = useState("");

  const refreshChats = useCallback(async () => {
    try { setChats(await api.listChats()); }
    catch (e) { setError(`Could not load conversation history: ${e.message}`); }
    finally { setLoadingChats(false); }
  }, []);

  useEffect(() => { refreshChats(); }, [refreshChats]);

  async function newChat() {
    if (busy) return;
    setError("");
    try {
      const chat = await api.createChat();
      setActiveId(chat.conversation_id);
      setMessages([]);
      setPrompt("");
      await refreshChats();
    } catch (e) { setError(`Could not create a conversation: ${e.message}`); }
  }

  async function selectChat(id) {
    if (busy) return;
    setError("");
    try {
      const chat = await api.getChat(id);
      setActiveId(id);
      setMessages(chat.messages || []);
      setPrompt("");
    } catch (e) { setError(`Could not open conversation: ${e.message}`); }
  }

  async function ensureChat() {
    if (activeId) return activeId;
    const chat = await api.createChat();
    setActiveId(chat.conversation_id);
    return chat.conversation_id;
  }

  async function sendMessage() {
    const text = prompt.trim();
    if (!text || busy) return;
    setBusy(true); setError(""); setPrompt("");
    const userMessage = { role: "user", content: text, timestamp: new Date().toISOString(), tone };
    setMessages(prev => [...prev, userMessage, { role: "assistant", content: "", timestamp: new Date().toISOString() }]);
    try {
      const id = await ensureChat();
      await api.streamMessage(id, text, tone, token => {
        setMessages(prev => {
          const copy = [...prev];
          const last = copy[copy.length - 1];
          if (last?.role === "assistant") copy[copy.length - 1] = { ...last, content: last.content + token };
          return copy;
        });
      });
      await refreshChats();
      const latest = await api.getChat(id);
      setMessages(latest.messages || []);
    } catch (e) {
      setError(e.message);
      setMessages(prev => prev.filter((m, i) => !(i === prev.length - 1 && m.role === "assistant" && !m.content)));
    } finally { setBusy(false); }
  }

  async function regenerate() {
    if (!activeId || busy) return;
    setBusy(true); setError("");
    setMessages(prev => [...prev.slice(0, -1), { role: "assistant", content: "", timestamp: new Date().toISOString() }]);
    try {
      await api.streamMessage(activeId, "", tone, token => {
        setMessages(prev => {
          const copy = [...prev];
          const last = copy[copy.length - 1];
          if (last?.role === "assistant") copy[copy.length - 1] = { ...last, content: last.content + token };
          return copy;
        });
      }, true);
      const latest = await api.getChat(activeId);
      setMessages(latest.messages || []);
      await refreshChats();
    } catch (e) {
      setError(e.message);
      try { const latest = await api.getChat(activeId); setMessages(latest.messages || []); } catch {}
    } finally { setBusy(false); }
  }

  return <div className="app-shell">
    <Sidebar chats={chats} activeId={activeId} onNew={newChat} onSelect={selectChat} loading={loadingChats}/>
    <ChatWindow messages={messages} prompt={prompt} setPrompt={setPrompt} onSend={sendMessage}
      onRegenerate={regenerate} tone={tone} setTone={setTone} busy={busy} activeId={activeId} error={error}/>
  </div>;
}
