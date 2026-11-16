package com.example.aidocprocessor

import android.content.ContentProvider
import android.content.ContentValues
import android.database.Cursor
import android.database.MatrixCursor
import android.net.Uri
import android.os.ParcelFileDescriptor
import android.provider.OpenableColumns

class FixtureProvider : ContentProvider() {
    override fun onCreate() = true
    override fun getType(uri: Uri) = "text/plain"
    override fun query(uri: Uri, projection: Array<out String>?, selection: String?, selectionArgs: Array<out String>?, sortOrder: String?): Cursor =
        MatrixCursor(arrayOf(OpenableColumns.DISPLAY_NAME)).apply { addRow(arrayOf("fixture.txt")) }
    override fun openFile(uri: Uri, mode: String): ParcelFileDescriptor {
        require(mode == "r")
        val file = java.io.File(context!!.cacheDir, "fixture.txt")
        file.writeText(when (uri.lastPathSegment) {
            "empty" -> ""
            "load" -> (FIXTURE_TEXT + "\n").repeat(800)
            else -> FIXTURE_TEXT
        })
        return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
    }
    override fun insert(uri: Uri, values: ContentValues?): Uri? = throw UnsupportedOperationException()
    override fun delete(uri: Uri, selection: String?, selectionArgs: Array<out String>?): Int = throw UnsupportedOperationException()
    override fun update(uri: Uri, values: ContentValues?, selection: String?, selectionArgs: Array<out String>?): Int = throw UnsupportedOperationException()

    companion object {
        const val FIXTURE_TEXT = "Local processing keeps documents private. A sapphire marker helps search this document. SQLite stores summaries on the device."
        val URI: Uri = Uri.parse("content://com.example.aidocprocessor.fixtures/document")
    }
}
