package com.example.aidocprocessor

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import com.tom_roush.pdfbox.android.PDFBoxResourceLoader
import com.tom_roush.pdfbox.io.MemoryUsageSetting
import com.tom_roush.pdfbox.pdmodel.PDDocument
import com.tom_roush.pdfbox.text.PDFTextStripper
import java.io.Writer

class DocumentExtractor(private val context: Context) {
    fun extract(uri: Uri): Pair<String, ProcessedDocument> {
        require(uri.scheme == "content") { "Choose a document through the file picker." }
        val name = context.contentResolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)
            ?.use { cursor -> if (cursor.moveToFirst()) cursor.getString(0) else null } ?: "Document"
        val bytes = context.contentResolver.openInputStream(uri)?.use(DocumentEngine::readBounded)
            ?: error("Unable to open document.")
        val isPdf = bytes.size >= 5 && bytes.copyOfRange(0, 5).contentEquals("%PDF-".toByteArray())
        val mime = context.contentResolver.getType(uri)
        val text = if (isPdf || mime == "application/pdf" || name.endsWith(".pdf", true)) pdfText(bytes)
        else {
            require(mime == "text/plain" || name.endsWith(".txt", true)) { "Only UTF-8 TXT and PDF files are supported." }
            DocumentEngine.decodeUtf8(bytes)
        }
        return name.take(200) to DocumentEngine.process(text)
    }

    fun pdfText(bytes: ByteArray): String {
        require(bytes.size <= DocumentEngine.MAX_BYTES) { "File exceeds 10 MiB limit." }
        PDFBoxResourceLoader.init(context.applicationContext)
        return bytes.inputStream().use { input ->
            // Scratch storage is capped; PDF object/decoder heap is not a total memory sandbox.
            PDDocument.load(input, "", MemoryUsageSetting.setupMainMemoryOnly(64L * 1024 * 1024)).use { document ->
                require(!document.isEncrypted) { "Encrypted PDFs are not supported." }
                require(document.numberOfPages <= DocumentEngine.MAX_PAGES) { "PDF exceeds 200 page limit." }
                require(document.currentAccessPermission.canExtractContent()) { "PDF does not permit text extraction." }
                val output = StringBuilder()
                val writer = object : Writer() {
                    override fun write(buffer: CharArray, offset: Int, length: Int) {
                        require(output.length + length <= DocumentEngine.MAX_CHARS) { "PDF text exceeds character limit." }
                        output.append(buffer, offset, length)
                    }
                    override fun flush() = Unit
                    override fun close() = Unit
                }
                PDFTextStripper().apply { sortByPosition = true }.writeText(document, writer)
                output.toString()
            }
        }
    }
}
