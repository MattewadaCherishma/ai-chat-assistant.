import { MessageSquare, Plus, Sparkles } from "lucide-react";

export default function Sidebar({ chats, activeId, onNew, onSelect, loading }) {
  return <aside className="sidebar">
    <div className="brand"><div className="brand-mark"><Sparkles size={19}/></div><div><b>nova</b><span>AI workspace</span></div></div>
    <button className="new-chat" onClick={onNew}><Plus size={17}/> New conversation</button>
    <div className="side-label">YOUR HISTORY</div>
    <div className="chat-list">
      {loading && <div className="side-empty">Loading conversations…</div>}
      {!loading && chats.length === 0 && <div className="side-empty">Your conversations will appear here.</div>}
      {chats.map(chat => <button key={chat.conversation_id}
        className={`history-item ${activeId === chat.conversation_id ? "active" : ""}`}
        onClick={() => onSelect(chat.conversation_id)}>
        <MessageSquare size={15}/><span>{chat.title || "New conversation"}</span>
      </button>)}
    </div>
    <div className="sidebar-bottom"><div className="online-dot"/> AI assistant <span>·</span> Ready</div>
  </aside>;
}
