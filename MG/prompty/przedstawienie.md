# Przedstawienie bohaterów

[← Spis promptów](README.md)

Materiały na początek sesji: wspólny plakat drużyny, sceny z przeszłości bohaterów (wątki z ich historii) i prompt dla modelu językowego, który napisze tekst do odczytania na głos. Żaden z nich nie zdradza fabuły sesji.

---

## Plakat drużyny

Wklej styl wspólny z [postacie.md](postacie.md#styl-wspólny-wklejaj-na-początku-każdego-promptu), a potem:

```text
A group portrait of five young gnome wizards and sorcerers posing heroically, like a movie poster, in front of a giant glowing glass dome with the dark ocean behind it. From left to right:
Pip, spiky indigo hair singed at the tips, brass goggles on forehead, hex-key amulet, rubber gloves;
Luma, moss-green braid, crown of silver duct tape, greasy sleeves, holding a big adjustable wrench;
Zizzle, wild sunflower-yellow hair, beard drawn with chalk, painted freckles, colorful exchange student sash, huge grin;
Orrin, neat silver-blue hair, chalk behind ear, ink-stained fingers, armful of books full of bookmarks;
Nixa, flame-orange bun, copper freckles, patched scorched cloak, dog-tooth amulet, fire in her palm.
Everyone is slightly mismatched and funny, but clearly ready for trouble. Wide composition, dramatic lighting.
```

Jeśli przy czterech graczach odkładasz Nixę albo Orrina, usuń jego linijkę i zmień `five` na `four`.

---

## Sceny z przeszłości bohaterów

Te obrazki ilustrują wspólne wątki z plików `backstory.md`. Możesz pokazać je przy przedstawianiu postaci albo rozdać graczom jako pamiątki.

### Incydent z Żabą (Pip, Zizzle, Luma)

```text
Night in a gnomish academy alarm room. Zizzle, a forest gnome with sunflower-yellow hair and a chalk-drawn beard, proudly offers a sandwich as a welcome gift. A green frog leaps out of the sandwich straight onto a big alarm console full of buttons. Pip, a gnome with spiky indigo hair and goggles, recoils in horror. In the doorway Luma, with a moss-green braid and a duct tape crown, stares at her open, empty lunchbox. Red alarm lights begin to flash. Slapstick comedy, frozen moment of disaster.
```

### Ewakuacja w piżamach

```text
Dozens of sleepy gnome students and professors in pajamas, nightcaps and bunny slippers climbing a spiral staircase in an underwater academy, carrying pillows, books and a cat, while alarm lights flash red. In the corner Pip, a gnome with indigo hair and goggles, angrily writes in a notebook. Cozy chaos, humorous details everywhere.
```

### Kichnięcie Nixy (Nixa, Pip)

```text
Nixa, a gnome girl with a flame-orange bun and copper freckles, sneezes a burst of sparks. Right in front of her Pip, a gnome with spiky indigo hair, freezes as the tips of his hair start to smoke. Both look at each other in shock. Warm sparks in the air, comic timing.
```

### Kotłownia o świcie (Nixa, Luma)

```text
Early morning in a steamy boiler room. Nixa, a gnome with a flame-orange bun and a cloak covered in duct tape patches, lights a huge brass boiler with fire from her palm. Luma, a gnome with a moss-green braid and a duct tape crown, hands her a steaming mug of tea while holding a fresh roll of silver tape. Warm, friendly, peaceful mood.
```

### Archiwum raportów (Orrin, Pip, Zizzle)

```text
A quiet library archive at night. Orrin, a gnome with neat silver-blue hair and chalk behind his ear, secretly reads a handwritten report by candlelight, trying not to laugh, a red quill in hand. On the desk beside him lies a crumpled letter with a huge official stamp and many red corrections. Shelves of labelled folders, cozy candlelight.
```

### List od smoczego kuzyna (Nixa, Orrin)

```text
A family dinner table in a gnome home with one extra empty chair and a place setting sized for a dragon, a giant spoon and a giant plate. Nixa, a gnome with a flame-orange bun, holds a thirty-page letter written in draconic script. Next to her Orrin, a gnome with silver-blue hair, translates it with a magnifying glass, looking very uncomfortable. Warm, homely, humorous.
```

### Klub Urodzonych z Talentem (Zizzle, Nixa)

```text
A tiny secret club room in a broom closet, with a hand-painted banner and two chairs. Zizzle, a forest gnome with sunflower-yellow hair and a chalk-drawn beard, solemnly guards a single cookie on a velvet cushion as treasurer. Nixa, a gnome with a flame-orange bun, presides with a small gavel. Faint fey sparkles and fire sparks mix in the air. Mock-serious, charming.
```

---

## Prompt tekstowy: przedstawienie drużyny

Wklej ten prompt do ChatGPT, Claude albo innego modelu językowego. Pod nim wklej pełne treści pięciu plików `backstory.md` (z folderu `gracze/postacie/`). Model napisze tekst do odczytania na głos na początku sesji.

```text
Jesteś narratorem humorystycznej sesji RPG w systemie Pathfinder 1. edycji. Akcja dzieje się nocą w podwodnej gnomiej akademii magii, chronionej zaklętą kopułą. W atrium stoi złoty posąg czwórki dawnych bohaterów (Brin, Fizz, Wib i Tib), którzy przed laty uratowali szkołę przed powodzią.

Napisz po polsku tekst do odczytania na głos (około 2–3 minut), który przedstawi pięcioro bohaterów graczy pełniących nocny dyżur. Wymagania:
- Każda postać dostaje krótki akapit: jak wygląda, czym się zajmuje i jedno zdanie, które dobrze ją oddaje.
- Pokaż relacje między bohaterami: Incydent z Żabą (kanapka od Zizzle'a dla Pipa, zabrana z pudełka Lumy), przypalone włosy Pipa, peleryna Nixy łatana przez Lumę, listy od smoczego kuzyna tłumaczone przez Orrina, Klub Urodzonych z Talentem.
- Ton: ciepły, zabawny, z odrobiną patosu na końcu. Krótkie zdania, naturalny polski, bez angielskich wtrąceń.
- Zakończ chwilą, w której dyżur przestaje być nudny: w atrium rozlega się komunikat o „nieautoryzowanym przeniesieniu dziedzictwa kulturowego”, a z sufitu zaczyna kapać.
- Nie wymyślaj złoczyńców, przyczyny alarmu ani niczego, co wydarzy się później. Nie wspominaj o koboldach ani o kradzieży.

Historie postaci:
[WKLEJ TUTAJ TREŚĆ PIĘCIU PLIKÓW backstory.md]
```

### Wariant: potencjalne sceny

Jeśli chcesz przygotować się na różne kierunki sesji, wklej w tej samej rozmowie drugi prompt. Model zaproponuje sceny, w których relacje bohaterów mogą wyjść na wierzch.

```text
Na podstawie tych samych historii zaproponuj 8 krótkich scen (po 3–4 zdania), które mogą wydarzyć się podczas nocnego dyżuru i w których relacje między bohaterami odegrają rolę. Przykłady kierunków: Zizzle próbuje zaprzyjaźnić się z Pipem jedzeniem, bez przeprosin; Splot domaga się następnej kanapki odsetkowej w najgorszym możliwym momencie; Nixa kicha iskrami przy czymś łatwopalnym; Orrin musi przyznać na głos, że Luma miała rację co do schematu; Nixa domaga się drugiego tłumaczenia zdania o zębie.

Do każdej sceny dopisz:
- które postacie biorą w niej udział,
- jaki test umiejętności z Pathfindera 1e może się pojawić i z jakim ST (10–15),
- jedno zdanie do odczytania na głos na otwarcie sceny.

Pisz po polsku, w humorystycznym tonie. Nie wymyślaj przyczyny alarmu ani złoczyńców — te sceny mają działać niezależnie od fabuły głównej.
```
