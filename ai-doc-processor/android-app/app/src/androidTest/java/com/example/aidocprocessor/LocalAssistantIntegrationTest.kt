package com.example.aidocprocessor

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import java.util.concurrent.ExecutionException
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeFalse
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class LocalAssistantIntegrationTest {
    @Test fun overlappingOwnersCloseExactlyOnce() = onWorker { first ->
        val field = LocalAssistant::class.java.getDeclaredField("owners")
        field.isAccessible = true
        val owners = field.get(null) as AtomicInteger
        val initial = owners.get()
        LocalAssistant(InstrumentationRegistry.getInstrumentation().targetContext).use { second ->
            assertEquals(initial + 1, owners.get())
            first.close()
            assertEquals(initial, owners.get())
            first.close()
            assertEquals(initial, owners.get())
            second.close()
            assertEquals(initial - 1, owners.get())
            second.close()
            assertEquals(initial - 1, owners.get())
        }
    }

    @Test fun missingModelLeavesOfflineToolsUsable() = onWorker { assistant ->
        assumeFalse("Run without an imported model to verify the absent-model path.", assistant.hasModel())
        try {
            assistant.answer("The meeting is Monday.", "When is the meeting?")
            throw AssertionError("Expected missing-model message")
        } catch (error: IllegalStateException) {
            assertTrue(error.message.orEmpty().contains("Import a compatible local"))
        }
        assertTrue(DocumentEngine.process("The meeting is Monday.").summary.isNotBlank())
        assistant.removeModel()
        assertFalse(assistant.hasModel())
        assistant.close()
        assertFalse(assistant.hasModel())
    }

    @Test fun realNativeInferenceWithUserSuppliedModel() = onWorker { assistant ->
        assumeTrue("Import a separately licensed compatible model before running native inference.", assistant.hasModel())
        val answer = assistant.answer("The meeting is Monday.", "When is the meeting?")
        assertTrue(answer.isNotBlank())
        assertFalse(answer.contains("The model returned no answer"))
    }

    private fun onWorker(action: (LocalAssistant) -> Unit) {
        val executor = Executors.newSingleThreadExecutor()
        try {
            executor.submit {
                LocalAssistant(InstrumentationRegistry.getInstrumentation().targetContext).use(action)
            }.get(5, TimeUnit.MINUTES)
        } catch (error: ExecutionException) {
            throw error.cause ?: error
        } finally {
            executor.shutdown()
        }
    }
}
