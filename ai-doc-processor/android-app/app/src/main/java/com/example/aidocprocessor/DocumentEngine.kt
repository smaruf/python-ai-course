package com.example.aidocprocessor

import java.io.InputStream
import java.nio.ByteBuffer
import java.nio.charset.CodingErrorAction
import java.util.Locale

data class ProcessedDocument(val text: String, val summary: String, val chunks: List<String>)

object DocumentEngine {
    const val MAX_BYTES = 10 * 1024 * 1024
    const val MAX_CHARS = 500_000
    const val MAX_PAGES = 200
    const val CHUNK_SIZE = 2_000

    fun readBounded(input: InputStream): ByteArray {
        val output = java.io.ByteArrayOutputStream()
        val buffer = ByteArray(8192)
        while (true) {
            val count = input.read(buffer)
            if (count < 0) break
            require(output.size() + count <= MAX_BYTES) { "File exceeds 10 MiB limit." }
            output.write(buffer, 0, count)
        }
        return output.toByteArray()
    }

    fun decodeUtf8(bytes: ByteArray): String {
        require(bytes.size <= MAX_BYTES) { "File exceeds 10 MiB limit." }
        return Charsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(bytes))
            .toString().removePrefix("\uFEFF")
    }

    fun process(raw: String): ProcessedDocument {
        require(raw.length <= MAX_CHARS) { "Text exceeds 500,000 character limit." }
        val text = raw.trim()
        require(text.isNotBlank()) { "No readable text. Scanned PDFs need OCR, which is not supported." }
        require(!text.contains('\u0000')) { "Not a plain text document." }
        return ProcessedDocument(text, summarize(text), chunks(text))
    }

    fun chunks(text: String): List<String> {
        require(text.length <= MAX_CHARS) { "Text exceeds character limit." }
        val result = mutableListOf<String>()
        var start = 0
        while (start < text.length) {
            var end = (start + CHUNK_SIZE).coerceAtMost(text.length)
            if (end < text.length && text[end - 1].isHighSurrogate() && text[end].isLowSurrogate()) end--
            result.add(text.substring(start, end))
            start = end
        }
        return result
    }

    fun summarize(text: String): String {
        require(text.length <= MAX_CHARS) { "Text exceeds character limit." }
        val sentences = text.split(Regex("(?<=[.!?])\\s+|\\n+")).filter { it.isNotBlank() }
        if (sentences.isEmpty()) return ""
        val words = Regex("[\\p{L}\\p{N}]{3,}")
        val stop = setOf("the", "and", "for", "that", "with", "this", "are", "was", "from", "have")
        val frequencies = mutableMapOf<String, Int>()
        fun tokens(sentence: String) = words.findAll(sentence.lowercase(Locale.ROOT))
            .map { it.value }.filter { it !in stop }.toList()
        sentences.forEach { s -> tokens(s).forEach { frequencies[it] = (frequencies[it] ?: 0) + 1 } }
        return sentences.indices.sortedWith(compareByDescending<Int> { index ->
            val terms = tokens(sentences[index])
            terms.sumOf { frequencies[it] ?: 0 }.toDouble() / terms.size.coerceAtLeast(1)
        }.thenBy { it }).take(3).sorted().joinToString("\n") { sentences[it].trim() }.take(1500)
    }
}
