To satisfy the constraints of a **very short learning path** and **less-code frontend**, we will use **Gradio** as the frontend. 

*Why Gradio over Streamlit for this specific stack?* While Streamlit is script-centric, **Gradio is function-centric**. Because we are using a **FastAPI backend**, Gradio acts as the perfect "thin UI layer." You don't write UI logic; you just map UI inputs to FastAPI function calls. Furthermore, Gradio has built-in, zero-code Chat interfaces that make integrating the LLM features incredibly fast.

Here is the redesigned, hybrid architecture plan using **Gradio + FastAPI**.

---

### **Architecture Overview**
*   **Frontend (Less-Code):** Gradio (Handles UI components, chat interfaces, and user interactions).
*   **Backend (Low-Code):** FastAPI (Handles business logic, database, auth, external API calls, and LLM orchestration).
*   **AI/LLM Layer:** RAG (Retrieval-Augmented Generation) + Prompt Engineering.

---

### **Phase 1: The FastAPI Backend Foundation**
*Goal: Build the API that will do all the heavy lifting, keeping the Gradio frontend lightweight.*

*   **Step 1: Setup & Auto-Docs.** 
    *   Install: `pip install fastapi uvicorn pydantic`.
    *   Create `main.py`. FastAPI automatically creates a testing UI at `/docs`.
*   **Step 2: Define Data Models (Pydantic).** 
    ```python
    from pydantic import BaseModel
    class Product(BaseModel):
        id: int
        name: str
        price: float
    class SearchQuery(BaseModel):
        query: str
    ```
*   **Step 3: Create Core Endpoints.**
    ```python
    from fastapi import FastAPI
    app = FastAPI()

    @app.post("/ai/search")
    async def universal_search(query: SearchQuery):
        # FastAPI handles the Vector DB lookup and LLM formatting here
        return {"results": ["Product A", "Product B"], "summary": "AI generated summary"}
    ```
*   **Step 4: Run Locally.** Execute `uvicorn main:app --reload`. 

---

### **Phase 2: "Easy Learning" LLM & Gradio's Secret Weapon**
*Goal: "Train" the LLM via RAG, and use Gradio's native components to build the AI UI in <5 lines of code.*

*   **Step 1: Backend RAG (The "Training").**
    *   In FastAPI, use **LangChain** or **LlamaIndex** to connect to **ChromaDB** (Vector DB). 
    *   When `/ai/search` is called, FastAPI retrieves relevant product context and injects it into a **Few-Shot Prompt** (as detailed in the previous plan) before calling the LLM.
*   **Step 2: Gradio's `ChatInterface` (The Less-Code Magic).**
    *   Instead of building a custom chat UI, Gradio provides `gr.ChatInterface`. You just write the Python function that calls your FastAPI backend, and Gradio builds a beautiful, fully functional chat UI automatically.
    ```python
    import gradio as gr
    import requests

    def chat_with_shop(message, history):
        # Call FastAPI backend
        res = requests.post("http://localhost:8000/ai/search", json={"query": message})
        return res.json()["summary"] # Return the LLM response

    # This single line creates a full ChatGPT-like UI for your shop!
    demo = gr.ChatInterface(fn=chat_with_shop, title="🛒 Shop AI Assistant")
    demo.launch()
    ```

---

### **Phase 3: External Integrations & Payments (Backend)**
*Goal: Handle Allegro/Amazon and Stripe securely in FastAPI.*

*   **Step 1: Marketplace Sync.**
    *   Create a FastAPI endpoint `/sync/allegro`. Use Python's `httpx` to call Allegro's API. Store credentials in a `.env` file via `python-dotenv`.
*   **Step 2: Payment Processing.**
    *   Create a FastAPI endpoint `/checkout`. Use the `stripe` Python SDK to generate a secure Checkout Session URL. Return the URL to the frontend.
*   **Step 3: Background Tasks.**
    *   Use FastAPI's `BackgroundTasks` to update inventory on Amazon/Allegro *after* the payment is confirmed, ensuring the user doesn't wait for the external API to respond.

---

### **Phase 4: Building the Full Gradio Frontend**
*Goal: Connect the Gradio UI to the FastAPI backend using `gr.Blocks` for a complex, dashboard-like layout.*

*   **Step 1: Layout with `gr.Blocks`.**
    *   Use `gr.Blocks(theme=gr.themes.Soft())` to create a customized, multi-tab application.
*   **Step 2: State Management.**
    *   Use `gr.State()` to hold the user's Cart in the frontend, or simply pass the cart to FastAPI to manage.
*   **Step 3: Wiring Inputs to FastAPI.**
    *   Use `.click()` or `.submit()` event listeners to trigger API calls.
    ```python
    import gradio as gr
    import requests

    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🛍️ E-Commerce Command Center")
        
        with gr.Tab("Catalog & Search"):
            search_input = gr.Textbox(label="Universal Search")
            search_btn = gr.Button("Search")
            results_output = gr.Dataframe(label="Products")
            
            # Wire button to FastAPI endpoint
            def fetch_products(query):
                res = requests.get(f"http://localhost:8000/products?search={query}")
                return res.json()
                
            search_btn.click(fetch_products, inputs=search_input, outputs=results_output)

        with gr.Tab("Checkout"):
            cart_state = gr.State([])
            # Add UI for cart and a button that calls FastAPI /checkout to get Stripe URL
            # Use gr.Markdown to display the clickable Stripe payment link
            
    demo.launch()
    ```

---

### **Phase 5: Run Anywhere & Low-Cost Deployment**
*Goal: Deploy the frontend and backend with zero infrastructure management.*

*   **Step 1: Backend Deployment (FastAPI).**
    *   Push backend code to GitHub.
    *   Deploy to **Render.com** or **Railway.app** (Free/Cheap tiers). They auto-detect Python/FastAPI and give you a public URL (e.g., `api.myshop.com`).
*   **Step 2: Frontend Deployment (Gradio).**
    *   Push frontend code to GitHub.
    *   Deploy to **Hugging Face Spaces** (100% Free). 
    *   Select "Gradio" as the SDK. In the Space's "Settings" -> "Variables", add `API_URL="https://api.myshop.com"` so Gradio knows where to find your FastAPI backend.
*   **Step 3: Local Containerization (Optional).**
    *   If you need to run it on a private server, use Docker Compose to spin up the FastAPI container and the Gradio container side-by-side.

---

### **Supporting Tools for the Gradio + FastAPI Stack**

1.  **Gradio Specific Tools:**
    *   **`gr.themes`**: Gradio's built-in theming engine. Use `gr.themes.Soft()`, `gr.themes.Glass()`, or `gr.themes.Monochrome()` for instant, beautiful UI configurability without writing CSS.
    *   **Gradio Component Gallery**: The official docs have an interactive gallery where you can copy-paste the code for any UI component (Dropdowns, Sliders, Dataframes).
2.  **API & Backend Testing:**
    *   **Swagger UI (`/docs`)**: Built into FastAPI. Test your backend endpoints directly in the browser before connecting Gradio.
    *   **HTTPX**: Use this async HTTP client inside Gradio to ensure your UI doesn't freeze when calling the FastAPI backend.
3.  **LLM & RAG Tools:**
    *   **Ollama**: Run local LLMs (like Llama 3 or Mistral) for free during development. Point your FastAPI backend to `http://localhost:11434` instead of OpenAI.
    *   **ChromaDB**: The easiest local vector database. Runs in-memory or saves to a local folder. Zero setup required.
4.  **Environment & Config:**
    *   **`python-dotenv`**: Manage your `.env` files for FastAPI.
    *   **Hugging Face Secrets**: When deploying Gradio to HF Spaces, use the "Variables" and "Secrets" tabs in the dashboard to inject API keys securely.

### **Summary of the Gradio Advantage:**
By using **Gradio + FastAPI**, you completely separate the UI from the logic. FastAPI handles the complex e-commerce rules, database, and LLM orchestration. Gradio simply acts as a beautiful, less-code presentation layer. When you need to add a new feature, you just write a new FastAPI endpoint and add a single `gr.Button().click()` in Gradio to connect it.
