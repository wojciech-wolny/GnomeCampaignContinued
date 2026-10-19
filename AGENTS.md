# GnomeCampaign — instrukcje dla agentów

Jednostrzałowa, humorystyczna przygoda do Pathfindera 1e dla 4–5 gnomów na 3. poziomie. Nocny dyżur w podwodnej gnomiej akademii magii: koboldy przebrane za studentów próbują ukraść złoty posąg dla smoka, psują przy tym barierę wodną, a bohaterowie muszą ją naprawić, zanim szkoła zatonie.

Cała kampania to pliki Markdown. Nie ma tu kodu ani testów.

---

## Struktura

```
GnomeCampaign/
├── README.md                 # nawigacja główna
├── MG/                       # TYLKO dla Mistrza Gry: tajemnice, rozwiązania, statystyki
│   ├── plan-sesji.md         # zegar powodzi (6 pól), cele, przebieg, ST
│   ├── mapa.md               # mapa z oznaczeniami MG
│   ├── zagadki.md            # zagadki z rozwiązaniami, procedury napraw
│   ├── bn.md                 # bohaterowie niezależni (BN)
│   ├── rekwizyty-kiedy.md    # kiedy wręczyć który rekwizyt R1–R9
│   ├── opisy/                # lokacje, historia posągu, smok i koboldy
│   ├── spotkania/            # S01–S12 (README.md = spis)
│   └── prompty/              # prompty do grafik i tekstowego przedstawienia drużyny
└── gracze/                   # materiały dla graczy — BEZ spoilerów
    ├── brief.md, mapa.md, rekwizyty.md, postacie-skrot.md
    ├── postacie/<postać>/    # sheet, spells, feats, features, backstory, state
    └── karty-do-druku/       # jednostronicowe karty A4 (skrót sheet.md)
```

Postacie (foldery): `pip-iskra-torren`, `luma-bramblewick`, `zizzle-stormpocket`, `orrin-quill`, `nixa-embercoil`.

---

## Zasady nadrzędne

### 1. Spoilery: granica MG / gracze

- Wszystko w `gracze/` gracze mogą przeczytać przed sesją. Nie wolno tam zdradzać: koboldów, kradzieży posągu, Kapitana Klika i jego ekipy (Fizzek, Wibcio, Tibusia, Brin Młodszy, Vex, Szczyp itd.), smoka Skarrzatha, kradzionego kryształu, wózka z posągiem, rozwiązania tablicy Triady, żywego mostka, liczby usterek („trzy naprawy”), konkretnych kabli (A/B/C).
- Wyjątek: `gracze/rekwizyty.md` — kartki wręczane w trakcie gry; mogą zawierać wskazówki.
- Dozwolone w `gracze/`: legenda o posągu (Brin, Fizz, Wib, Tib), Incydent z Żabą, Wielki Czerwony Przycisk, chochliki i Splot, smoczy kuzyn Nixy (mosiężny, dobry, bez związku z fabułą).
- Wszystko, co zdradza fabułę, idzie do `MG/`. W `MG/prompty/sceny.md` każda scena ma kolumnę „Kiedy pokazać”.

### 2. Język

- Wszystko po polsku, naturalnym językiem, bez angielskich wtrąceń.
- Jedyne wyjątki:
  - linijka `*Nazwa w podręczniku: English Name*` pod nagłówkiem `###` czaru lub atutu (do wyszukiwania na d20pfsrd). **Nie wstawiaj angielskiej nazwy do samego nagłówka** — psuje kotwice linków;
  - treść promptów obrazowych w `MG/prompty/` (generatory lepiej rozumieją angielski).
- Polska terminologia (D&D 3.5 / PF1e):

| Polski | Angielski | | Polski | Angielski |
|---|---|---|---|---|
| ST | DC | | BPA | BAB |
| KP | AC | | PMB | CMB |
| PW | HP | | OMB | CMD |
| SW | CR | | PR (poziom rzucającego) | CL |
| PD | XP | | KW | HD |
| Wytr / Ref / Wola | Fort / Ref / Will | | BN | NPC |
| `1k6`, `3k4+3` | `1d6`, `3d4+3` | | spotkania | encounters |
| rekwizyty | handouts | | sz (sztuki złota) | gp |

- Szkoły: wywoływanie, poznanie, przemiany, odrzucanie, zauroczanie, iluzja, nekromancja, przywoływanie. Linie krwi: baśniowa, smocza.

### 3. Kanon (nie zmieniaj bez prośby użytkownika)

- **Bohaterowie z posągu:** Brin, Fizz, Wib i **Tib — kobieta**, imię nieodmienne („posąg Brina, Fizza, Wiba i Tib”). Brin był żywym mostkiem; żyje na emeryturze na powierzchni (hoduje grzyby), w posągu zostało echo jego świadomości. Fizz żyje i uczy w akademii. Tib na emeryturze, jej twarz na plakatach BHP.
- **BN:** profesor Plink (stempel „NIE MOJA WINA”), bibliotekarka Vellum, chochlik Splot (płaci się mu kanapkami), Skarrzath „Łuskowa Skarbonka”.
- **Relacje między postaciami graczy** (szczegóły w `gracze/postacie/*/backstory.md` i tabeli w `gracze/postacie-skrot.md`):
  - Incydent z Żabą: Zizzle wziął kanapkę z pudełka Lumy (dla Splota), dołożył żywą żabę (leśny zwyczaj na szczęście) i dał Pipowi; żaba wskoczyła na pulpit alarmowy → ewakuacja w piżamach. Zizzle jest winien Lumie 17 kanapek. Orrin dwa razy odrzucił raport Pipa (notes „Incydent z Żabą, wersja 3”).
  - Nixa kichnęła iskrami i przypaliła Pipowi włosy; Pip twierdzi, że to jego eksperyment.
  - Nixa rozpala kocioł Lumy; Luma łata jej pelerynę („niepalna w 60%”, reszta to taśma).
  - Orrin tłumaczy Nixie listy od mosiężnego smoczego kuzyna; kuzyn twierdzi, że ząb w jej amulecie jest psi.
  - Zizzle i Nixa: Klub Urodzonych z Talentem (dwoje zaklinaczy, budżet: jedno ciastko).
  - Orrin trzyma w aktach list „legalny gnom” Zizzle'a.
- Historie postaci **nie nawiązują do koboldów**.

### 4. Mechanika

- Wszystkie postacie: gnomy, 3. poziom, zakup punktowy 20, premia za klasę preferowaną na umiejętności.
- ST czaru = 10 + krąg + modyfikator atrybutu (+1 Skupienie na czarach, +1 gnomia magia dla iluzji, +2 arkanum baśniowe dla **przymusu**, nie uroku).
- Zasięgi przy PR 3: bliski 30 stóp, średni 130 stóp, daleki 520 stóp. Czasy działania podawaj przeliczone, gdy to karta do druku.
- Zaklinacze na 3. poziomie **nie mają** czarów 2. kręgu.
- Zasada domowa: Luma rzuca Naprawę i Scalenie na instalacje akademii w 1 rundę.
- Wzmożone czary (Pip): +1 obrażeń raz na czar, nie na każdy pocisk.
- Statystyki weryfikuj przez serwer MCP `pathfinder` z tego repo (narzędzia: `search_spells`, `search_feats`, `search_classes`, `search_class_options`, `search_races`, `search_items`, `search_equipment`, `get_detail`, `check_feat_prerequisites`). Bez MCP: `mcp-server/.venv-win/Scripts/python.exe` + SQLite `db/pathfinder.db`.

---

## Gdzie zmiana musi być zsynchronizowana

| Gdy zmieniasz… | Popraw też… |
|---|---|
| statystykę w `postacie/<p>/sheet.md` | `karty-do-druku/<p>.md`, `postacie-skrot.md`, ewentualnie `state.md` (zasoby) |
| ST lub efekt czaru w `spells.md` | tabelę czarów w `sheet.md` i `karty-do-druku/<p>.md` |
| cytat, wygląd albo historię postaci | `sheet.md` (cytat pod nagłówkiem), `backstory.md`, `postacie-skrot.md`, `karty-do-druku/<p>.md`, `MG/prompty/postacie.md` |
| relację między postaciami | `backstory.md` obu postaci, tabelę relacji w `postacie-skrot.md`, sekcję „Kim jestem” w kartach do druku, sekcję Kanon w tym pliku |
| nazwę pliku lub nagłówek `###` | wszystkie linki i kotwice, które na niego wskazują |
| spotkanie S01–S12 | `MG/spotkania/README.md`, `MG/plan-sesji.md`, `MG/rekwizyty-kiedy.md` |
| nazwę lokacji | `MG/mapa.md`, `gracze/mapa.md`, `MG/opisy/lokacje.md`, `MG/prompty/sceny.md` |

---

## Styl pisania

- Ton humorystyczny, ciepły, absurd biurokratyczny (formularze, stemple, protokoły). Żarty nie mogą psuć czytelności zasad.
- Krótkie zdania. Pełne zdania zamiast skrótowców.
- Pola do odhaczania w kartach do druku: `☐`.
- Linki względne w Markdown; po zmianach nazw sprawdź, czy kotwice (`plik.md#nagłówek`) nadal pasują.

## Kontrola przed zakończeniem pracy

1. Szukaj spoilerów w plikach graczy, np. `rg -n -i "kobold|Klik|wózk|Skarrzath|\bVex\b|\bSzczyp\b|Brin Młodsz|mostek" GnomeCampaign/gracze` — jedyne dozwolone trafienia są w `rekwizyty.md`.
2. Szukaj angielskiej notacji kości: `rg -n "\b\d+d\d+" GnomeCampaign -g "!AGENTS.md"`.
3. Sprawdź, czy wartości w `sheet.md`, `karty-do-druku/` i `postacie-skrot.md` są zgodne.
