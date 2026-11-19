import { ArrowUp, Sparkles } from "lucide-react";
import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import ToneSelector from "./ToneSelector";

const suggestions = ["Explain a complex topic simply", "Help me brainstorm project ideas", "Write and improve my resume"];

export default function ChatWindow({ messages, prompt, setPrompt, onSend, onRegenerate, tone, setTone, busy, activeId, error }) {
  const bottomRef = useRef(null);
  const inputRef = useRef(null);
  useEffect(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), [messages]);
  function submit(e) {
    e.preventDefault();
    if (!busy && prompt.trim()) onSend();
  }
  return <main className="main-panel">
    <header className="topbar">
      <div className="topbar-title"><span className="status-dot"/> <b>AI Assistant</b><span className="topbar-divider">/</span><span>{activeId ? "Conversation" : "New chat"}</span></div>
      <ToneSelector tone={tone} onChange={setTone} disabled={busy}/>
    </header>
    <section className="conversation">
      {messages.length === 0 ? <div className="welcome">
        <div className="welcome-icon"><Sparkles size={25}/></div>
        <div className="eyebrow">YOUR THOUGHT PARTNER</div>
        <h1>What can I help you<br/><em>figure out today?</em></h1>
        <p>Ask anything. Explore ideas, solve problems, or turn a blank page into a plan.</p>
        <div className="suggestions">{suggestions.map(s => <button key={s} onClick={() => {setPrompt(s); inputRef.current?.focus();}}>{s}<span>↗</span></button>)}</div>
      </div> : <div className="messages">
        {messages.map((m, i) => <MessageBubble key={`${i}-${m.timestamp || "stream"}`} message={m}
          isLastAssistant={m.role === "assistant" && i === messages.length - 1}
          onRegenerate={onRegenerate} busy={busy}/>)}
        <div ref={bottomRef}/>
      </div>}
    </section>
    {error && <div className="error-banner">{error}</div>}
    <div className="composer-wrap">
      <form className="composer" onSubmit={submit}>
        <textarea ref={inputRef} value={prompt} onChange={e => setPrompt(e.target.value)}
          onKeyDown={e => {if(e.key === "Enter" && !e.shiftKey){e.preventDefault(); submit(e);}}}
          placeholder="Message Nova… (Enter to send, Shift + Enter for new line)" rows={1} disabled={busy}/>
        <button className="send-button" type="submit" disabled={busy || !prompt.trim()} aria-label="Send message">
          {busy ? <span className="mini-loader"/> : <ArrowUp size={19}/>}
        </button>
      </form>
      <div className="composer-foot"><span>Nova can make mistakes. Verify important information.</span><span>Powered by AI</span></div>
    </div>
  </main>;
}
