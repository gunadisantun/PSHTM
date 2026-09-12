# PSHTM Daily Instagram Agent

Repository khusus untuk otomasi konten Instagram PSHTM.

Alur utama:
1. GitHub Actions berjalan setiap hari pukul 07.00 WIB.
2. Agent mengambil berita terbaru dari RSS publik.
3. Berita diberi skor berdasarkan relevansi hukum, teknologi, media, privasi, keamanan siber, dan AI.
4. Agent menghindari topik yang mirip dengan posting 14 hari terakhir.
5. Agent membuat visual 1080x1350 dengan identitas teks di footer: `Pusat Studi Hukum, Teknologi dan Media` dan `IKA FH UNDIP`.
6. Mode awal adalah dry-run, jadi tidak mem-posting ke Instagram sampai kredensial Meta disiapkan.

## GitHub Secrets

Untuk mengaktifkan publikasi Instagram, tambahkan:
- `IG_USER_ID`
- `IG_ACCESS_TOKEN`

Jangan simpan token di source code.

## Status

Tahap awal: generate konten dan visual otomatis terlebih dahulu. Auto-publish diaktifkan setelah hasil desain dan sumber berita sudah disetujui.
