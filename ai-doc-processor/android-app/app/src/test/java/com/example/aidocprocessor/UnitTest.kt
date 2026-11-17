package com.example.aidocprocessor

import org.junit.Assert.*
import org.junit.Test
import java.io.ByteArrayInputStream

class UnitTest {
    @Test fun extractiveSummaryIsDeterministicAndOrdered() {
        val text = "Cats enjoy sunshine. Cats enjoy gardens. Rain falls outside. Cats sleep quietly."
        val summary = DocumentEngine.process(text).summary
        assertEquals(summary, DocumentEngine.process(text).summary)
        assertEquals(3, summary.lines().size)
        assertTrue(summary.lines().all { text.contains(it) })
        assertEquals(summary.lines(), summary.lines().sortedBy { text.indexOf(it) })
    }
    @Test fun chunksRoundTripWithoutSplittingSurrogates() {
        val text = "x".repeat(1999) + "😀" + "end".repeat(1000)
        val chunks = DocumentEngine.chunks(text)
        assertEquals(text, chunks.joinToString(""))
        assertTrue(chunks.all { it.length <= DocumentEngine.CHUNK_SIZE })
        assertFalse(chunks.first().last().isHighSurrogate())
    }
    @Test fun emptyTextFails() { assertThrows(IllegalArgumentException::class.java) { DocumentEngine.process(" \n") } }
    @Test fun characterLimitFails() { assertThrows(IllegalArgumentException::class.java) { DocumentEngine.process("x".repeat(DocumentEngine.MAX_CHARS + 1)) } }
    @Test fun byteLimitIsEnforced() {
        assertEquals(DocumentEngine.MAX_BYTES, DocumentEngine.readBounded(ByteArrayInputStream(ByteArray(DocumentEngine.MAX_BYTES))).size)
        assertThrows(IllegalArgumentException::class.java) { DocumentEngine.readBounded(ByteArrayInputStream(ByteArray(DocumentEngine.MAX_BYTES + 1))) }
    }
    @Test fun strictUtf8AndBom() {
        assertEquals("café", DocumentEngine.decodeUtf8("\uFEFFcafé".toByteArray()))
        assertThrows(java.nio.charset.CharacterCodingException::class.java) { DocumentEngine.decodeUtf8(byteArrayOf(0xc3.toByte())) }
    }
    @Test fun binaryAndSummaryBounds() {
        assertThrows(IllegalArgumentException::class.java) { DocumentEngine.process("binary\u0000") }
        assertTrue(DocumentEngine.process("word ".repeat(10000)).summary.length <= 1500)
        assertEquals("", DocumentEngine.summarize(""))
    }
    @Test fun previewBoundaryDoesNotSplitSurrogatePairs() {
        val text = "x".repeat(19_999) + "😀tail"
        assertEquals("x".repeat(19_999), DocumentEngine.boundedPrefix(text, 20_000))
        assertEquals("x".repeat(19_999) + "😀", DocumentEngine.boundedPrefix(text, 20_001))
        assertEquals("short", DocumentEngine.boundedPrefix("short", 20_000))
        assertEquals("", DocumentEngine.boundedPrefix(text, 0))
    }
    @Test fun summaryBoundaryDoesNotSplitSurrogatePairs() {
        val summary = DocumentEngine.summarize("x".repeat(1499) + "😀tail")
        assertEquals("x".repeat(1499), summary)
    }
}
