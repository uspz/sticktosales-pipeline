package com.sticktosales.escritorio;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;
import java.io.File;
import java.io.FileNotFoundException;

/** Entrega o vídeo baixado para o TikTok sem precisar salvar na galeria. */
public class Videos extends ContentProvider {
  @Override public boolean onCreate() { return true; }

  private File arquivo(Uri uri) throws FileNotFoundException {
    String n = uri.getLastPathSegment();
    if (n == null || n.contains("/") || n.contains("..")) throw new FileNotFoundException();
    File f = new File(new File(getContext().getCacheDir(), "videos"), n);
    if (!f.exists()) throw new FileNotFoundException();
    return f;
  }

  @Override public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
    return ParcelFileDescriptor.open(arquivo(uri), ParcelFileDescriptor.MODE_READ_ONLY);
  }

  @Override public String getType(Uri uri) { return "video/mp4"; }

  @Override public Cursor query(Uri uri, String[] p, String s, String[] a, String o) {
    MatrixCursor c = new MatrixCursor(new String[]{OpenableColumns.DISPLAY_NAME, OpenableColumns.SIZE});
    try { File f = arquivo(uri); c.addRow(new Object[]{f.getName(), f.length()}); } catch (Exception ignored) { }
    return c;
  }

  @Override public Uri insert(Uri uri, ContentValues v) { return null; }
  @Override public int delete(Uri uri, String s, String[] a) { return 0; }
  @Override public int update(Uri uri, ContentValues v, String s, String[] a) { return 0; }
}
