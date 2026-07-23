import streamlit as st
import httpx
import json

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="AI Document Processor", layout="wide")
st.title("📄 AI Document Processor")
st.caption("Upload a document and get a streaming AI summary instantly.")

uploaded = st.file_uploader("Choose a PDF or text file", type=["pdf", "txt"])
prompt = st.text_input("Custom prompt (optional)", placeholder="Summarize this document concisely:")

if uploaded and st.button("Process Document ▶"):
    output_area = st.empty()
    full_text = ""

    with httpx.stream(
        "POST",
        f"{API_BASE}/api/documents/process-stream",
        files={"file": (uploaded.name, uploaded.read(), uploaded.type)},
        data={"prompt": prompt},
        timeout=120,
    ) as response:
        for line in response.iter_lines():
            if line.startswith("data: "):
                payload = json.loads(line[6:])
                if "token" in payload:
                    full_text += payload["token"]
                    output_area.markdown(full_text)
                elif payload.get("status") == "complete":
                    st.success("✅ Processing complete")
