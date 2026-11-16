package com.example.aidocprocessor

import java.io.ByteArrayInputStream
import java.io.IOException
import java.io.InputStream
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.After
import org.junit.Before
import org.junit.Test

class ModelFilesTest {
    private val directory = java.io.File("build/model-files-test")
    private fun newModel(): java.io.File = java.io.File(directory, "assistant-model.task")

    @Before fun setUp() {
        check(directory.mkdirs() || directory.isDirectory)
    }

    @After fun cleanUp() {
        directory.deleteRecursively()
    }

    @Test fun replacesModelOnlyAfterCompleteCopy() {
        val target = newModel()
        target.writeText("old")
        ModelFiles.install(ByteArrayInputStream("new".toByteArray()), target, 3)
        assertEquals("new", target.readText())
        assertFalse(java.io.File(target.parentFile, target.name + ".importing").exists())
    }

    @Test fun oversizedAndEmptyImportsPreserveExistingModel() {
        val target = newModel()
        target.writeText("old")
        listOf(byteArrayOf(), ByteArray(4)).forEach { bytes ->
            try {
                ModelFiles.install(ByteArrayInputStream(bytes), target, 3)
                throw AssertionError("Expected invalid model")
            } catch (_: IllegalArgumentException) {
            }
            assertEquals("old", target.readText())
            assertFalse(java.io.File(target.parentFile, target.name + ".importing").exists())
        }
    }

    @Test fun readFailureCleansStagingFileAndClosesStream() {
        val target = newModel()
        target.writeText("old")
        var closed = false
        val broken = object : InputStream() {
            override fun read(): Int = throw IOException("provider unavailable")
            override fun close() { closed = true }
        }
        try {
            ModelFiles.install(broken, target, 3)
            throw AssertionError("Expected read failure")
        } catch (_: IOException) {
        }
        assertEquals("old", target.readText())
        assertFalse(java.io.File(target.parentFile, target.name + ".importing").exists())
        assertEquals(true, closed)
    }

    @Test fun copiesBinaryDataAndRunsCallbackBeforeReplacement() {
        val target = newModel()
        target.writeText("old")
        val data = byteArrayOf(0, 1, -1)
        var callback = false
        ModelFiles.install(ByteArrayInputStream(data), target, 3) {
            assertEquals("old", target.readText())
            callback = true
        }
        assertEquals(true, callback)
        assertArrayEquals(data, target.readBytes())
    }

    @Test fun callbackFailurePreservesExistingModel() {
        val target = newModel()
        target.writeText("old")
        try {
            ModelFiles.install(ByteArrayInputStream(byteArrayOf(1)), target, 3) {
                throw IOException("cannot release engine")
            }
            throw AssertionError("Expected callback failure")
        } catch (_: IOException) {
        }
        assertEquals("old", target.readText())
        assertFalse(java.io.File(target.parentFile, target.name + ".importing").exists())
    }
}
