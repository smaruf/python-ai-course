package com.example.aidocprocessor

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.tom_roush.pdfbox.android.PDFBoxResourceLoader
import com.tom_roush.pdfbox.pdmodel.PDDocument
import com.tom_roush.pdfbox.pdmodel.PDPage
import com.tom_roush.pdfbox.pdmodel.PDPageContentStream
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font
import com.tom_roush.pdfbox.pdmodel.encryption.AccessPermission
import com.tom_roush.pdfbox.pdmodel.encryption.StandardProtectionPolicy
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.io.ByteArrayOutputStream

@RunWith(AndroidJUnit4::class)
class DocumentIntegrationTest {
    private val context = InstrumentationRegistry.getInstrumentation().targetContext
    @Test fun extractionPersistenceRestartSearchAndCascadeDelete() {
        context.deleteDatabase("integration.db")
        val (name, processed) = DocumentExtractor(context).extract(FixtureProvider.URI)
        val id = DocumentStore(context, "integration.db").use { it.save(name, processed) }
        DocumentStore(context, "integration.db").use { db ->
            assertEquals(processed.text, db.get(id)!!.text)
            assertEquals(processed.summary, db.get(id)!!.summary)
            assertEquals(processed.chunks, db.chunks(id))
            assertEquals(listOf(id to name), db.list("SAPPHIRE"))
            assertTrue(db.list("%").isEmpty())
            db.delete(id)
            assertNull(db.get(id))
            assertTrue(db.chunks(id).isEmpty())
        }
        context.deleteDatabase("integration.db")
    }
    @Test fun pdfExtractionAndInvalidEmptyPageLimitedDocuments() {
        PDFBoxResourceLoader.init(context)
        val extractor = DocumentExtractor(context)
        assertThrows(IllegalArgumentException::class.java) {
            extractor.pdfText(ByteArray(DocumentEngine.MAX_BYTES + 1))
        }
        val bytes = PDDocument().use { doc ->
            val page = PDPage()
            doc.addPage(page)
            PDPageContentStream(doc, page).use { stream ->
                stream.beginText(); stream.setFont(PDType1Font.HELVETICA, 12f)
                stream.newLineAtOffset(30f, 700f); stream.showText("Offline PDF extraction works."); stream.endText()
            }
            ByteArrayOutputStream().also { doc.save(it) }.toByteArray()
        }
        assertTrue(extractor.pdfText(bytes).contains("Offline PDF extraction works."))
        assertThrows(Exception::class.java) { extractor.pdfText("%PDF-invalid".toByteArray()) }
        val scanned = PDDocument().use { doc -> doc.addPage(PDPage()); ByteArrayOutputStream().also { doc.save(it) }.toByteArray() }
        assertThrows(IllegalArgumentException::class.java) { DocumentEngine.process(extractor.pdfText(scanned)) }
        val tooMany = PDDocument().use { doc ->
            repeat(DocumentEngine.MAX_PAGES + 1) { doc.addPage(PDPage()) }
            ByteArrayOutputStream().also { doc.save(it) }.toByteArray()
        }
        assertThrows(IllegalArgumentException::class.java) { extractor.pdfText(tooMany) }
        val encrypted = PDDocument().use { doc ->
            doc.addPage(PDPage())
            doc.protect(StandardProtectionPolicy("owner-password", "", AccessPermission()))
            ByteArrayOutputStream().also { doc.save(it) }.toByteArray()
        }
        assertThrows(IllegalArgumentException::class.java) { extractor.pdfText(encrypted) }
    }
    @Test fun failedTransactionDoesNotLeavePartialDocument() {
        context.deleteDatabase("atomic.db")
        DocumentStore(context, "atomic.db").use { store ->
            store.writableDatabase.execSQL("CREATE TRIGGER reject_chunk BEFORE INSERT ON chunks BEGIN SELECT RAISE(ABORT, 'test failure'); END")
            assertThrows(Exception::class.java) { store.save("fail.txt", DocumentEngine.process("Content that must roll back.")) }
            assertTrue(store.list().isEmpty())
        }
        context.deleteDatabase("atomic.db")
    }
    @Test fun maximumUtf8TextSurvivesSqliteCursorRoundTrip() {
        context.deleteDatabase("boundary.db")
        val text = "\u4e00".repeat(DocumentEngine.MAX_CHARS)
        val document = DocumentEngine.process(text)
        try {
            val id = DocumentStore(context, "boundary.db").use { it.save("boundary.txt", document) }
            DocumentStore(context, "boundary.db").use { store ->
                val restored = requireNotNull(store.get(id))
                assertEquals(DocumentEngine.MAX_CHARS, restored.text.length)
                assertEquals(text, restored.text)
                assertEquals(document.summary, restored.summary)
                assertEquals(document.chunks, store.chunks(id))
                assertEquals(text, store.chunks(id).joinToString(""))
                assertEquals(listOf(id to "boundary.txt"), store.list("\u4e00\u4e00"))
            }
        } finally { context.deleteDatabase("boundary.db") }
    }
}
