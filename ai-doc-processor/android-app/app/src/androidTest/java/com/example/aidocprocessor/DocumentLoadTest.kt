package com.example.aidocprocessor

import android.os.Bundle
import android.os.SystemClock
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class DocumentLoadTest {
    @Test fun boundedRepeatedImportsPersistWithinBudget() {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        val context = instrumentation.targetContext
        context.deleteDatabase("load.db")
        val started = SystemClock.elapsedRealtime()
        val iterations = 30
        var processedCharacters = 0L
        try {
            DocumentStore(context, "load.db").use { store ->
                repeat(iterations) {
                    val (name, document) = DocumentExtractor(context).extract(FixtureProvider.URI.buildUpon().path("load").build())
                    assertTrue(document.text.length >= 100_000)
                    processedCharacters += document.text.length
                    val id = store.save(name, document)
                    assertEquals(document.text, store.get(id)!!.text)
                    assertEquals(document.summary, store.get(id)!!.summary)
                    assertEquals(document.text, store.chunks(id).joinToString(""))
                    assertEquals(it + 1, store.list("sapphire").size)
                    assertTrue("30 imports must complete within 30 seconds", SystemClock.elapsedRealtime() - started < 30_000)
                }
            }
            DocumentStore(context, "load.db").use { assertEquals(iterations, it.list("sapphire").size) }
            val elapsed = SystemClock.elapsedRealtime() - started
            assertTrue("Entire workload must complete within 30 seconds", elapsed < 30_000)
            val charactersPerSecond = processedCharacters * 1000.0 / elapsed.coerceAtLeast(1)
            instrumentation.sendStatus(0, Bundle().apply {
                putString("stream", "Load report: $iterations serialized SAF extraction + SQLite imports (>=100K characters each), ${elapsed}ms, $charactersPerSecond characters/second, budget 30000ms\n")
                putLong("load_elapsed_ms", elapsed); putInt("load_imports", iterations)
                putLong("load_processed_characters", processedCharacters)
                putDouble("load_characters_per_second", charactersPerSecond)
            })
        } finally { context.deleteDatabase("load.db") }
    }
}
