package com.example.aidocprocessor

import android.app.Activity
import android.app.AlertDialog
import android.content.Intent
import android.os.Bundle
import android.os.Build
import android.view.WindowInsets
import android.widget.*
import java.util.concurrent.Executors

class MainActivity : Activity() {
    private val worker = Executors.newSingleThreadExecutor()
    private lateinit var store: DocumentStore
    private lateinit var list: ListView
    private lateinit var detail: TextView
    private lateinit var status: TextView
    private lateinit var search: EditText
    private lateinit var searchButton: Button
    private lateinit var importButton: Button
    private lateinit var deleteButton: Button
    private lateinit var assistant: LocalAssistant
    private var selectedDocument: StoredDocument? = null
    private var assistantOutput: TextView? = null
    private var assistantControls = emptyList<Button>()
    private var entries = emptyList<Pair<Long, String>>()
    private var selected = -1L
    @Volatile private var alive = true
    private var busy = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        store = DocumentStore(applicationContext)
        assistant = LocalAssistant(applicationContext)
        selected = savedInstanceState?.getLong("selected", -1L) ?: -1L
        val padding = (16 * resources.displayMetrics.density).toInt()
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(padding, padding, padding, padding)
            setOnApplyWindowInsetsListener { view, insets ->
                if (Build.VERSION.SDK_INT >= 30) {
                    val bars = insets.getInsets(WindowInsets.Type.systemBars() or WindowInsets.Type.displayCutout())
                    view.setPadding(padding + bars.left, padding + bars.top, padding + bars.right, padding + bars.bottom)
                } else {
                    @Suppress("DEPRECATION")
                    view.setPadding(padding + insets.systemWindowInsetLeft, padding + insets.systemWindowInsetTop,
                        padding + insets.systemWindowInsetRight, padding + insets.systemWindowInsetBottom)
                }
                insets
            }
        }
        root.addView(TextView(this).apply { text = "Local documents • Extractive summaries + optional local LLM\nTXT/PDF • 10 MiB • 200 pages • No OCR\nCloud picker files are downloaded by their provider; processing stays on this device." })
        importButton = Button(this).apply { id = R.id.import_button; text = "Import TXT or PDF"; setOnClickListener { chooseDocument() } }
        root.addView(importButton)
        search = EditText(this).apply { id = R.id.search_input; hint = "Search stored text or filename"; setSingleLine(true) }
        root.addView(search)
        searchButton = Button(this).apply { id = R.id.search_button; text = "Search"; setOnClickListener { refresh(search.text.toString()) } }
        root.addView(searchButton)
        status = TextView(this).apply { id = R.id.status; text = "Loading documents…" }
        root.addView(status)
        list = ListView(this).apply {
            id = R.id.document_list
            setOnItemClickListener { _, _, position, _ -> showDocument(entries[position].first) }
        }
        root.addView(list, LinearLayout.LayoutParams(-1, 0, 1f))
        detail = TextView(this).apply { id = R.id.document_detail; setTextIsSelectable(true); text = "Select a stored document." }
        root.addView(ScrollView(this).apply { addView(detail) }, LinearLayout.LayoutParams(-1, 0, 1f))
        deleteButton = Button(this).apply {
            id = R.id.delete_button; text = "Delete selected document"; isEnabled = false
            setOnClickListener {
                val idToDelete = selected
                execute {
                    store.delete(idToDelete)
                    val rows = store.list(searchQuery)
                    post {
                        selected = -1L; selectedDocument = null; detail.text = "Select a stored document."; deleteButton.isEnabled = false
                        renderRows(rows); status.text = "Document deleted."
                    }
                }
            }
        }
        root.addView(deleteButton)
        root.addView(Button(this).apply {
            id = R.id.assistant_button; text = "Local LLM assistant"
            setOnClickListener { showAssistant() }
        })
        setContentView(root)
        root.requestApplyInsets()
        refresh("")
    }

    private var searchQuery = ""
    private fun post(action: () -> Unit) { runOnUiThread { if (alive && !isFinishing) action() } }
    private fun execute(action: () -> Unit) {
        if (busy) return
        busy = true
        importButton.isEnabled = false
        deleteButton.isEnabled = false
        searchButton.isEnabled = false
        list.isEnabled = false
        assistantControls.forEach { it.isEnabled = false }
        worker.execute {
            try { action() }
            catch (error: Exception) { post {
                val message = "Import/action failed: ${error.message ?: error.javaClass.simpleName}"
                status.text = message; assistantOutput?.text = message
            } }
            finally { post {
                busy = false; importButton.isEnabled = true; deleteButton.isEnabled = selected != -1L
                searchButton.isEnabled = true; list.isEnabled = true
                assistantControls.forEach { it.isEnabled = true }
            } }
        }
    }

    private fun refresh(query: String) {
        searchQuery = query
        execute {
            val rows = store.list(query)
            val restored = if (selected != -1L) store.get(selected) else null
            post {
                renderRows(rows)
                status.text = "${rows.size} document(s) • Local storage"
                if (restored != null) renderDocument(restored)
            }
        }
    }
    private fun renderRows(rows: List<Pair<Long, String>>) {
        entries = rows
        list.adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, rows.map { it.second })
    }
    private fun renderDocument(document: StoredDocument) {
        selected = document.id
        selectedDocument = document
        val preview = DocumentEngine.boundedPrefix(document.text, 20_000)
        detail.text = "${document.name}\n\nExtractive summary\n${document.summary}\n\nExtracted text (preview; full text retained locally)\n$preview"
        deleteButton.isEnabled = !busy
    }
    private fun showDocument(id: Long) { execute { val document = store.get(id); post { if (document != null) renderDocument(document) } } }
    private fun chooseDocument() {
        startActivityForResult(Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "*/*"
            putExtra(Intent.EXTRA_MIME_TYPES, arrayOf("text/plain", "application/pdf"))
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }, 10)
    }
    private fun showAssistant() {
        val layout = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(24, 12, 24, 12) }
        layout.addView(TextView(this).apply {
            text = "Optional on-device LLM. Import a compatible MediaPipe .task/.bin model you obtained separately. No model download or network access. Device support and memory vary; generated answers may be wrong."
        })
        val output = TextView(this).apply {
            id = R.id.assistant_answer
            text = if (assistant.hasModel()) "Local model installed." else "No local model installed."
            setTextIsSelectable(true)
        }
        assistantOutput = output
        val modelImport = Button(this).apply {
            id = R.id.model_import_button; text = "Import local model"
            setOnClickListener {
                startActivityForResult(Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE); type = "*/*"
                    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                }, 20)
            }
        }
        val modelRemove = Button(this).apply {
            id = R.id.model_remove_button; text = "Remove local model"
            setOnClickListener {
                output.text = "Removing model…"
                execute { assistant.removeModel(); post { output.text = "Local model removed." } }
            }
        }
        val question = EditText(this).apply {
            id = R.id.assistant_question; hint = "Ask about the selected document"; setSingleLine(false)
            filters = arrayOf(android.text.InputFilter.LengthFilter(512))
        }
        val ask = Button(this).apply {
            id = R.id.assistant_answer_button; text = "Ask local LLM"
            setOnClickListener {
                val document = selectedDocument
                if (document == null) output.text = "Select a stored document first."
                else {
                    val prompt = question.text.toString()
                    output.text = "Generating locally for ${document.name}…"
                    execute {
                        val answer = assistant.answer(document.text, prompt)
                        post { output.text = "Generated answer (verify against the document):\n$answer" }
                    }
                }
            }
        }
        assistantControls = listOf(modelImport, modelRemove, ask)
        assistantControls.forEach { it.isEnabled = !busy; layout.addView(it) }
        layout.addView(question, 2)
        layout.addView(output)
        AlertDialog.Builder(this).setTitle("Local LLM assistant")
            .setView(ScrollView(this).apply { addView(layout) }).setNegativeButton("Close", null)
            .create().apply {
                setOnDismissListener { assistantOutput = null; assistantControls = emptyList() }
                show()
            }
    }
    @Deprecated("Platform activity result API")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode !in listOf(10, 20) || resultCode != RESULT_OK) return
        val uri = data?.data ?: return
        if (requestCode == 20) {
            status.text = "Importing local model…"
            assistantOutput?.text = "Importing local model…"
            execute {
                assistant.importModel(uri)
                post { status.text = "Local model installed."; assistantOutput?.text = "Local model installed. Ask about your selected document." }
            }
            return
        }
        status.text = "Importing…"
        execute {
            val (name, document) = DocumentExtractor(applicationContext).extract(uri)
            val id = store.save(name, document)
            val rows = store.list("")
            val stored = store.get(id)!!
            post { search.setText(""); searchQuery = ""; renderRows(rows); renderDocument(stored); status.text = "Imported locally." }
        }
    }
    override fun onSaveInstanceState(outState: Bundle) { outState.putLong("selected", selected); super.onSaveInstanceState(outState) }
    override fun onDestroy() {
        alive = false
        worker.execute { try { assistant.close() } finally { store.close() } }
        worker.shutdown()
        super.onDestroy()
    }
}
