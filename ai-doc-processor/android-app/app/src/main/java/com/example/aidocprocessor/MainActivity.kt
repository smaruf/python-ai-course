package com.example.aidocprocessor

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.widget.*
import java.util.concurrent.Executors

class MainActivity : Activity() {
    private val worker = Executors.newSingleThreadExecutor()
    private lateinit var store: DocumentStore
    private lateinit var list: ListView
    private lateinit var detail: TextView
    private lateinit var status: TextView
    private lateinit var search: EditText
    private lateinit var importButton: Button
    private lateinit var deleteButton: Button
    private var entries = emptyList<Pair<Long, String>>()
    private var selected = -1L
    @Volatile private var alive = true
    private var busy = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        store = DocumentStore(applicationContext)
        selected = savedInstanceState?.getLong("selected", -1L) ?: -1L
        val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(16, 16, 16, 16) }
        root.addView(TextView(this).apply { text = "Local documents • Extractive summaries (not AI/LLM)\nTXT/PDF • 10 MiB • 200 pages • No OCR\nCloud picker files are downloaded by their provider; processing stays on this device." })
        importButton = Button(this).apply { id = R.id.import_button; text = "Import TXT or PDF"; setOnClickListener { chooseDocument() } }
        root.addView(importButton)
        search = EditText(this).apply { id = R.id.search_input; hint = "Search stored text or filename"; setSingleLine(true) }
        root.addView(search)
        root.addView(Button(this).apply { id = R.id.search_button; text = "Search"; setOnClickListener { refresh(search.text.toString()) } })
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
                        selected = -1L; detail.text = "Select a stored document."; deleteButton.isEnabled = false
                        renderRows(rows); status.text = "Document deleted."
                    }
                }
            }
        }
        root.addView(deleteButton)
        setContentView(root)
        refresh("")
        if (selected != -1L) showDocument(selected)
    }

    private var searchQuery = ""
    private fun post(action: () -> Unit) { runOnUiThread { if (alive && !isFinishing) action() } }
    private fun execute(action: () -> Unit) {
        if (busy) return
        busy = true
        importButton.isEnabled = false
        deleteButton.isEnabled = false
        worker.execute {
            try { action() }
            catch (error: Exception) { post { status.text = "Import/action failed: ${error.message ?: error.javaClass.simpleName}" } }
            finally { post { busy = false; importButton.isEnabled = true; deleteButton.isEnabled = selected != -1L } }
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
        detail.text = "${document.name}\n\nExtractive summary\n${document.summary}\n\nExtracted text\n${document.text}"
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
    @Deprecated("Platform activity result API")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != 10 || resultCode != RESULT_OK) return
        val uri = data?.data ?: return
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
        worker.execute { store.close() }
        worker.shutdown()
        super.onDestroy()
    }
}
