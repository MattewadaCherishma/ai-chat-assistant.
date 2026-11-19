const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try { const body = await response.json(); message = body.detail || message; } catch {}
    throw new Error(message);
  }
  return response.json();
}

export const api = {
  listChats: () => request("/api/chats"),
  createChat: () => request("/api/chats", { method: "POST" }),
  getChat: (id) => request(`/api/chats/${id}`),
  streamMessage: (id, prompt, tone, onToken, regenerate = false) =>
    stream(`${API_BASE}/api/chats/${id}/${regenerate ? "regenerate" : "messages"}`,
      regenerate ? { tone } : { prompt, tone }, onToken),
};

async function stream(url, body, onToken) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "text/event-stream" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try { const data = await response.json(); message = data.detail || message; } catch {}
    throw new Error(message);
  }
  if (!response.body) throw new Error("Streaming is not supported by this browser.");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let completed = false;
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop() || "";
      for (const raw of events) {
        const eventName = raw.match(/^event:\s*(.+)$/m)?.[1]?.trim();
        const dataLine = raw.split("\n").find((line) => line.startsWith("data:"));
        if (!dataLine) continue;
        const data = JSON.parse(dataLine.slice(5).trim());
        if (eventName === "token") onToken(data.content || "");
        if (eventName === "error") throw new Error(data.message || "AI response failed.");
        if (eventName === "done") completed = true;
      }
    }
  } finally {
    reader.releaseLock();
  }
  if (!completed) throw new Error("The stream ended unexpectedly. Please try again.");
}
