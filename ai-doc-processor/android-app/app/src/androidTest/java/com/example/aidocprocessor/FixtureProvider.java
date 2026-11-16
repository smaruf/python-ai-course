package com.example.aidocprocessor;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;

public class FixtureProvider extends ContentProvider {
    public static final String FIXTURE_TEXT = "Local processing keeps documents private. A sapphire marker helps search this document. SQLite stores summaries on the device.";
    public static final Uri URI = Uri.parse("content://com.example.aidocprocessor.fixtures/document");

    @Override
    public boolean onCreate() {
        return true;
    }

    @Override
    public String getType(Uri uri) {
        return "text/plain";
    }

    @Override
    public Cursor query(Uri uri, String[] projection, String selection, String[] selectionArgs, String sortOrder) {
        MatrixCursor cursor = new MatrixCursor(new String[]{OpenableColumns.DISPLAY_NAME});
        cursor.addRow(new Object[]{"fixture.txt"});
        return cursor;
    }

    @Override
    public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
        if (!"r".equals(mode)) {
            throw new FileNotFoundException("Fixtures are read-only.");
        }
        File file = new File(getContext().getCacheDir(), "fixture.txt");
        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(new FileOutputStream(file), StandardCharsets.UTF_8))) {
            if ("load".equals(uri.getLastPathSegment())) {
                for (int index = 0; index < 800; index++) {
                    writer.write(FIXTURE_TEXT);
                    writer.write('\n');
                }
            } else if (!"empty".equals(uri.getLastPathSegment())) {
                writer.write(FIXTURE_TEXT);
            }
        } catch (IOException error) {
            FileNotFoundException failure = new FileNotFoundException("Unable to create document fixture.");
            failure.initCause(error);
            throw failure;
        }
        return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY);
    }

    @Override
    public Uri insert(Uri uri, ContentValues values) {
        throw new UnsupportedOperationException();
    }

    @Override
    public int delete(Uri uri, String selection, String[] selectionArgs) {
        throw new UnsupportedOperationException();
    }

    @Override
    public int update(Uri uri, ContentValues values, String selection, String[] selectionArgs) {
        throw new UnsupportedOperationException();
    }
}
