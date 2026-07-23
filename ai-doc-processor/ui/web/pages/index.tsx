import { useState } from "react";
import DocumentUploader from "../components/DocumentUploader";

export default function Home() {
  const [result, setResult] = useState<string>("");

  return (
    <main style={{ maxWidth: 760, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>📄 AI Document Processor</h1>
      <p>Upload a PDF or text file to get an AI-powered summary.</p>
      <DocumentUploader onStream={(token) => setResult((prev) => prev + token)} />
      {result && (
        <section>
          <h2>Summary</h2>
          <pre style={{ background: "#f4f4f4", padding: "1rem", borderRadius: 4 }}>{result}</pre>
        </section>
      )}
    </main>
  );
}
