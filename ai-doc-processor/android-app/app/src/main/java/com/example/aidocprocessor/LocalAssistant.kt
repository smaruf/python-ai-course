package com.example.aidocprocessor

import android.content.Context
import android.net.Uri
import android.os.Looper
import android.provider.OpenableColumns
import com.google.mediapipe.tasks.genai.llminference.LlmInference
import java.io.Closeable
import java.io.File
import java.io.IOException
import java.nio.file.Files
import java.util.Locale

/**
 * Optional on-device inference. Blocking operations must run on a worker thread.
 * Users supply a separately licensed, MediaPipe-compatible .task or .bin model, not GGUF.
 * Generated answers are unverified; only a bounded initial document excerpt is provided.
 */
class LocalAssistant(context: Context) : Closeable {
    private val appContext = context.applicationContext
    private val modelFile = File(appContext.filesDir, "assistant-model.task")
    @Volatile private var closed = false

    private companion object {
        // Activity recreation can leave an older worker alive. Share both the lock and native session.
        val lock = Any()
        var engine: LlmInference? = null
    }

    fun hasModel(): Boolean = !closed && modelFile.isFile && modelFile.length() > 0

    fun importModel(uri: Uri): Unit = synchronized(lock) {
        checkWorker()
        checkOpen()
        require(uri.scheme == "content") { "Choose a model with the Android file picker." }
        val name = appContext.contentResolver.query(
            uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null
        )?.use { cursor ->
            if (cursor.moveToFirst()) cursor.getString(0) else null
        }.orEmpty().lowercase(Locale.ROOT)
        require(name.endsWith(".task") || name.endsWith(".bin")) {
            "Choose a MediaPipe-compatible .task or .bin model (GGUF is not supported)."
        }
        try {
            val input = appContext.contentResolver.openInputStream(uri)
                ?: throw IOException("Cannot open the selected model.")
            ModelFiles.install(input, modelFile) { releaseEngine() }
        } catch (error: IOException) {
            throw IllegalStateException("Model import failed. Check free space and file access; the previous model is unchanged.", error)
        }
    }

    fun answer(documentText: String, question: String): String = synchronized(lock) {
        checkWorker()
        checkOpen()
        AssistantPrompt.validate(documentText, question)
        check(hasModel()) {
            "Import a compatible local .task or .bin model first. Offline document tools work without a model."
        }
        try {
            val inference = engine ?: LlmInference.createFromOptions(
                appContext,
                LlmInference.LlmInferenceOptions.builder()
                    .setModelPath(modelFile.absolutePath)
                    .setMaxTokens(AssistantPrompt.MAX_TOKENS)
                    .setPreferredBackend(LlmInference.Backend.DEFAULT)
                    .build()
            ).also { engine = it }
            val prompt = AssistantPrompt.build(documentText, question, inference::sizeInTokens)
            inference.generateResponse(prompt).trim().ifBlank {
                "The model returned no answer. Try a shorter question."
            }
        } catch (error: LinkageError) {
            releaseEngine()
            throw IllegalStateException("Native local inference is unavailable on this device. Offline document tools remain available.", error)
        } catch (error: IllegalArgumentException) {
            throw error
        } catch (error: RuntimeException) {
            releaseEngine()
            throw IllegalStateException("Local inference failed. Verify this is a compatible MediaPipe model and that the device has enough memory.", error)
        }
    }

    fun removeModel(): Unit = synchronized(lock) {
        checkWorker()
        checkOpen()
        releaseEngine()
        try {
            Files.deleteIfExists(modelFile.toPath())
        } catch (error: IOException) {
            throw IllegalStateException("Could not remove the local model.", error)
        }
    }

    override fun close(): Unit = synchronized(lock) {
        checkWorker()
        if (closed) return
        closed = true
        releaseEngine()
    }

    private fun checkOpen() = check(!closed) { "Local assistant is closed." }

    private fun checkWorker() = check(Looper.myLooper() != Looper.getMainLooper()) {
        "Local model operations must run on a worker thread."
    }

    private fun releaseEngine() {
        val previous = engine
        engine = null
        try {
            previous?.close()
        } catch (_: LinkageError) {
            // Native startup may fail partway through; retain the offline app's usability.
        } catch (_: RuntimeException) {
        }
    }
}
