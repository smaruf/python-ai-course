import { useState, ChangeEvent, FormEvent } from "react";

interface Props {
  onStream: (token: string) => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function DocumentUploader({ onStream }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setStatus("Uploading…");

    const form = new FormData();
    form.append("file", file);
    form.append("prompt", prompt);

    const response = await fetch(`${API_URL}/api/documents/process-stream`, {
      method: "POST",
      body: form,
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) return;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const lines = decoder.decode(value).split("\n");
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const payload = JSON.parse(line.slice(6));
          if (payload.token) onStream(payload.token);
          if (payload.status) setStatus(payload.status);
        }
      }
    }

    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="file"
        accept=".pdf,.txt"
        onChange={(e: ChangeEvent<HTMLInputElement>) =>
          setFile(e.target.files?.[0] ?? null)
        }
      />
      <input
        type="text"
        placeholder="Custom prompt (optional)"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        style={{ display: "block", marginTop: "0.5rem", width: "100%" }}
      />
      <button type="submit" disabled={loading || !file} style={{ marginTop: "0.5rem" }}>
        {loading ? "Processing…" : "Process Document ▶"}
      </button>
      {status && <p>{status}</p>}
    </form>
  );
}
