package com.sticktosales.escritorio;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;

/** Abre o Escritório Stick To Sales numa aba do Chrome (mesmo login do Claude no navegador). */
public class MainActivity extends Activity {
  static final String URL = "https://claude.ai/artifact/EQEku2m5GeGxQjZ3ttS9rW";
  static final String[] NAVEGADORES = {"com.android.chrome", "com.chrome.beta", "com.sec.android.app.sbrowser", "com.brave.browser", "com.microsoft.emmx"};
  private boolean abriu = false;

  @Override protected void onCreate(Bundle b) {
    super.onCreate(b);
    setContentView(R.layout.main);
    abriu = b != null && b.getBoolean("abriu");
  }

  @Override protected void onSaveInstanceState(Bundle out) {
    super.onSaveInstanceState(out);
    out.putBoolean("abriu", abriu);
  }

  @Override protected void onResume() {
    super.onResume();
    if (!abriu) { abriu = true; abrir(); }
  }

  @Override protected void onNewIntent(Intent intent) {
    super.onNewIntent(intent);
    abriu = false;
  }

  public void reabrir(View v) { abrir(); }

  public void sair(View v) { finish(); }

  private void abrir() {
    Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse(URL));
    Bundle extras = new Bundle();
    extras.putBinder("android.support.customtabs.extra.SESSION", null);
    i.putExtras(extras);
    i.putExtra("android.support.customtabs.extra.TOOLBAR_COLOR", 0xFF0E151A);
    i.putExtra("android.support.customtabs.extra.TITLE_VISIBILITY", 1);
    i.putExtra("android.support.customtabs.extra.SHARE_STATE", 2);
    for (String p : NAVEGADORES) {
      if (instalado(p)) { i.setPackage(p); break; }
    }
    try {
      startActivity(i);
    } catch (Exception e) {
      i.setPackage(null);
      try { startActivity(i); } catch (Exception ignored) { }
    }
  }

  private boolean instalado(String pacote) {
    try { getPackageManager().getPackageInfo(pacote, 0); return true; } catch (Exception e) { return false; }
  }
}
