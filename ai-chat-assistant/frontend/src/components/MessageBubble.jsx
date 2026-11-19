import { Bot, Check, Copy, RefreshCw, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useState } from "react";

export default function MessageBubble({ message, onRegenerate, isLastAssistant, busy }) {
  const [copied, setCopied] = useState(false);
  const assistant = message.role === "assistant";
  async function copyText() {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch { setCopied(false); }
  }
  return <div className={`message-row ${assistant ? "assistant-row" : "user-row"}`}>
    <div className={`avatar ${assistant ? "bot-avatar" : "user-avatar"}`}>{assistant ? <Bot size={17}/> : <User size={17}/>}</div>
    <div className="message-content">
      <div className="message-meta"><b>{assistant ? "Nova" : "You"}</b><span>{message.timestamp ? new Date(message.timestamp).toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"}) : "Now"}</span></div>
      <div className={`bubble ${assistant ? "ai-bubble" : "human-bubble"}`}>
        {assistant ? <div className="markdown"><ReactMarkdown>{message.content || ""}</ReactMarkdown></div> : <div className="plain-text">{message.content}</div>}
        {assistant && !message.content && <span className="typing-dots"><i/><i/><i/></span>}
      </div>
      {assistant && message.content && <div className="message-actions">
        <button onClick={copyText} title="Copy response">{copied ? <Check size={14}/> : <Copy size={14}/>} {copied ? "Copied" : "Copy"}</button>
        {isLastAssistant && <button onClick={onRegenerate} disabled={busy} title="Regenerate response"><RefreshCw size={14}/> Regenerate</button>}
      </div>}
    </div>
  </div>;
}
