# Wydruki

Otwórz [index.html](index.html) w przeglądarce albo uruchom serwer:

```text
druk/.venv/Scripts/python.exe druk/serwer.py
```

Adres to `http://127.0.0.1:8080/`. Strona startowa daje wybór: wydruki albo katalog. W katalogu pliki Markdown otwierają się do czytania. Surowy plik jest pod adresem z `?zrodlo=1`. Zatrzymasz serwer skrótem Ctrl+C.

- [postacie/](postacie/index.html) — karty dla graczy. Ten folder można im dać. Arkusze do stołu (`arkusz-*.html`) mają układ karty Pathfindera, dwie strony na postać. Przy druku włącz grafiki tła.
- [mg/](mg/index.html) — materiały Mistrza Gry. Tu są tajemnice.

Druk: papier A4, skala 100%, bez nagłówków i stopek przeglądarki. Pola ☐ na kartach odhaczaj ołówkiem.

Po zmianie plików Markdown uruchom ponownie:

```text
druk/.venv/Scripts/python.exe druk/buduj.py
```

Przy pierwszym razie, jeśli brakuje środowiska: `python -m venv druk/.venv`, potem `druk/.venv/Scripts/python.exe -m pip install -r druk/requirements.txt`.
