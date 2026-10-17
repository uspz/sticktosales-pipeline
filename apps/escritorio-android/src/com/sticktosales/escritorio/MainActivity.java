package com.sticktosales.escritorio;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import org.json.JSONArray;
import org.json.JSONObject;

/** Central do Escritório no celular: abre o painel e posta o próximo vídeo no TikTok em um toque. */
public class MainActivity extends Activity {
  static final String URL_ESCRITORIO = "https://claude.ai/artifact/EQEku2m5GeGxQjZ3ttS9rW";
  static final String URL_FILA = "https://raw.githubusercontent.com/uspz/sticktosales-midia/main/fila.json";
  static final String[] NAVEGADORES = {"com.android.chrome", "com.chrome.beta", "com.sec.android.app.sbrowser", "com.brave.browser", "com.microsoft.emmx"};
  static final String[] TIKTOK = {"com.zhiliaoapp.musically", "com.ss.android.ugc.trill"};

  private TextView tTitulo, tQuando, tStatus, tResto;
  private Button bPostar, bFeito;
  private JSONArray itens;
  private JSONObject atual;
  private SharedPreferences postados;
  private boolean ocupado = false;

  @Override protected void onCreate(Bundle b) {
    super.onCreate(b);
    setContentView(R.layout.main);
    tTitulo = (TextView) findViewById(R.id.titulo);
    tQuando = (TextView) findViewById(R.id.quando);
    tStatus = (TextView) findViewById(R.id.status);
    tResto = (TextView) findViewById(R.id.resto);
    bPostar = (Button) findViewById(R.id.postar);
    bFeito = (Button) findViewById(R.id.feito);
    postados = getSharedPreferences("postados", MODE_PRIVATE);
    carregar();
  }

  @Override protected void onResume() {
    super.onResume();
    if (itens != null) mostrar();
  }

  public void atualizar(View v) { carregar(); }

  private void carregar() {
    tStatus.setText("Carregando a fila…");
    new Thread(new Runnable() { public void run() {
      try {
        JSONObject o = new JSONObject(texto(URL_FILA + "?t=" + System.currentTimeMillis()));
        final JSONArray a = o.getJSONArray("itens");
        runOnUiThread(new Runnable() { public void run() { itens = a; tStatus.setText(""); mostrar(); } });
      } catch (final Exception e) {
        runOnUiThread(new Runnable() { public void run() { tStatus.setText("Não consegui carregar a fila. Confira a internet e toque em Atualizar."); } });
      }
    }}).start();
  }

  private void mostrar() {
    atual = null;
    int resto = 0;
    for (int i = 0; i < itens.length(); i++) {
      JSONObject it = itens.optJSONObject(i);
      if (it == null || postados.getBoolean(it.optString("id"), false)) continue;
      if (atual == null) atual = it; else resto++;
    }
    boolean tem = atual != null;
    bPostar.setVisibility(tem ? View.VISIBLE : View.GONE);
    bFeito.setVisibility(tem ? View.VISIBLE : View.GONE);
    if (!tem) {
      tTitulo.setText("Tudo postado no TikTok");
      tQuando.setText("Quando sair lote novo, ele aparece aqui.");
      tResto.setText("");
      return;
    }
    long agora = System.currentTimeMillis() / 1000;
    String q = atual.optString("quando_txt");
    if (atual.optLong("quando") <= agora) q += " · já está na hora";
    tTitulo.setText(atual.optString("titulo"));
    tQuando.setText(q);
    tResto.setText(resto == 0 ? "É o último da fila." : "Depois dele: " + resto + " na fila.");
  }

  public void postar(View v) {
    if (atual == null || ocupado) return;
    ocupado = true;
    bPostar.setEnabled(false);
    tStatus.setText("Baixando o vídeo…");
    final JSONObject it = atual;
    new Thread(new Runnable() { public void run() {
      try {
        File pasta = new File(getCacheDir(), "videos");
        pasta.mkdirs();
        File f = new File(pasta, it.optString("id") + ".mp4");
        if (!f.exists() || f.length() == 0) baixar(it.optString("url"), f);
        final File pronto = f;
        runOnUiThread(new Runnable() { public void run() { abrirTikTok(it, pronto); } });
      } catch (final Exception e) {
        runOnUiThread(new Runnable() { public void run() {
          tStatus.setText("Não consegui baixar o vídeo. Confira a internet e tente de novo.");
          ocupado = false; bPostar.setEnabled(true);
        } });
      }
    }}).start();
  }

  private void abrirTikTok(JSONObject it, File f) {
    ocupado = false;
    bPostar.setEnabled(true);
    String legenda = it.optString("legenda");
    ClipboardManager cm = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
    if (cm != null) cm.setPrimaryClip(ClipData.newPlainText("legenda", legenda));
    Uri uri = Uri.parse("content://com.sticktosales.escritorio.videos/" + f.getName());
    Intent i = new Intent(Intent.ACTION_SEND);
    i.setType("video/mp4");
    i.putExtra(Intent.EXTRA_STREAM, uri);
    i.setClipData(ClipData.newRawUri("video", uri));
    i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
    tStatus.setText("Legenda copiada. No TikTok, cole na descrição e poste. Depois volte e toque em Já postei.");
    Toast.makeText(this, "Legenda copiada: cole na descrição", Toast.LENGTH_LONG).show();
    for (String p : TIKTOK) {
      if (!instalado(p)) continue;
      i.setPackage(p);
      try { startActivity(i); return; } catch (Exception ignored) { }
      i.setPackage(null);
    }
    try { startActivity(Intent.createChooser(i, "Postar com o TikTok")); }
    catch (Exception e) { tStatus.setText("Não achei o TikTok neste celular."); }
  }

  public void feito(View v) {
    if (atual == null) return;
    postados.edit().putBoolean(atual.optString("id"), true).apply();
    File f = new File(new File(getCacheDir(), "videos"), atual.optString("id") + ".mp4");
    if (f.exists()) f.delete();
    tStatus.setText("");
    mostrar();
  }

  public void reabrir(View v) {
    Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse(URL_ESCRITORIO));
    Bundle extras = new Bundle();
    extras.putBinder("android.support.customtabs.extra.SESSION", null);
    i.putExtras(extras);
    i.putExtra("android.support.customtabs.extra.TOOLBAR_COLOR", 0xFF0E151A);
    i.putExtra("android.support.customtabs.extra.TITLE_VISIBILITY", 1);
    for (String p : NAVEGADORES) {
      if (instalado(p)) { i.setPackage(p); break; }
    }
    try { startActivity(i); } catch (Exception e) {
      i.setPackage(null);
      try { startActivity(i); } catch (Exception ignored) { }
    }
  }

  private boolean instalado(String pacote) {
    try { getPackageManager().getPackageInfo(pacote, 0); return true; } catch (Exception e) { return false; }
  }

  private static String texto(String u) throws Exception {
    HttpURLConnection c = (HttpURLConnection) new URL(u).openConnection();
    c.setConnectTimeout(15000); c.setReadTimeout(20000);
    BufferedReader r = new BufferedReader(new InputStreamReader(c.getInputStream(), "UTF-8"));
    StringBuilder sb = new StringBuilder(); String l;
    while ((l = r.readLine()) != null) sb.append(l).append('\n');
    r.close(); c.disconnect();
    return sb.toString();
  }

  private static void baixar(String u, File destino) throws Exception {
    HttpURLConnection c = (HttpURLConnection) new URL(u).openConnection();
    c.setConnectTimeout(15000); c.setReadTimeout(60000); c.setInstanceFollowRedirects(true);
    if (c.getResponseCode() != 200) throw new Exception("http " + c.getResponseCode());
    File tmp = new File(destino.getPath() + ".parte");
    InputStream in = c.getInputStream(); FileOutputStream out = new FileOutputStream(tmp);
    byte[] buf = new byte[65536]; int n;
    while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
    out.close(); in.close(); c.disconnect();
    if (tmp.length() == 0 || !tmp.renameTo(destino)) throw new Exception("arquivo vazio");
  }
}
