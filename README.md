# 🎰 Lotería Texas — Analizador

Dashboard estático de Mega Millions y Powerball con datos oficiales de la
[Texas Lottery](https://www.texaslottery.com): frecuencias por número, pares
con mayor concurrencia (mapa de calor) y generador de boletos con 4 estrategias.

**Cómo funciona**

- `build_stats.py` descarga los CSV oficiales y escribe `stats.json`.
- GitHub Actions ([`update-data.yml`](.github/workflows/update-data.yml)) lo
  corre a diario a las 10:30 UTC y hace commit si hay sorteos nuevos.
- GitHub Pages sirve `index.html`, que lee `stats.json`; el generador de
  boletos corre por completo en el navegador.

**Publicar**

1. Crea un repo y sube estos archivos.
2. En *Settings → Pages*, elige *Deploy from a branch* → `main` → `/ (root)`.
3. En *Settings → Actions → General*, verifica que los workflows tengan
   permiso de escritura (*Read and write permissions*).

⚠️ Cada sorteo es un evento independiente: este análisis es estadística
descriptiva y entretenimiento; no mejora las probabilidades reales de ganar.
