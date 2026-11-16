package com.example.aidocprocessor

import java.io.File
import java.io.FileOutputStream
import java.io.InputStream
import java.nio.file.Files
import java.nio.file.StandardCopyOption

internal object ModelFiles {
    const val MAX_MODEL_BYTES = 2L * 1024 * 1024 * 1024

    fun install(
        input: InputStream,
        target: File,
        maxBytes: Long = MAX_MODEL_BYTES,
        beforeReplace: () -> Unit = {}
    ) {
        val staging = File(target.parentFile, target.name + ".importing")
        try {
            input.use { source ->
                FileOutputStream(staging).use { output ->
                    val buffer = ByteArray(64 * 1024)
                    var total = 0L
                    while (true) {
                        val count = source.read(buffer)
                        if (count < 0) break
                        total += count
                        require(total <= maxBytes) { "Model exceeds the 2 GiB import limit." }
                        output.write(buffer, 0, count)
                    }
                    require(total > 0) { "Model file is empty." }
                    output.fd.sync()
                }
            }
            beforeReplace()
            // Both files are in private storage on the same filesystem; never delete the old model first.
            Files.move(staging.toPath(), target.toPath(),
                StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING)
        } finally {
            staging.delete()
        }
    }
}
