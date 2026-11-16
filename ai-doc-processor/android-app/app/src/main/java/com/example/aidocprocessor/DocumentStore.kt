package com.example.aidocprocessor

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

data class StoredDocument(val id: Long, val name: String, val text: String, val summary: String)

class DocumentStore(context: Context, name: String = "documents.db") : SQLiteOpenHelper(context, name, null, 1) {
    override fun onConfigure(db: SQLiteDatabase) { db.setForeignKeyConstraintsEnabled(true) }
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("CREATE TABLE documents (id INTEGER PRIMARY KEY, name TEXT NOT NULL, text TEXT NOT NULL, summary TEXT NOT NULL)")
        db.execSQL("CREATE TABLE chunks (document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE, position INTEGER NOT NULL, text TEXT NOT NULL, PRIMARY KEY(document_id, position))")
    }
    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) = Unit

    fun save(name: String, document: ProcessedDocument): Long {
        val db = writableDatabase
        db.beginTransaction()
        try {
            val id = db.insertOrThrow("documents", null, ContentValues().apply {
                put("name", name); put("text", document.text); put("summary", document.summary)
            })
            document.chunks.forEachIndexed { position, text ->
                db.insertOrThrow("chunks", null, ContentValues().apply {
                    put("document_id", id); put("position", position); put("text", text)
                })
            }
            db.setTransactionSuccessful()
            return id
        } finally { db.endTransaction() }
    }

    fun list(query: String = ""): List<Pair<Long, String>> =
        readableDatabase.rawQuery(
            "SELECT id, name FROM documents WHERE instr(lower(text), lower(?)) > 0 OR instr(lower(name), lower(?)) > 0 ORDER BY id DESC",
            arrayOf(query, query)
        ).use { cursor -> buildList { while (cursor.moveToNext()) add(cursor.getLong(0) to cursor.getString(1)) } }

    fun get(id: Long): StoredDocument? = readableDatabase.rawQuery(
        "SELECT id, name, text, summary FROM documents WHERE id = ?", arrayOf(id.toString())
    ).use { c -> if (c.moveToFirst()) StoredDocument(c.getLong(0), c.getString(1), c.getString(2), c.getString(3)) else null }

    fun chunks(id: Long): List<String> = readableDatabase.rawQuery(
        "SELECT text FROM chunks WHERE document_id = ? ORDER BY position", arrayOf(id.toString())
    ).use { c -> buildList { while (c.moveToNext()) add(c.getString(0)) } }

    fun delete(id: Long) { writableDatabase.delete("documents", "id = ?", arrayOf(id.toString())) }
}
