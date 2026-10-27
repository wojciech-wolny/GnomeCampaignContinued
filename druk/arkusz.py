"""Filled Pathfinder 1e character sheets for the five pregenerated gnomes.

The pages follow the two-page core sheet: identity and abilities, armor class,
saves, weapons and the full skill list on the first page; armor, gear, feats,
special abilities and spells on the second. Labels are Polish. Numbers come
from the character sheets and are checked against those totals before any HTML
is written.
"""

import html
from dataclasses import dataclass, field

type Scores = dict[str, int]


def mods(scores: Scores) -> dict[str, int]:
    """Return ability modifiers for a score map.

    :param scores: ability key to score
    :return: ability key to modifier
    """
    return {key: (score - 10) // 2 for key, score in scores.items()}


def signed(number: int) -> str:
    """Format a bonus with a sign.

    :param number: integer bonus
    :return: ``+2``, ``+0`` or a unicode minus
    """
    if number < 0:
        return f"−{abs(number)}"
    return f"+{number}"


def escape(text: str) -> str:
    """Escape text for HTML.

    :param text: raw text
    :return: escaped text
    """
    return html.escape(text, quote=True)


WIEDZA = (
    "magia",
    "lochy",
    "inzynieria",
    "geografia",
    "historia",
    "lokalna",
    "natura",
    "szlachectwo",
    "plany",
    "religia",
)

SKILLS: tuple[tuple[str, str, str, bool], ...] = (
    ("akrobatyka", "Akrobatyka", "zre", False),
    ("szacowanie", "Szacowanie", "inte", False),
    ("blefowanie", "Blefowanie", "cha", False),
    ("wspinaczka", "Wspinaczka", "sil", False),
    ("rzemioslo1", "Rzemiosło", "inte", False),
    ("rzemioslo2", "Rzemiosło", "inte", False),
    ("rzemioslo3", "Rzemiosło", "inte", False),
    ("dyplomacja", "Dyplomacja", "cha", False),
    ("unieszkodliwianie", "Unieszkodliwianie mechanizmów", "zre", True),
    ("przebieranie", "Przebieranie się", "cha", False),
    ("wyzwalanie", "Wyzwalanie się", "zre", False),
    ("latanie", "Latanie", "zre", False),
    ("opieka", "Opieka nad zwierzętami", "cha", True),
    ("leczenie", "Leczenie", "mdr", False),
    ("zastraszanie", "Zastraszanie", "cha", False),
    ("wiedza-magia", "Wiedza (magia)", "inte", True),
    ("wiedza-lochy", "Wiedza (lochów)", "inte", True),
    ("wiedza-inzynieria", "Wiedza (inżynieria)", "inte", True),
    ("wiedza-geografia", "Wiedza (geografia)", "inte", True),
    ("wiedza-historia", "Wiedza (historia)", "inte", True),
    ("wiedza-lokalna", "Wiedza (lokalna)", "inte", True),
    ("wiedza-natura", "Wiedza (natura)", "inte", True),
    ("wiedza-szlachectwo", "Wiedza (szlachectwo)", "inte", True),
    ("wiedza-plany", "Wiedza (plany)", "inte", True),
    ("wiedza-religia", "Wiedza (religia)", "inte", True),
    ("lingwistyka", "Lingwistyka", "inte", True),
    ("percepcja", "Percepcja", "mdr", False),
    ("wystepy1", "Występy", "cha", False),
    ("wystepy2", "Występy", "cha", False),
    ("profesja1", "Profesja", "mdr", True),
    ("profesja2", "Profesja", "mdr", True),
    ("jezdziectwo", "Jeździectwo", "zre", False),
    ("wyczucie", "Wyczucie pobudek", "mdr", False),
    ("zreczna-dlon", "Zręczna dłoń", "zre", True),
    ("czaroznawstwo", "Czaroznawstwo", "inte", True),
    ("skradanie", "Skradanie się", "zre", False),
    ("przetrwanie", "Sztuka przetrwania", "mdr", False),
    ("plywanie", "Pływanie", "sil", False),
    ("ump", "Używanie magicznych przedmiotów", "cha", True),
)

ABILITY_LABELS = (
    ("sil", "SIŁ", "siła"),
    ("zre", "ZRĘ", "zręczność"),
    ("bud", "BUD", "budowa"),
    ("inte", "INT", "inteligencja"),
    ("mdr", "MDR", "mądrość"),
    ("cha", "CHA", "charyzma"),
)

ABILITY_ABBR = {key: label for key, label, _name in ABILITY_LABELS}

GNOME_MISC = {"skradanie": 4, "percepcja": 2}


def wizard_skills(*extra: str) -> set[str]:
    """Class skills of a wizard, plus campaign traits.

    :param extra: additional class skills
    :return: skill keys
    """
    skills = {
        "szacowanie",
        "latanie",
        "lingwistyka",
        "czaroznawstwo",
        "rzemioslo1",
        "rzemioslo2",
        "rzemioslo3",
        "profesja1",
        "profesja2",
    }
    skills.update(f"wiedza-{name}" for name in WIEDZA)
    skills.update(extra)
    return skills


def sorcerer_skills(*extra: str) -> set[str]:
    """Class skills of a sorcerer, plus campaign traits.

    :param extra: additional class skills
    :return: skill keys
    """
    skills = {
        "szacowanie",
        "blefowanie",
        "latanie",
        "zastraszanie",
        "wiedza-magia",
        "czaroznawstwo",
        "ump",
        "rzemioslo1",
        "rzemioslo2",
        "rzemioslo3",
        "profesja1",
        "profesja2",
    }
    skills.update(extra)
    return skills


@dataclass(frozen=True)
class Training:
    ranks: int = 0
    misc: int = 0
    label: str = ""


@dataclass(frozen=True)
class Weapon:
    name: str = ""
    attack: str = ""
    critical: str = ""
    kind: str = ""
    reach: str = ""
    ammo: str = ""
    damage: str = ""


@dataclass(frozen=True)
class Character:
    slug: str
    name: str
    quote: str
    alignment: str
    class_line: str
    deity: str
    homeland: str
    race: str
    gender: str
    age: str
    hair: str
    scores: Scores
    hp: int
    init_misc: int
    natural: int
    ranks_total: int
    class_skills: set[str]
    training: dict[str, Training]
    skill_checks: dict[str, int]
    weapons: tuple[Weapon, ...]
    languages: str
    combat_notes: str
    spell_notes: str
    school: str
    gear: tuple[str, ...]
    feats: tuple[tuple[str, str], ...]
    specials: tuple[str, ...]
    gp: int
    load: tuple[int, int, int, int, int, int]
    spells: dict[int, tuple[str, ...]]
    spell_table: dict[int, tuple[str, str, str, str]]
    expend: dict[int, int] = field(default_factory=dict)
    expect: dict[str, int] = field(default_factory=dict)


def combat_of(character: Character) -> dict[str, int]:
    """Derive the combat block from abilities. Armor is not worn.

    :param character: pregenerated gnome
    :return: named totals
    """
    modifier = mods(character.scores)
    dexterity = modifier["zre"]
    strength = modifier["sil"]
    constitution = modifier["bud"]
    wisdom = modifier["mdr"]
    bab = 1
    size_ac = 1
    size_cmb = -1
    return {
        "kp": 10 + dexterity + size_ac + character.natural,
        "dotyk": 10 + dexterity + size_ac,
        "nieprzyg": 10 + size_ac + character.natural,
        "inicjatywa": dexterity + character.init_misc,
        "wytr": 1 + constitution,
        "ref": 1 + dexterity,
        "wola": 3 + wisdom,
        "pmb": bab + strength + size_cmb,
        "omb": 10 + bab + strength + dexterity + size_cmb,
        "bpa": bab,
        "sil": strength,
        "zre": dexterity,
        "bud": constitution,
        "mdr": wisdom,
        "pancerz": 0,
        "tarcza": 0,
        "rozmiar": size_ac,
        "naturalny": character.natural,
        "odbicie": 0,
        "inne": 0,
        "rozmiar_pmb": size_cmb,
    }


def skill_rows(character: Character) -> list[dict[str, str | int | bool | None]]:
    """Fill every skill row, including untrained totals.

    :param character: pregenerated gnome
    :return: rows in sheet order
    """
    modifier = mods(character.scores)
    rows: list[dict[str, str | int | bool | None]] = []
    for key, label, ability, trained_only in SKILLS:
        entry = character.training.get(key)
        ranks = entry.ranks if entry else 0
        if entry:
            misc = entry.misc
            if entry.label:
                label = f"{label} ({entry.label})"
        else:
            misc = GNOME_MISC.get(key, 0)
        class_skill = key in character.class_skills
        class_bonus = 3 if class_skill and ranks > 0 else 0
        shown_misc = misc + class_bonus
        if trained_only and ranks == 0:
            total: int | None = None
        else:
            total = modifier[ability] + ranks + shown_misc
        rows.append(
            {
                "key": key,
                "label": label,
                "ability": ability,
                "ability_mod": modifier[ability],
                "trained_only": trained_only,
                "class_skill": class_skill,
                "ranks": ranks,
                "misc": shown_misc,
                "total": total,
            }
        )
    return rows


def verify(character: Character) -> None:
    """Raise when a derived total disagrees with the written sheet.

    :param character: pregenerated gnome
    """
    combat = combat_of(character)
    for key, expected in character.expect.items():
        if combat[key] != expected:
            raise RuntimeError(f"{character.slug} {key}: {combat[key]} != {expected}")
    rows = {str(row["key"]): row for row in skill_rows(character)}
    spent = 0
    for row in rows.values():
        spent += int(row["ranks"])
        total = row["total"]
        if total is None:
            continue
        ability = int(row["ability_mod"])
        ranks = int(row["ranks"])
        misc = int(row["misc"])
        if int(total) != ability + ranks + misc:
            raise RuntimeError(f"{character.slug} {row['key']} does not add up")
    if spent != character.ranks_total:
        raise RuntimeError(f"{character.slug} ranks {spent} != {character.ranks_total}")
    for key, expected in character.skill_checks.items():
        total = rows[key]["total"]
        if total != expected:
            raise RuntimeError(f"{character.slug} {key}: {total} != {expected}")


def verify_all() -> None:
    """Check every pregenerated sheet."""
    for character in CHARACTERS:
        verify(character)


PIP = Character(
    slug="pip-iskra-torren",
    name="Pip „Iskra” Torren",
    quote="Nie jem niczego, co może samo zeskoczyć z talerza.",
    alignment="chaotyczny dobry",
    class_line="czarodziej 3 (wywoływanie)",
    deity="Nethys",
    homeland="akademia, dyżur nocny",
    race="gnom",
    gender="mężczyzna",
    age="52",
    hair="indygo",
    scores={"sil": 8, "zre": 14, "bud": 13, "inte": 17, "mdr": 10, "cha": 13},
    hp=17,
    init_misc=4,
    natural=0,
    ranks_total=18,
    class_skills=wizard_skills("unieszkodliwianie"),
    training={
        "wiedza-inzynieria": Training(3, 2),
        "wiedza-magia": Training(3, 0),
        "czaroznawstwo": Training(3, 0),
        "unieszkodliwianie": Training(3, 1),
        "percepcja": Training(3, 2),
        "wiedza-lokalna": Training(1, 0),
        "rzemioslo1": Training(1, 0, "alchemia"),
        "plywanie": Training(1, 0),
    },
    skill_checks={
        "wiedza-inzynieria": 11,
        "wiedza-magia": 9,
        "czaroznawstwo": 9,
        "unieszkodliwianie": 9,
        "percepcja": 5,
        "wiedza-lokalna": 7,
        "rzemioslo1": 7,
        "plywanie": 0,
        "akrobatyka": 2,
        "skradanie": 6,
    },
    weapons=(
        Weapon("Sztylet, wręcz", "+1", "19–20/×2", "kłuto-cięta", "—", "—", "1k3−1"),
        Weapon("Sztylet, rzucony", "+4", "19–20/×2", "kłuto-cięta", "10 stóp", "—", "1k3−1"),
        Weapon("Promień mrozu", "+4 dotyk", "—", "zimno", "bliski", "bez limitu", "1k3+1"),
        Weapon("Palący promień", "+4 dotyk", "—", "ogień", "bliski", "miejsce 2", "4k6+1"),
        Weapon("Pocisk mocy", "zawsze", "—", "moc", "średni", "6/dzień", "1k4+1"),
    ),
    languages="wspólny, gnomi, sylwański, smoczy, krasnoludzki, goblinski",
    combat_notes=(
        "+2 do rzutów przeciw iluzjom. +4 z uniku do KP przeciw olbrzymom. "
        "+1 do ataków przeciw gadzim humanoidom i goblinoidom. Koncentracja +8."
    ),
    spell_notes=(
        "ST 13 + krąg. Wywoływanie +1. Iluzje z gnomiej magii +1. "
        "Wzmożone czary: +1 obrażeń raz na czar wywoływania, nie na każdy pocisk. "
        "Szkoły przeciwne: zauroczanie i nekromancja."
    ),
    school=(
        "Wywoływanie (wzmożone czary, pocisk mocy). "
        "Więź: amulet w kształcie klucza imbusowego. "
        "Przygotowane sztuczki rzuca się bez limitu. Wolne miejsce 2. kręgu: 15 minut nauki z księgi."
    ),
    gear=(
        "sztylet",
        "strój uczonego, gogle",
        "amulet-klucz (przedmiot więzi)",
        "różdżka Magicznego pocisku, poziom rzucającego 1, 10 ładunków",
        "rękawice izolacyjne",
        "notes „Incydent z Żabą, wersja 3”",
        "księga czarów, sakiewka na komponenty",
    ),
    feats=(
        ("Spisanie zwoju", "tworzenie zwojów"),
        ("Skupienie na czarach (wywoływanie)", "+1 do ST czarów wywoływania"),
        ("Ulepszona inicjatywa", "+4 do inicjatywy"),
    ),
    specials=(
        "Pocisk mocy ☐☐☐☐☐☐ — 1k4+1 od mocy, trafia sam, zasięg średni.",
        "Czar z więzi ☐ — dowolny czar z księgi, bez przygotowania.",
        "Gnomia magia, po jednym: ☐ tańczące światła ☐ upiorny dźwięk ☐ prestidigitatorstwo ☐ rozmowa ze zwierzętami.",
        "Różdżka Magicznego pocisku ☐☐☐☐☐ ☐☐☐☐☐ — jeden pocisk, 1k4+1.",
        "Widzenie w słabym świetle. Broń z „gnomią” w nazwie jest dla niego żołnierska.",
        "Cechy wliczone w testy: Skupiony umysł, Dyżurny techniczny, Akademik (inżynieria).",
    ),
    gp=35,
    load=(19, 39, 60, 60, 120, 300),
    spells={
        0: (
            "Tańczące światła — do 4 świateł, 1 min, zasięg średni",
            "Wykrycie magii — aury w stożku 60 stóp, koncentracja",
            "Promień mrozu — 1k3+1 od zimna, dotyk +4, zasięg bliski",
            "Prestidigitatorstwo — drobne sztuczki, 1 godz.",
        ),
        1: (
            "Magiczny pocisk — 2 × (1k4+1) od mocy, zawsze trafia, zasięg średni",
            "Magiczny pocisk — jak wyżej",
            "Smar — śliska powierzchnia albo przedmiot, Refleks ST 14, 3 min",
            "Powiększenie osoby — +2 SIŁ i −2 ZRĘ, Wytrwałość ST 14, 3 min; rzucanie: 1 runda",
        ),
        2: (
            "Palący promień — 4k6+1 od ognia, dotyk +4, zasięg bliski",
            "Lśniący pył — oślepia i ujawnia niewidzialnych, Wola ST 15, 3 rundy",
            "Wolne miejsce — można je wypełnić w 15 minut nauki z księgi",
        ),
    },
    spell_table={
        0: ("księga", "13", "4", "—"),
        1: ("księga", "14", "4", "+2"),
        2: ("księga", "15", "3", "+2"),
    },
    expend={1: 4, 2: 3},
    expect={
        "kp": 13,
        "dotyk": 13,
        "nieprzyg": 11,
        "inicjatywa": 6,
        "wytr": 2,
        "ref": 3,
        "wola": 3,
        "pmb": -1,
        "omb": 11,
    },
)

LUMA = Character(
    slug="luma-bramblewick",
    name="Luma Bramblewick",
    quote="Nie ma awarii, której nie skleję. Są tylko takie, które jeszcze o tym nie wiedzą.",
    alignment="neutralna dobra",
    class_line="czarodziejka 3 (przemiany)",
    deity="Brigh",
    homeland="kotłownia akademii",
    race="gnomka",
    gender="kobieta",
    age="48",
    hair="",
    scores={"sil": 10, "zre": 13, "bud": 12, "inte": 18, "mdr": 10, "cha": 11},
    hp=17,
    init_misc=0,
    natural=0,
    ranks_total=21,
    class_skills=wizard_skills("unieszkodliwianie"),
    training={
        "rzemioslo1": Training(3, 4, "mechanizmy"),
        "unieszkodliwianie": Training(3, 5),
        "wiedza-inzynieria": Training(3, 1),
        "czaroznawstwo": Training(3, 0),
        "wiedza-magia": Training(2, 0),
        "percepcja": Training(3, 2),
        "dyplomacja": Training(3, 0),
        "plywanie": Training(1, 0),
    },
    skill_checks={
        "rzemioslo1": 14,
        "unieszkodliwianie": 12,
        "wiedza-inzynieria": 11,
        "czaroznawstwo": 10,
        "wiedza-magia": 9,
        "percepcja": 5,
        "dyplomacja": 3,
        "plywanie": 1,
        "skradanie": 5,
    },
    weapons=(
        Weapon("Mistrzowski klucz francuski, jak pałka", "+3", "×2", "obuchowe", "—", "—", "1k4"),
        Weapon("Telekinetyczna pięść", "+3 dotyk", "—", "obuchowe", "30 stóp", "7/dzień", "1k4+1"),
    ),
    languages="wspólny, gnomi, sylwański, smoczy, krasnoludzki, goblinski, elfi",
    combat_notes=(
        "+2 do rzutów przeciw iluzjom. +4 z uniku do KP przeciw olbrzymom. "
        "+1 do ataków przeciw gadzim humanoidom i goblinoidom. "
        "Koncentracja +9, przy rzucaniu defensywnym +13."
    ),
    spell_notes=(
        "ST 14 + krąg. Szkoły przeciwne: zauroczanie i iluzja. "
        "Naprawę i Scalenie rzucone na instalacje akademii rzuca w 1 rundę zamiast w 10 minut."
    ),
    school=(
        "Przemiany (wzmocnienie fizyczne: +1 do Zręczności, już wliczone; telekinetyczna pięść). "
        "Więź: mistrzowski klucz francuski, w walce jak pałka. "
        "Dodatkowe miejsce ze szkoły jest czarem przemian."
    ),
    gear=(
        "mistrzowski klucz francuski (przedmiot więzi)",
        "mistrzowskie narzędzia rzemieślnicze (+2 do Rzemiosła)",
        "mistrzowskie narzędzia złodziejskie (+2 do Unieszkodliwiania mechanizmów)",
        "taśma Gnomoklej, śrubki",
        "kanapka należna dla Splotu",
        "kanapka odsetkowa (żaba narysowana kredą)",
        "księga czarów, sakiewka na komponenty",
    ),
    feats=(
        ("Spisanie zwoju", "tworzenie zwojów"),
        ("Skupienie na umiejętności (Unieszkodliwianie mechanizmów)", "+3 do tej umiejętności"),
        ("Rzucanie w walce", "+4 do koncentracji przy rzucaniu defensywnym i w zwarciu"),
    ),
    specials=(
        "Telekinetyczna pięść ☐☐☐☐☐☐☐ — dystansowy atak dotykowy, 1k4+1 obuchowe, 30 stóp.",
        "Czar z więzi ☐ — dowolny czar z księgi, bez przygotowania.",
        "Gnomia magia, po jednym: ☐ tańczące światła ☐ upiorny dźwięk ☐ prestidigitatorstwo ☐ rozmowa ze zwierzętami.",
        "Naprawa i Scalenie na przewodach, rurach i panelach akademii: czas rzucania 1 runda.",
        "Widzenie w słabym świetle. Broń z „gnomią” w nazwie jest dla niej żołnierska.",
        "Cechy wliczone w testy: Skupiony umysł, Uczennica kotłowni, Obsesja (mechanizmy).",
    ),
    gp=28,
    load=(24, 49, 75, 75, 150, 375),
    spells={
        0: (
            "Naprawa — łata drobne uszkodzenie (1k4 PW przedmiotu)",
            "Dłoń maga — przesuwa przedmiot do 5 funtów, koncentracja",
            "Otwarcie/zamknięcie — drzwi, szafka albo zawór",
            "Światło — przedmiot świeci jak pochodnia, 30 min",
        ),
        1: (
            "Ożywienie liny (szkoła) — lina do 65 stóp oplata i krępuje, 3 rundy",
            "Szybki odwrót — +30 stóp prędkości, 3 min",
            "Piórkospad — akcja natychmiastowa, łagodne opadanie, 3 rundy",
            "Niewidzialny sługa — niewidzialny pomocnik, 3 godz.",
        ),
        2: (
            "Lewitacja (szkoła) — 20 stóp na rundę, do 300 funtów, 3 min",
            "Scalenie — naprawia poważnie uszkodzony przedmiot",
            "Byczy wigor — +4 do Siły celu, 3 min",
        ),
    },
    spell_table={
        0: ("księga", "14", "4", "—"),
        1: ("księga", "15", "4", "+2"),
        2: ("księga", "16", "3", "+2"),
    },
    expend={1: 4, 2: 3},
    expect={
        "kp": 12,
        "dotyk": 12,
        "nieprzyg": 11,
        "inicjatywa": 1,
        "wytr": 2,
        "ref": 2,
        "wola": 3,
        "pmb": 0,
        "omb": 11,
    },
)

ZIZZLE = Character(
    slug="zizzle-stormpocket",
    name="Zizzle Stormpocket",
    quote="Mam plan. Mam też kanapkę. Kanapka jest lepiej przemyślana.",
    alignment="chaotyczny neutralny",
    class_line="zaklinacz 3 (baśniowa linia krwi)",
    deity="Calistria",
    homeland="las, wymiana",
    race="gnom",
    gender="mężczyzna",
    age="",
    hair="",
    scores={"sil": 8, "zre": 14, "bud": 14, "inte": 10, "mdr": 10, "cha": 19},
    hp=20,
    init_misc=4,
    natural=0,
    ranks_total=9,
    class_skills=sorcerer_skills("dyplomacja"),
    training={
        "dyplomacja": Training(3, 1),
        "blefowanie": Training(3, 0),
        "ump": Training(3, 0),
        "przebieranie": Training(0, 2),
        "zastraszanie": Training(0, 1),
    },
    skill_checks={
        "dyplomacja": 11,
        "blefowanie": 10,
        "ump": 10,
        "przebieranie": 6,
        "skradanie": 6,
        "zastraszanie": 5,
        "percepcja": 2,
    },
    weapons=(
        Weapon("Sztylet", "+1", "19–20/×2", "kłuto-cięta", "—", "—", "1k3−1"),
        Weapon("Promień mrozu", "+4 dotyk", "—", "zimno", "bliski", "bez limitu", "1k3"),
        Weapon("Śmiejący dotyk", "+1 dotyk", "—", "wręcz", "—", "7/dzień", "tylko ruch, 1 runda"),
    ),
    languages="wspólny, gnomi, sylwański",
    combat_notes=(
        "+2 do rzutów przeciw iluzjom. +4 z uniku do KP przeciw olbrzymom. "
        "+1 do ataków przeciw gadzim humanoidom i goblinoidom. Koncentracja +7. "
        "Czarujący: +1 do Blefowania i Dyplomacji oraz +1 do ST czarów zależnych od języka wobec istot, które mogłyby uznać go za atrakcyjnego."
    ),
    spell_notes=(
        "ST 14 + krąg. Zauroczanie +1. Iluzje +1. Przymus +2. "
        "Pominięcie komponentów: tanie komponenty materiałowe są niepotrzebne. "
        "Miejsca 1. kręgu wydajesz z puli, nie z konkretnego czaru. "
        "Na 4. poziomie naturalny czar 2. kręgu to Okropny śmiech (ST 19 dzięki arkanum i skupieniu na czarach)."
    ),
    school=(
        "Baśniowa linia krwi. Arkanum: +2 do ST czarów z podszkoły przymusu. "
        "Śmiejący dotyk 7 razy dziennie. Leśny krok: niemagiczne zarośla nie spowalniają ruchu. "
        "Splątanie jest czarem linii krwi."
    ),
    gear=(
        "sztylet",
        "zestaw do malowania piegów, kreda do brody",
        "list „legalny gnom”: pieczątka „NIE MOJA WINA”, na kartce nie ma poprawek. Odpis Orrina ma czternaście poprawek i dopisek „Formalnie bez zarzutu. Broda do weryfikacji”",
        "różdżka Leczenia lekkich ran, 5 ładunków, pęknięta",
        "zestaw do przebieranek, cukierki",
    ),
    feats=(
        ("Pominięcie komponentów", "bez tanich komponentów materiałowych"),
        ("Skupienie na czarach (zauroczanie)", "+1 do ST czarów zauroczania"),
        ("Ulepszona inicjatywa", "+4 do inicjatywy"),
    ),
    specials=(
        "Śmiejący dotyk ☐☐☐☐☐☐☐ — dotyk wręcz; przez rundę cel wykonuje tylko akcje ruchu.",
        "Leśny krok — niemagiczne zarośla nie spowalniają ruchu.",
        "Różdżka Leczenia lekkich ran ☐☐☐☐☐ — 1k8+1, różdżka pęknięta. Czar nie jest zaklinaczowi znany: Używanie magicznych przedmiotów ST 20.",
        "Gnomia magia, po jednym: ☐ tańczące światła ☐ upiorny dźwięk ☐ prestidigitatorstwo ☐ rozmowa ze zwierzętami.",
        "Widzenie w słabym świetle. Broń z „gnomią” w nazwie jest dla niego żołnierska.",
        "Cechy wliczone w testy: Przekonujący. Czarujący: +1 do Blefowania, Dyplomacji i ST czarów zależnych od języka wobec istot, które mogłyby uznać go za atrakcyjnego.",
    ),
    gp=40,
    load=(19, 39, 60, 60, 120, 300),
    spells={
        0: (
            "Wykrycie magii — aury w stożku 60 stóp, koncentracja",
            "Upiorny dźwięk — iluzoryczne dźwięki, Wola (nie uwierzyć), 3 rundy",
            "Wiadomość — szeptana rozmowa, 30 min",
            "Prestidigitatorstwo — drobne sztuczki, 1 godz.",
            "Promień mrozu — 1k3 od zimna, dotyk +4, zasięg bliski",
        ),
        1: (
            "Zauroczenie osoby — humanoid uznaje go za przyjaciela, Wola ST 16, 3 godz.",
            "Barwny strumień — stożek 15 stóp, Wola ST 16",
            "Zniknięcie — niewidzialność, kończy się po ataku, do 3 rund",
            "Splątanie (linia krwi) — rośliny na promieniu 40 stóp, Refleks ST 15, 3 min",
        ),
    },
    spell_table={
        0: ("5", "14", "∞", "—"),
        1: ("4", "15", "6", "+1"),
    },
    expend={1: 6},
    expect={
        "kp": 13,
        "dotyk": 13,
        "nieprzyg": 11,
        "inicjatywa": 6,
        "wytr": 3,
        "ref": 3,
        "wola": 3,
        "pmb": -1,
        "omb": 11,
    },
)

ORRIN = Character(
    slug="orrin-quill",
    name="Orrin Quill",
    quote="Według trzech źródeł to dobry pomysł. Według czwartego zginiemy. Czwarte jest przypisem.",
    alignment="praworządny neutralny",
    class_line="czarodziej 3 (poznanie)",
    deity="Irori",
    homeland="archiwum akademii",
    race="gnom",
    gender="mężczyzna",
    age="",
    hair="",
    scores={"sil": 8, "zre": 12, "bud": 12, "inte": 18, "mdr": 13, "cha": 10},
    hp=17,
    init_misc=5,
    natural=0,
    ranks_total=21,
    class_skills=wizard_skills("percepcja"),
    training={
        "wiedza-historia": Training(3, 2),
        "wiedza-magia": Training(3, 0),
        "wiedza-inzynieria": Training(3, 0),
        "wiedza-plany": Training(3, 0),
        "czaroznawstwo": Training(3, 0),
        "lingwistyka": Training(3, 0),
        "percepcja": Training(3, 3),
    },
    skill_checks={
        "wiedza-historia": 12,
        "wiedza-magia": 10,
        "wiedza-inzynieria": 10,
        "wiedza-plany": 10,
        "czaroznawstwo": 10,
        "lingwistyka": 10,
        "percepcja": 10,
        "skradanie": 5,
    },
    weapons=(
        Weapon("Lekka kusza", "+3", "19–20/×2", "kłute", "80 stóp", "10 bełtów", "1k6"),
        Weapon("Sztylet", "+1", "19–20/×2", "kłuto-cięta", "—", "—", "1k3−1"),
    ),
    languages="wspólny, gnomi, sylwański, smoczy, krasnoludzki, elfi, olbrzymi, akwan, niebiański, piekielny",
    combat_notes=(
        "+2 do rzutów przeciw iluzjom. +4 z uniku do KP przeciw olbrzymom. "
        "+1 do ataków przeciw gadzim humanoidom i goblinoidom. "
        "Koncentracja +9. Zawsze działa w rundzie zaskoczenia. Tarcza (czar): KP 16."
    ),
    spell_notes=(
        "ST 14 + krąg. Poznanie +1. Dodatkowe miejsce ze szkoły musi zawierać czar poznania: "
        "na 1. kręgu Identyfikacja, na 2. Zlokalizowanie przedmiotu. "
        "Szkoły przeciwne: wywoływanie i nekromancja."
    ),
    school=(
        "Poznanie (przezorność, szczęście wieszcza). "
        "Więź: amulet z kryształową soczewką. "
        "Charyzma 10: nie korzysta ze zdolności czaropodobnych gnomiej magii."
    ),
    gear=(
        "lekka kusza, 10 bełtów",
        "sztylet",
        "amulet z kryształową soczewką (przedmiot więzi)",
        "kopia schematu bariery",
        "kreda, lupa, czerwony atrament",
        "księga czarów, sakiewka na komponenty",
    ),
    feats=(
        ("Spisanie zwoju", "tworzenie zwojów"),
        ("Ulepszona inicjatywa", "+4 do inicjatywy"),
        ("Skupienie na czarach (poznanie)", "+1 do ST czarów poznania"),
    ),
    specials=(
        "Szczęście wieszcza ☐☐☐☐☐☐☐ — dotyk: +1 z wnikliwości do ataków, testów umiejętności, testów atrybutów i rzutów obronnych przez rundę.",
        "Przezorność — +1 do inicjatywy (wliczone). Zawsze działa w rundzie zaskoczenia.",
        "Czar z więzi ☐ — dowolny czar z księgi, bez przygotowania.",
        "Widzenie w słabym świetle. Broń z „gnomią” w nazwie jest dla niego żołnierska.",
        "Cechy wliczone w testy: Poszukiwacz, Skupiony umysł, Akademik (historia).",
    ),
    gp=32,
    load=(19, 39, 60, 60, 120, 300),
    spells={
        0: (
            "Wykrycie magii — aury w stożku 60 stóp, koncentracja",
            "Odczytanie magii — zwoje i magiczne napisy, 30 min",
            "Wykrycie trucizny — czy coś jest zatrute",
            "Dłoń maga — przesuwa przedmiot do 5 funtów, koncentracja",
        ),
        1: (
            "Zrozumienie języków — rozumie mowę i pismo, 30 min",
            "Identyfikacja (szkoła) — +10 do Czaroznawstwa przy przedmiotach, 9 rund",
            "Tarcza — +4 do KP, blokuje Magiczny pocisk, 3 min",
            "Pewny cios — +20 do następnego ataku, 1 runda",
        ),
        2: (
            "Wykrycie myśli — powierzchowne myśli, Wola ST 17, koncentracja",
            "Widzenie niewidzialnego — 30 min",
            "Zlokalizowanie przedmiotu (szkoła) — kierunek do przedmiotu, zasięg daleki, 3 min",
        ),
    },
    spell_table={
        0: ("księga", "14", "4", "—"),
        1: ("księga", "15", "4", "+2"),
        2: ("księga", "16", "3", "+2"),
    },
    expend={1: 4, 2: 3},
    expect={
        "kp": 12,
        "dotyk": 12,
        "nieprzyg": 11,
        "inicjatywa": 6,
        "wytr": 2,
        "ref": 2,
        "wola": 4,
        "pmb": -1,
        "omb": 10,
    },
)

NIXA = Character(
    slug="nixa-embercoil",
    name="Nixa Embercoil",
    quote="Najpierw rozmawiamy. Potem rozmawiamy głośniej. Potem rozmawiamy ogniem.",
    alignment="neutralna dobra",
    class_line="zaklinaczka 3 (smocza linia krwi, mosiądz)",
    deity="Apsu",
    homeland="akademia",
    race="gnomka",
    gender="kobieta",
    age="",
    hair="",
    scores={"sil": 10, "zre": 13, "bud": 14, "inte": 10, "mdr": 10, "cha": 19},
    hp=20,
    init_misc=2,
    natural=1,
    ranks_total=9,
    class_skills=sorcerer_skills("percepcja", "plywanie"),
    training={
        "zastraszanie": Training(3, 0),
        "ump": Training(1, 0),
        "percepcja": Training(2, 2),
        "plywanie": Training(1, 1),
        "wiedza-magia": Training(1, 0),
        "czaroznawstwo": Training(1, 0),
    },
    skill_checks={
        "zastraszanie": 10,
        "ump": 8,
        "percepcja": 7,
        "plywanie": 5,
        "wiedza-magia": 4,
        "czaroznawstwo": 4,
        "skradanie": 5,
        "blefowanie": 4,
    },
    weapons=(
        Weapon("2 pazury", "+2", "×2", "cięte", "—", "7 rund", "1k3 każdy"),
        Weapon("Sztylet", "+2", "19–20/×2", "kłuto-cięta", "—", "—", "1k3+1"),
        Weapon("Bryzg kwasu", "+3 dotyk", "—", "kwas", "bliski", "bez limitu", "1k3"),
        Weapon("Płonące dłonie", "—", "—", "ogień", "stożek 15 stóp", "miejsce 1", "3k4+3"),
        Weapon("Magiczny pocisk", "zawsze", "—", "moc", "średni", "miejsce 1", "2 × (1k4+1)"),
    ),
    languages="wspólny, gnomi, sylwański",
    combat_notes=(
        "+2 do rzutów przeciw iluzjom. +4 z uniku do KP przeciw olbrzymom. "
        "+1 do ataków przeciw gadzim humanoidom i goblinoidom. "
        "Koncentracja +7, przy rzucaniu defensywnym +11. Odporność na ogień 5. "
        "Zbroja maga: KP 17."
    ),
    spell_notes=(
        "ST 14 + krąg. Wywoływanie +1. Ogień: +1 obrażeń na każdą kość (wliczone przy Płonących dłoniach). "
        "Pominięcie komponentów. Miejsca 1. kręgu wydajesz z puli. "
        "Płonące dłonie: Refleks ST 16 połowę. "
        "Na 4. poziomie naturalny czar 2. kręgu to Palący promień (4k6+4 od ognia dzięki arkanum)."
    ),
    school=(
        "Smocza linia krwi, mosiężny smok, ogień. Pazury, odporność na ogień 5, "
        "+1 naturalnego pancerza (wliczone w KP). Zbroja maga jest czarem linii krwi."
    ),
    gear=(
        "sztylet",
        "peleryna „niepalna w 60%” (pamiątka, bez magii; reszta to taśma)",
        "amulet z zębem (nazywa go „na pewno smoczym”; Percepcja ST 15: to ząb psa)",
        "nieotwarty list od kuzyna",
        "sakiewka na komponenty",
    ),
    feats=(
        ("Pominięcie komponentów", "bez tanich komponentów materiałowych"),
        ("Skupienie na czarach (wywoływanie)", "+1 do ST czarów wywoływania"),
        ("Rzucanie w walce", "+4 do koncentracji przy rzucaniu defensywnym i w zwarciu"),
    ),
    specials=(
        "Pazury ☐☐☐☐☐☐☐ rund — dwa ataki wręcz +2, obrażenia 1k3 każde.",
        "Odporność na ogień 5. Naturalny pancerz +1 jest wliczony w KP.",
        "Gnomia magia, po jednym: ☐ tańczące światła ☐ upiorny dźwięk ☐ prestidigitatorstwo ☐ rozmowa ze zwierzętami.",
        "Widzenie w słabym świetle. Broń z „gnomią” w nazwie jest dla niej żołnierska.",
        "Cechy wliczone w testy: Szybka reakcja, Szczur rzeczny.",
    ),
    gp=45,
    load=(24, 49, 75, 75, 150, 375),
    spells={
        0: (
            "Bryzg kwasu — 1k3 od kwasu, dotyk +3, zasięg bliski",
            "Wykrycie magii — aury w stożku 60 stóp, koncentracja",
            "Rozbłysk — oślepienie na 1 rundę, Wytrwałość ST 15",
            "Dłoń maga — przesuwa przedmiot do 5 funtów, koncentracja",
            "Iskra — podpala łatwopalny przedmiot",
        ),
        1: (
            "Płonące dłonie — 3k4+3 od ognia, stożek 15 stóp, Refleks ST 16 połowę",
            "Magiczny pocisk — 2 × (1k4+1) od mocy, zawsze trafia, zasięg średni",
            "Tarcza — +4 do KP, blokuje Magiczny pocisk, 3 min",
            "Zbroja maga (linia krwi) — +4 z pancerza do KP, 3 godz.",
        ),
    },
    spell_table={
        0: ("5", "14", "∞", "—"),
        1: ("4", "15", "6", "+1"),
    },
    expend={1: 6},
    expect={
        "kp": 13,
        "dotyk": 12,
        "nieprzyg": 12,
        "inicjatywa": 3,
        "wytr": 3,
        "ref": 2,
        "wola": 3,
        "pmb": 0,
        "omb": 11,
    },
)

CHARACTERS: tuple[Character, ...] = (PIP, LUMA, ZIZZLE, ORRIN, NIXA)


STYLESHEET = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: "Liberation Sans", "DejaVu Sans", "Nimbus Sans", Arial, sans-serif; color: #141414; }
.sheet {
  width: 210mm;
  height: 296.6mm;
  padding: 4.5mm 5mm 4mm;
  display: flex;
  background: #fff;
  break-after: page;
  overflow: hidden;
}
.sheet:last-child { break-after: auto; }
.frame {
  flex: 1;
  min-height: 0;
  border: 1.15pt solid #141414;
  padding: 1.6mm 1.8mm 1.1mm;
  display: flex;
  flex-direction: column;
}
.banner, .aname, .tag, .touch, .flat, .save b, .vitals .label, .mini span, .flbl, .skills th, .legend, footer, .coin span, .load span, .eq small, .cell small, .spline .lv {
  font-family: "Liberation Sans", "DejaVu Sans", Arial, sans-serif;
}
.banner {
  background: #141414;
  color: #fff;
  font-size: 7.2pt;
  font-weight: 700;
  letter-spacing: 0.045em;
  text-transform: uppercase;
  line-height: 1.15;
  padding: 0.45mm 1.4mm;
}
.head { display: flex; gap: 2mm; align-items: stretch; }
.emblem {
  width: 32mm;
  border: 1.3pt solid #141414;
  padding: 0.8mm 1.2mm 1mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.emblem .g { font-weight: 800; font-size: 10.5pt; letter-spacing: 0.01em; line-height: 1; }
.emblem .e { font-size: 6.4pt; letter-spacing: 0.14em; text-transform: uppercase; margin-top: 0.3mm; }
.emblem .k { margin-top: 0.9mm; padding-top: 0.6mm; border-top: 0.8pt solid #141414; font-size: 7.4pt; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }
.identity { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.45mm; }
.id1, .id2, .id3 { display: grid; gap: 0.35mm 1.4mm; }
.id1 { grid-template-columns: 1.55fr 1.05fr 0.85fr; }
.id2 { grid-template-columns: 1.45fr 0.85fr 1.15fr; }
.id3 { grid-template-columns: 0.9fr 0.7fr 0.95fr 0.55fr 0.7fr 0.7fr 0.85fr 0.7fr; }
.fval { border-bottom: 0.75pt solid #141414; min-height: 3.8mm; font-size: 7.6pt; font-weight: 700; line-height: 1.15; padding: 0 0.4mm; }
.flbl { font-size: 5pt; letter-spacing: 0.03em; text-transform: uppercase; line-height: 1.15; }
.quote { margin: 0.55mm 0 0.7mm; font-size: 7.4pt; font-style: italic; line-height: 1.2; }
.cols { flex: 1; min-height: 0; display: grid; grid-template-columns: 1.18fr 0.92fr; gap: 1.6mm; }
.left, .right { min-width: 0; min-height: 0; display: flex; flex-direction: column; }
.top { display: grid; grid-template-columns: 46mm 1fr; gap: 1.1mm; }
.abilities { width: 100%; border-collapse: collapse; }
.abilities th, .abilities td { border: 0.7pt solid #141414; text-align: center; }
.aname { background: #141414; color: #fff; text-align: left; padding: 0 0.7mm; width: 15mm; }
.aname b { display: block; font-size: 7.4pt; letter-spacing: 0.04em; line-height: 1; }
.aname span { display: block; font-size: 4.7pt; font-weight: 500; letter-spacing: 0.02em; text-transform: uppercase; opacity: 0.9; }
.abilities thead th { font-size: 4.6pt; font-weight: 700; letter-spacing: 0.02em; text-transform: uppercase; padding: 0; border-color: transparent; }
.abilities tbody td { font-size: 8pt; font-weight: 700; height: 5.15mm; width: 7.2mm; }
.vitals { display: grid; grid-template-columns: 1.05fr 0.95fr; grid-template-rows: 1fr auto; gap: 0.8mm; }
.panel { border: 0.75pt solid #141414; min-width: 0; }
.panel .label { background: #141414; color: #fff; font-size: 6.4pt; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; padding: 0.2mm 0.8mm; }
.hp { grid-row: 1 / span 2; padding-bottom: 0.6mm; }
.hp-row, .init-row, .speed-grid { display: flex; align-items: stretch; }
.hp-total, .statbox { border-left: 0.7pt solid #141414; text-align: center; }
.hp-total { margin-left: auto; min-width: 12mm; }
.hp-total b, .statbox b, .mini b { display: block; font-size: 11pt; line-height: 1; }
.hp-total span, .statbox span, .mini span, .cell small, .eq small { display: block; font-size: 4.6pt; letter-spacing: 0.03em; text-transform: uppercase; font-weight: 700; }
.wounds { margin: 0.6mm; border: 0.7pt solid #141414; min-height: 16mm; padding: 0.4mm 0.6mm; }
.wounds .cap { font-size: 4.7pt; letter-spacing: 0.04em; text-transform: uppercase; }
.ticks { line-height: 0; margin-top: 0.5mm; }
.sq { display: inline-block; width: 2.35mm; height: 2.35mm; border: 0.65pt solid #141414; margin: 0 0.22mm 0.35mm 0; vertical-align: middle; }
.gap { display: inline-block; width: 0.9mm; }
.subline { display: flex; justify-content: space-between; gap: 1mm; margin: 0.5mm 0.7mm 0; font-size: 6pt; }
.subline b { font-size: 8pt; }
.speed-grid { display: grid; grid-template-columns: 1fr 1fr; }
.speed-grid div { border-top: 0.6pt solid #141414; border-right: 0.6pt solid #141414; padding: 0.25mm 0.5mm 0.4mm; min-height: 5.4mm; }
.speed-grid div:nth-child(2n) { border-right: none; }
.speed-grid span { display: block; font-size: 4.5pt; text-transform: uppercase; letter-spacing: 0.03em; }
.speed-grid b { font-size: 7pt; }
.init-row { align-items: stretch; }
.init-row .statbox { flex: 1; border-left: none; border-top: 0.6pt solid #141414; padding: 0.3mm; }
.init-row .statbox + .statbox { border-left: 0.6pt solid #141414; }
.block { margin-top: 0.8mm; border: 0.75pt solid #141414; }
.equation { display: flex; align-items: stretch; }
.big { min-width: 9mm; text-align: center; font-size: 12pt; font-weight: 800; display: flex; align-items: center; justify-content: center; border-right: 0.7pt solid #141414; }
.eq { display: flex; align-items: center; padding: 0 0.5mm; font-size: 7pt; font-weight: 700; }
.cell { flex: 1; text-align: center; border-left: 0.6pt solid #141414; padding: 0.15mm 0.2mm 0.3mm; }
.cell b { font-size: 8pt; }
.ac-foot, .save, .maneuver { display: flex; align-items: stretch; border-top: 0.7pt solid #141414; }
.touch, .flat, .save b.name, .maneuver .name { background: #141414; color: #fff; font-size: 6.2pt; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; display: flex; align-items: center; padding: 0 1mm; }
.ac-foot .num, .save .num, .maneuver .num { min-width: 8mm; text-align: center; font-weight: 800; font-size: 10pt; display: flex; align-items: center; justify-content: center; border-left: 0.7pt solid #141414; }
.ac-foot .pair { display: flex; }
.formula { display: flex; flex: 1; }
.formula .cell { display: flex; flex-direction: column; justify-content: center; }
.save .name { width: 24mm; }
.save .tiny { font-size: 4.6pt; font-weight: 500; letter-spacing: 0; text-transform: none; display: block; }
.bab-row { display: flex; border-top: none; }
.bab-row .banner { flex: 1; }
.bab-row .num { min-width: 12mm; }
.sr { width: 28mm; border-left: 0.7pt solid #141414; text-align: center; }
.sr span { display: block; font-size: 4.6pt; text-transform: uppercase; letter-spacing: 0.03em; }
.sr b { font-size: 9pt; }
.maneuver .name { width: 16mm; justify-content: center; }
.maneuver .rest { margin-left: auto; display: flex; align-items: center; padding: 0 0.8mm; font-size: 8pt; font-weight: 700; }
.weapons { margin-top: 0.7mm; display: flex; flex-direction: column; gap: 0.55mm; }
.weapon { border: 0.75pt solid #141414; }
.weapon-top { display: grid; grid-template-columns: 1fr 24mm 27mm; }
.weapon-top .banner { display: flex; align-items: center; gap: 1.2mm; min-height: 5.2mm; }
.weapon-top .tag { font-weight: 600; opacity: 0.8; }
.mini { border-left: 0.7pt solid #141414; text-align: center; padding: 0.15mm 0.4mm; }
.mini b { font-size: 8pt; }
.weapon-bot { display: grid; grid-template-columns: 1.05fr 0.85fr 0.8fr 1.15fr; border-top: 0.65pt solid #141414; }
.weapon-bot div { padding: 0.15mm 0.6mm 0.35mm; min-height: 5.6mm; }
.weapon-bot div + div { border-left: 0.6pt solid #141414; }
.weapon-bot span { display: block; font-size: 4.5pt; text-transform: uppercase; letter-spacing: 0.03em; }
.weapon-bot b { font-size: 7pt; font-weight: 700; }
.skills { width: 100%; border-collapse: collapse; }
.skills th { font-size: 4.7pt; text-transform: uppercase; letter-spacing: 0.02em; font-weight: 700; text-align: center; padding: 0; }
.skills th.name { text-align: left; }
.skills td { height: 4.22mm; font-size: 6.15pt; border-bottom: 0.35pt solid #c8c8c8; padding: 0 0.35mm; vertical-align: middle; white-space: nowrap; }
.skills td.num { text-align: center; font-weight: 700; font-variant-numeric: tabular-nums; width: 7.5mm; }
.skills td.ab { text-align: center; width: 11mm; font-weight: 600; }
.skills td.name { font-weight: 650; }
.mark { display: inline-block; width: 2.05mm; height: 2.05mm; border: 0.6pt solid #141414; margin-right: 0.55mm; vertical-align: -0.3mm; }
.mark.on { background: #141414; }
.star { font-weight: 700; }
.legend { font-size: 5.4pt; margin: 0.4mm 0 0.6mm; }
.note { border: 0.75pt solid #141414; display: flex; flex-direction: column; min-height: 0; }
.note + .note { margin-top: 0.7mm; }
.note p { margin: 0.6mm 0.8mm; font-size: 6.5pt; line-height: 1.25; }
.note.grow { flex: 1; }
footer { display: flex; justify-content: space-between; font-size: 6pt; margin-top: 0.7mm; }
.page2 { flex: 1; min-height: 0; display: grid; grid-template-columns: 36% 31% 33%; gap: 1.5mm; }
.col { min-width: 0; min-height: 0; display: flex; flex-direction: column; gap: 1.1mm; }
.box { border: 0.75pt solid #141414; min-height: 0; display: flex; flex-direction: column; }
.grow { flex: 1; }
.p2head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 1mm; }
.p2head .who { font-size: 11pt; font-weight: 800; }
.p2head .what { font-size: 7pt; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700; }
table.grid { width: 100%; border-collapse: collapse; font-size: 6.2pt; }
table.grid th, table.grid td { border: 0.55pt solid #141414; padding: 0.2mm 0.45mm; text-align: center; font-weight: 650; }
table.grid th { font-size: 4.6pt; text-transform: uppercase; letter-spacing: 0.02em; background: #f3f3f3; }
table.grid td.item { text-align: left; font-weight: 600; }
.lined { position: relative; flex: 1; min-height: 0; }
.lines { position: absolute; inset: 0; background-image: repeating-linear-gradient(to bottom, transparent 0, transparent calc(4.7mm - 0.45pt), #222 calc(4.7mm - 0.45pt), #222 4.7mm); }
.items { position: relative; }
.line { min-height: 4.7mm; font-size: 6.7pt; line-height: 1.25; padding: 0.5mm 0.8mm; }
.plain { margin: 0.5mm 0.8mm 0.8mm; padding: 0; list-style: none; font-size: 6.7pt; line-height: 1.28; }
.plain li { margin: 0 0 0.35mm; }
.plain b { font-weight: 750; }
.load { display: grid; grid-template-columns: 1fr 1fr; gap: 0.4mm 1.4mm; padding: 0.7mm 0.8mm 0.8mm; font-size: 6.4pt; }
.load div { display: flex; justify-content: space-between; border-bottom: 0.6pt solid #141414; }
.load b { font-size: 8pt; }
.cap { font-size: 5pt; letter-spacing: 0.04em; text-transform: uppercase; padding: 0.4mm 0.8mm 0; }
.coins { display: grid; grid-template-columns: repeat(4, 1fr); }
.coin { text-align: center; padding: 0.4mm 0 0.6mm; }
.coin + .coin { border-left: 0.6pt solid #141414; }
.coin b { display: block; font-size: 11pt; line-height: 1.05; }
.coin span { font-size: 5pt; text-transform: uppercase; letter-spacing: 0.04em; }
.xp { display: grid; grid-template-columns: 1.2fr 0.8fr; }
.xp div { padding: 0.4mm 0.8mm 0.6mm; }
.xp div + div { border-left: 0.7pt solid #141414; }
.xp span { display: block; font-size: 5pt; text-transform: uppercase; letter-spacing: 0.04em; }
.xp b { font-size: 11pt; }
.school { padding: 0.6mm 0.8mm; font-size: 6.5pt; line-height: 1.25; }
.spellhead td, .spellhead th { height: 3.7mm; }
.spells { padding: 0.4mm 0.6mm 0.6mm; overflow: hidden; }
.splevel { display: grid; grid-template-columns: 7.5mm 1fr; gap: 0.4mm; margin-bottom: 0.45mm; }
.splevel .lv { font-size: 8pt; font-weight: 800; }
.splevel .slots { line-height: 0; margin-top: 0.3mm; }
.spline { font-size: 6.35pt; line-height: 1.22; border-bottom: 0.4pt solid #bbb; min-height: 3.5mm; }
.spline.blank { min-height: 3.6mm; }
.higher { display: grid; grid-template-columns: repeat(7, 1fr); gap: 0.6mm; margin-top: 0.4mm; }
.higher div { border-bottom: 0.6pt solid #141414; font-size: 6.5pt; font-weight: 800; color: #444; }
.powrot { font-family: "Liberation Sans", "DejaVu Sans", Arial, sans-serif; font-size: 10pt; margin: 0; padding: 4mm 6mm 0; }
.powrot a { color: #6b3a1f; }
@media screen {
  html { background: #d9d3c8; }
  body { padding-bottom: 8mm; }
  .sheet { margin: 6mm auto; box-shadow: 0 8px 22px rgba(0, 0, 0, 0.18); }
}
@media print {
  .powrot { display: none !important; }
  .sheet { margin: 0; box-shadow: none; }
  .banner, .aname, .touch, .flat, .save b.name, .maneuver .name, .mark.on, .panel .label, table.grid th {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
"""


def squares(count: int) -> str:
    """Render empty checkbox squares.

    :param count: how many squares
    :return: HTML
    """
    parts: list[str] = []
    for index in range(count):
        if index and index % 5 == 0:
            parts.append('<span class="gap"></span>')
        parts.append('<i class="sq"></i>')
    return "".join(parts)


def field_html(value: str, label: str) -> str:
    """One underlined identity field.

    :param value: filled value, possibly empty
    :param label: caption under the line
    :return: HTML
    """
    return f'<div class="field"><div class="fval">{escape(value)}</div><div class="flbl">{escape(label)}</div></div>'


def cell(value: str, caption: str) -> str:
    """A small equation cell.

    :param value: number already formatted
    :param caption: caption under the number
    :return: HTML
    """
    return f'<div class="cell"><b>{escape(value)}</b><small>{escape(caption)}</small></div>'


def page_header(character: Character) -> str:
    """Identity block shared by the first page.

    :param character: pregenerated gnome
    :return: HTML
    """
    row1 = (
        field_html(character.name, "Imię postaci")
        + field_html(character.alignment, "Charakter")
        + field_html("", "Gracz")
    )
    row2 = (
        field_html(character.class_line, "Klasa i poziom")
        + field_html(character.deity, "Bóstwo")
        + field_html(character.homeland, "Ojczyzna")
    )
    row3 = (
        field_html(character.race, "Rasa")
        + field_html("mały", "Rozmiar")
        + field_html(character.gender, "Płeć")
        + field_html(character.age, "Wiek")
        + field_html("", "Wzrost")
        + field_html("", "Waga")
        + field_html(character.hair, "Włosy")
        + field_html("", "Oczy")
    )
    return (
        '<header class="head">'
        '<div class="emblem"><div class="g">Pathfinder</div><div class="e">1. edycja</div>'
        '<div class="k">Karta postaci</div></div>'
        '<div class="identity">'
        f'<div class="id1">{row1}</div><div class="id2">{row2}</div><div class="id3">{row3}</div>'
        "</div></header>"
        f'<p class="quote">„{escape(character.quote)}”</p>'
    )


def abilities_html(character: Character) -> str:
    """Ability score table.

    :param character: pregenerated gnome
    :return: HTML
    """
    modifier = mods(character.scores)
    body = []
    for key, label, subtitle in ABILITY_LABELS:
        body.append(
            "<tr>"
            f'<th class="aname"><b>{label}</b><span>{subtitle}</span></th>'
            f"<td>{character.scores[key]}</td><td>{signed(modifier[key])}</td><td></td><td></td>"
            "</tr>"
        )
    return (
        '<table class="abilities"><thead><tr><th></th><th>Wynik</th><th>Mod.</th>'
        "<th>Tymcz.</th><th>Tymcz. mod.</th></tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table>"
    )


def vitals_html(character: Character, combat: dict[str, int]) -> str:
    """Hit points, speed and initiative.

    :param character: pregenerated gnome
    :param combat: derived combat totals
    :return: HTML
    """
    modifier = mods(character.scores)
    speed_bits = (
        ("Ląd", "20 stóp"),
        ("Bazowa", "20 stóp"),
        ("W pancerzu", "20 stóp"),
        ("Lot", "—"),
        ("Pływanie", "—"),
        ("Wspinaczka", "—"),
        ("Kopanie", "—"),
        ("Zwrotność", "—"),
    )
    speed = "".join(f"<div><span>{escape(label)}</span><b>{escape(value)}</b></div>" for label, value in speed_bits)
    return (
        f'<section class="panel hp"><div class="hp-row"><div class="label">Punkty wytrzymałości</div>'
        f'<div class="hp-total"><b>{character.hp}</b><span>suma</span></div></div>'
        f'<div class="wounds"><div class="cap">Bieżące — odhaczaj rany</div>'
        f'<div class="ticks">{squares(character.hp)}</div></div>'
        '<div class="subline"><span>Niegroźne <b>—</b></span><span>Redukcja <b>—</b></span></div></section>'
        f'<section class="panel"><div class="label">Prędkość</div><div class="speed-grid">{speed}</div></section>'
        f'<section class="panel"><div class="label">Inicjatywa</div><div class="init-row">'
        f'<div class="statbox"><b>{signed(combat["inicjatywa"])}</b><span>suma</span></div>'
        f'<div class="statbox"><b>{signed(modifier["zre"])}</b><span>zręczność</span></div>'
        f'<div class="statbox"><b>{signed(character.init_misc)}</b><span>inne</span></div>'
        "</div></section>"
    )


def defense_html(combat: dict[str, int]) -> str:
    """Armor class, saves, attack bonus and maneuvers.

    :param combat: derived combat totals
    :return: HTML
    """
    ac_cells = (
        (str(combat["pancerz"]), "pancerz"),
        (str(combat["tarcza"]), "tarcza"),
        (signed(combat["zre"]), "zręczność"),
        (signed(combat["rozmiar"]), "rozmiar"),
        (str(combat["naturalny"]), "naturalny"),
        (str(combat["odbicie"]), "odbicie"),
        (str(combat["inne"]), "inne"),
    )
    equation = "".join(cell(value, caption) for value, caption in ac_cells)
    saves = (
        ("Wytrwałość", "budowa", combat["wytr"], 1, combat["bud"]),
        ("Refleks", "zręczność", combat["ref"], 1, combat["zre"]),
        ("Wola", "mądrość", combat["wola"], 3, combat["mdr"]),
    )
    save_html = []
    for name, ability, total, base, ability_mod in saves:
        save_html.append(
            '<div class="save">'
            f'<b class="name">{name}<span class="tiny">{ability}</span></b>'
            f'<div class="num">{signed(total)}</div>'
            '<div class="formula">'
            + cell(signed(base), "bazowy")
            + cell(signed(ability_mod), "atrybut")
            + cell("0", "magia")
            + cell("0", "inne")
            + cell("", "tymczasowy")
            + "</div></div>"
        )
    cmb_rest = (
        f'{cell(signed(combat["bpa"]), "premia bazowa")}'
        f'{cell(signed(combat["sil"]), "siła")}'
        f'{cell(signed(combat["rozmiar_pmb"]), "rozmiar")}'
    )
    cmd_rest = (
        f'{cell(signed(combat["bpa"]), "premia bazowa")}'
        f'{cell(signed(combat["sil"]), "siła")}'
        f'{cell(signed(combat["zre"]), "zręczność")}'
        f'{cell(signed(combat["rozmiar_pmb"]), "rozmiar")}'
        '<div class="rest">= 10</div>'
    )
    return (
        '<section class="block"><div class="equation">'
        f'<div class="big">{combat["kp"]}</div><div class="eq">= 10 +</div>{equation}</div>'
        '<div class="ac-foot"><div class="pair"><div class="touch">Dotyk</div>'
        f'<div class="num">{combat["dotyk"]}</div></div>'
        '<div class="pair"><div class="flat">Nieprzygotowany</div>'
        f'<div class="num">{combat["nieprzyg"]}</div></div></div></section>'
        '<section class="block"><div class="banner">Rzuty obronne</div>'
        + "".join(save_html)
        + "</section>"
        '<section class="block"><div class="bab-row"><div class="banner">Bazowa premia do ataku</div>'
        f'<div class="num">{signed(combat["bpa"])}</div>'
        '<div class="sr"><span>Odporność na czary</span><b>—</b></div></div>'
        f'<div class="maneuver"><div class="name">PMB</div><div class="num">{signed(combat["pmb"])}</div>'
        f'<div class="formula">{cmb_rest}</div></div>'
        f'<div class="maneuver"><div class="name">OMB</div><div class="num">{combat["omb"]}</div>'
        f'<div class="formula">{cmd_rest}</div></div></section>'
    )


def weapons_html(character: Character) -> str:
    """Five weapon blocks, the unused ones left blank.

    :param character: pregenerated gnome
    :return: HTML
    """
    weapons = list(character.weapons) + [Weapon()] * (5 - len(character.weapons))
    blocks = []
    for weapon in weapons[:5]:
        name = escape(weapon.name)
        shown = f'<span class="tag">Broń</span> {name}' if name else "Broń"
        blocks.append(
            '<article class="weapon"><div class="weapon-top">'
            f'<div class="banner">{shown}</div>'
            f'<div class="mini"><span>Premia</span><b>{escape(weapon.attack)}</b></div>'
            f'<div class="mini"><span>Krytyk</span><b>{escape(weapon.critical)}</b></div></div>'
            '<div class="weapon-bot">'
            f"<div><span>Typ</span><b>{escape(weapon.kind)}</b></div>"
            f"<div><span>Zasięg</span><b>{escape(weapon.reach)}</b></div>"
            f"<div><span>Amunicja</span><b>{escape(weapon.ammo)}</b></div>"
            f"<div><span>Obrażenia</span><b>{escape(weapon.damage)}</b></div>"
            "</div></article>"
        )
    return f'<div class="weapons">{"".join(blocks)}</div>'


def skills_html(character: Character) -> str:
    """Full skill list.

    :param character: pregenerated gnome
    :return: HTML
    """
    rows = []
    for row in skill_rows(character):
        mark = "mark on" if row["class_skill"] else "mark"
        star = '<span class="star">*</span>' if row["trained_only"] else ""
        total = "" if row["total"] is None else signed(int(row["total"]))
        ranks = "" if int(row["ranks"]) == 0 else str(row["ranks"])
        misc = "" if int(row["misc"]) == 0 else signed(int(row["misc"]))
        ability = f'{signed(int(row["ability_mod"]))} {ABILITY_ABBR[str(row["ability"])]}'
        rows.append(
            "<tr>"
            f'<td class="name"><i class="{mark}"></i>{escape(str(row["label"]))}{star}</td>'
            f'<td class="num">{total}</td>'
            f'<td class="ab">{ability}</td>'
            f'<td class="num">{ranks}</td>'
            f'<td class="num">{misc}</td>'
            "</tr>"
        )
    return (
        '<table class="skills"><thead><tr>'
        '<th class="name">Umiejętność</th><th>Suma</th><th>Atrybut</th><th>Rangi</th><th>Inne</th>'
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
        '<p class="legend"><i class="mark on"></i> umiejętność klasowa &nbsp; * tylko po wyszkoleniu. '
        "Premia +3 za klasę jest w kolumnie „inne”, gdy wydano rangę.</p>"
    )


def notes_html(title: str, text: str, grow: bool = False) -> str:
    """A boxed note under a black bar.

    :param title: bar label
    :param text: paragraph
    :param grow: whether the box eats leftover space
    :return: HTML
    """
    klass = "note grow" if grow else "note"
    return f'<section class="{klass}"><div class="banner">{escape(title)}</div><p>{escape(text)}</p></section>'


def first_page(character: Character) -> str:
    """Render page one.

    :param character: pregenerated gnome
    :return: HTML article
    """
    combat = combat_of(character)
    return (
        '<article class="sheet"><div class="frame">'
        + page_header(character)
        + '<div class="cols"><div class="left"><div class="top">'
        + abilities_html(character)
        + f'<div class="vitals">{vitals_html(character, combat)}</div></div>'
        + defense_html(combat)
        + weapons_html(character)
        + '</div><div class="right"><div class="banner">Umiejętności</div>'
        + skills_html(character)
        + notes_html("Modyfikatory warunkowe", character.combat_notes)
        + notes_html("Języki", character.languages, grow=True)
        + "</div></div>"
        + f"<footer><span>{escape(character.name)}</span><span>strona 1 z 2</span></footer>"
        + "</div></article>"
    )


def lined(items: tuple[str, ...]) -> str:
    """One item per ruled line, with blank rules underneath.

    :param items: gear lines
    :return: HTML
    """
    lines = "".join(f'<div class="line">{escape(item)}</div>' for item in items)
    return f'<div class="lined"><div class="lines"></div><div class="items">{lines}</div></div>'


def gear_html(character: Character) -> str:
    """Armor table, gear, carrying capacity and coins.

    :param character: pregenerated gnome
    :return: HTML for the left column of page two
    """
    light, medium, heavy, overhead, ground, push = character.load
    load_rows = (
        ("Lekki", light, "Nad głowę", overhead),
        ("Średni", medium, "Z ziemi", ground),
        ("Ciężki", heavy, "Pchanie", push),
    )
    load = "".join(
        f"<div><span>{left}</span><b>{left_n}</b></div><div><span>{right}</span><b>{right_n}</b></div>"
        for left, left_n, right, right_n in load_rows
    )
    return (
        '<section class="box"><div class="banner">Pancerz i tarcza</div>'
        '<table class="grid"><thead><tr><th>Przedmiot</th><th>Premia</th><th>Typ</th>'
        "<th>Kara</th><th>Niepow.</th><th>Ciężar</th></tr></thead><tbody>"
        '<tr><td class="item">brak noszonego pancerza</td><td>0</td><td>—</td><td>0</td><td>0%</td><td>—</td></tr>'
        '<tr><td class="item">suma</td><td>0</td><td></td><td>0</td><td>0%</td><td>—</td></tr>'
        "</tbody></table></section>"
        '<section class="box grow"><div class="banner">Ekwipunek</div>'
        + lined(character.gear)
        + "</section>"
        '<section class="box"><div class="banner">Udźwig</div>'
        '<div class="cap">Funty, rozmiar mały</div>'
        f'<div class="load">{load}</div></section>'
        '<section class="box"><div class="banner">Pieniądze</div><div class="coins">'
        '<div class="coin"><b>0</b><span>miedź</span></div>'
        '<div class="coin"><b>0</b><span>srebro</span></div>'
        f'<div class="coin"><b>{character.gp}</b><span>złoto</span></div>'
        '<div class="coin"><b>0</b><span>platyna</span></div></div></section>'
    )


def feats_html(character: Character) -> str:
    """Feats, special abilities and experience.

    :param character: pregenerated gnome
    :return: HTML for the middle column
    """
    feats = "".join(f"<li><b>{escape(name)}.</b> {escape(detail)}</li>" for name, detail in character.feats)
    specials = "".join(f"<li>{escape(line)}</li>" for line in character.specials)
    return (
        f'<section class="box"><div class="banner">Atuty</div><ul class="plain">{feats}</ul></section>'
        f'<section class="box grow"><div class="banner">Zdolności specjalne</div><ul class="plain">{specials}</ul></section>'
        '<section class="box"><div class="xp"><div><span>Punkty doświadczenia</span><b>5 000</b></div>'
        "<div><span>Następny poziom</span><b>9 000</b></div></div></section>"
    )


def spells_html(character: Character) -> str:
    """Spell table and the prepared or known list.

    :param character: pregenerated gnome
    :return: HTML for the right column
    """
    table = []
    for level in range(10):
        known, dc, per_day, bonus = character.spell_table.get(level, ("", "", "", ""))
        table.append(
            f"<tr><td>{escape(known)}</td><td>{escape(dc)}</td><td>{level}</td>"
            f"<td>{escape(per_day)}</td><td>{escape(bonus)}</td></tr>"
        )
    levels = []
    for level in range(3):
        lines = character.spells.get(level, ())
        body = "".join(f'<div class="spline">{escape(line)}</div>' for line in lines)
        if not body:
            body = '<div class="spline blank"></div>'
        boxes = squares(character.expend.get(level, 0))
        levels.append(
            f'<div class="splevel"><div><div class="lv">{level}</div><div class="slots">{boxes}</div></div>'
            f"<div>{body}</div></div>"
        )
    higher = "".join(f"<div>{level}</div>" for level in range(3, 10))
    return (
        '<section class="box"><div class="banner">Czary</div>'
        '<table class="grid spellhead"><thead><tr><th>Znane</th><th>ST</th><th>Krąg</th>'
        "<th>Dziennie</th><th>Premia</th></tr></thead><tbody>"
        + "".join(table)
        + "</tbody></table></section>"
        f'<section class="box"><div class="banner">Szkoła albo linia krwi</div><div class="school">{escape(character.school)}</div></section>'
        f'<section class="box"><div class="school">{escape(character.spell_notes)}</div></section>'
        '<section class="box grow"><div class="banner">Przygotowane i znane</div>'
        f'<div class="spells">{"".join(levels)}<div class="higher">{higher}</div></div></section>'
    )


def second_page(character: Character) -> str:
    """Render page two.

    :param character: pregenerated gnome
    :return: HTML article
    """
    return (
        '<article class="sheet"><div class="frame">'
        '<div class="p2head"><div class="what">Karta postaci · Pathfinder 1e</div>'
        f'<div class="who">{escape(character.name)}</div></div>'
        '<div class="page2"><div class="col">'
        + gear_html(character)
        + '</div><div class="col">'
        + feats_html(character)
        + '</div><div class="col">'
        + spells_html(character)
        + "</div></div>"
        + f"<footer><span>{escape(character.name)}</span><span>strona 2 z 2</span></footer>"
        + "</div></article>"
    )


def document(title: str, nav: str, sheets: str) -> str:
    """Wrap sheets in a printable document.

    :param title: browser title
    :param nav: screen-only links
    :param sheets: one or more articles
    :return: full HTML document
    """
    return (
        "<!DOCTYPE html>\n<html lang=\"pl\">\n<head>\n<meta charset=\"utf-8\">\n"
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{escape(title)}</title>\n<style>\n{STYLESHEET}\n</style>\n</head>\n<body>\n"
        f"{nav}\n{sheets}\n</body>\n</html>\n"
    )


def navigation(character: Character | None) -> str:
    """Screen-only links back to the print index and the prose packet.

    :param character: sheet being shown, or None for the combined file
    :return: HTML paragraph
    """
    links = '<a href="index.html">Spis postaci</a>'
    if character is not None:
        links += f' · <a href="{escape(character.slug)}.html">Opis, czary i historia</a>'
    links += ' · <a href="arkusze.html">Wszystkie arkusze</a>'
    return f'<p class="powrot">{links}</p>'


def render_sheet_pages() -> dict[str, str]:
    """Build every filled sheet and the combined file.

    :return: filename to HTML document
    :raises RuntimeError: when a total does not match the written sheet
    """
    verify_all()
    pages = {
        f"arkusz-{character.slug}.html": document(
            f"{character.name} — karta postaci",
            navigation(character),
            first_page(character) + second_page(character),
        )
        for character in CHARACTERS
    }
    combined = "".join(first_page(character) + second_page(character) for character in CHARACTERS)
    pages["arkusze.html"] = document("Arkusze postaci", navigation(None), combined)
    return pages


def index_entries() -> tuple[tuple[str, str, str], ...]:
    """Filenames and blurbs for the print index.

    :return: filename, title, description
    """
    entries = [
        (
            "arkusze.html",
            "Wszystkie arkusze",
            "Pięć kart jedna po drugiej. Dwie strony na postać, układ karty Pathfindera.",
        )
    ]
    for character in CHARACTERS:
        entries.append(
            (
                f"arkusz-{character.slug}.html",
                character.name,
                "Dwie strony: obrona, ataki, umiejętności, ekwipunek i czary.",
            )
        )
    return tuple(entries)
