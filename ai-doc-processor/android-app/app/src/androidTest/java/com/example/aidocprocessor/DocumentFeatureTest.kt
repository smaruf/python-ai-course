package com.example.aidocprocessor

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.*
import org.junit.Assume.assumeFalse
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class DocumentFeatureTest {
    @Test fun executeEveryFeatureScenario() {
        val lines = InstrumentationRegistry.getInstrumentation().context.assets.open("documents.feature")
            .bufferedReader().use { it.readLines() }.map { it.trim() }.filter { it.isNotEmpty() }
        var flow: UiFlow? = null
        var scenarios = 0
        var steps = 0
        try {
            lines.forEach { line ->
                when {
                    line.startsWith("Feature:") -> Unit
                    line.startsWith("Scenario:") -> { flow?.close(); flow = UiFlow(); scenarios++ }
                    else -> {
                        assertTrue("Unrecognized feature syntax: $line", line.startsWith("Given ") || line.startsWith("When ") || line.startsWith("Then ") || line.startsWith("And "))
                        val active = requireNotNull(flow) { "Step outside scenario" }
                        when (line.substringAfter(' ')) {
                            "an empty local document library" -> active.start()
                            "I import a UTF-8 document" -> active.importDocument()
                            "the summary and extracted text are visible" -> active.assertStored()
                            "I restart the app" -> active.restart()
                            "I open the stored document" -> active.viewDocument()
                            "searching for sapphire finds one document" -> active.search("sapphire", 1)
                            "searching for absent finds no documents" -> active.search("absent", 0)
                            "I clear the search" -> active.search("", 1)
                            "I delete the selected document" -> active.delete()
                            "the library remains empty after restart" -> { active.restart(); active.search("", 0) }
                            "I import an empty document" -> active.importDocument(empty = true)
                            "an error appears and nothing is stored" -> active.assertImportFailed()
                            "no local LLM model is installed" -> LocalAssistant(
                                InstrumentationRegistry.getInstrumentation().targetContext
                            ).use { assumeFalse("Run the missing-model scenario on a fresh installation", it.hasModel()) }
                            "I ask the local assistant about the document" -> active.askWithoutModel()
                            "the missing model is explained and the document is retained" -> active.assertStored()
                            else -> fail("Unknown BDD step: $line")
                        }
                        steps++
                    }
                }
            }
            assertEquals(3, scenarios)
            assertTrue(steps >= 10)
        } finally { flow?.close() }
    }
}
