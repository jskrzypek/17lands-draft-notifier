#!/usr/bin/env python3
"""
Process 17lands logs for draft packs and print card ratings to stdout.

Arguments:
    ratings:
        Path to CSV file containing card ratings data. This should
        be exported from the 17lands card data page.
        (https://www.17lands.com/card_data)

Options:
    --ratings-column, -r:
        Column name(s) for rating values to sort on and display.
        Default: ["GIH WR"]
        Can specify multiple times to sort on multiple columns.
        Order matters. You may prefix a column name with a "-"
        to sort in ascending order.
"""


from argparse import ArgumentParser, ONE_OR_MORE, Action
from csv import DictReader
from functools import lru_cache
from pathlib import Path
import re
from sys import stdin
from typing import Literal, cast


class SetAddAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        items: list = getattr(namespace, self.dest) or []
        items.extend(value for value in values if value not in items)
        setattr(namespace, self.dest, items)


parser = ArgumentParser()
parser.add_argument("ratings", help="CSV file with ratings", type=Path)
parser.add_argument("ids", help="CSV file with ids", type=Path)
parser.add_argument(
    "--ratings-column",
    "-r",
    help="Column with ratings",
    default=["GIH WR"],
    nargs=ONE_OR_MORE,
    action=SetAddAction,
)

draft_notify_re = re.compile(
    r"^.*\(Draft\.Notify\): (?P<draft_notify>\{.*\})$",
)


columns = {
    "Name": "name",
    "CardID": "card_id",
    "Color": "color",
    "Rarity": "rarity",
    "# Seen": "num_seen",
    "ALSA": "alsa",
    "# Picked": "num_picked",
    "ATA": "ata",
    "# GP": "num_gp",
    "% GP": "pct_gp",
    "GP WR": "gp_wr",
    "# OH": "num_oh",
    "OH WR": "oh_wr",
    "# GD": "num_gd",
    "GD WR": "gd_wr",
    "# GIH": "num_gih",
    "GIH WR": "gih_wr",
    "# GNS": "num_gns",
    "GNS WR": "gns_wr",
    "IWD": "iwd",
}

Card = dict[
    Literal[
        "Name",
        "CardID",
        "Color",
        "Rarity",
        "# Seen",
        "ALSA",
        "# Picked",
        "ATA",
        "# GP",
        "% GP",
        "GP WR",
        "# OH",
        "OH WR",
        "# GD",
        "GD WR",
        "# GIH",
        "GIH WR",
        "# GNS",
        "GNS WR",
        "IWD",
    ],
    str,
]


class CardRating:
    name: str  # "Name"
    card_id: int  # "CardID"
    color: str  # "Color"
    rarity: str  # "Rarity"
    card: Card
    _num_seen: int | None  # "# Seen"
    _alsa: float | None  # "ALSA"
    _num_picked: int | None  # "# Picked"
    _ata: float | None  # "ATA"
    _num_gp: int | None  # "# GP"
    _pct_gp: float | None  # "% GP"
    _gp_wr: float | None  # "GP WR"
    _num_oh: int | None  # "# OH"
    _oh_wr: float | None  # "OH WR"
    _num_gd: int | None  # "# GD"
    _gd_wr: float | None  # "GD WR"
    _num_gih: int | None  # "# GIH"
    _gih_wr: float | None  # "GIH WR"
    _num_gns: int | None  # "# GNS"
    _gns_wr: float | None  # "GNS WR"
    _iwd: float | None  # "IWD"

    def __init__(self, card: Card) -> None:
        self.card = card
        self.name = card["Name"]
        self.card_id = int(card["CardID"])
        self.color = card["Color"]
        self.rarity = card["Rarity"]

        self._num_seen = None if not card.get("# Seen") else int(card["# Seen"])
        self._alsa = None if not card.get("ALSA") else float(card["ALSA"])
        self._num_picked = None if not card.get("# Picked") else int(card["# Picked"])
        self._ata = None if not card.get("ATA") else float(card["ATA"])
        self._num_gp = None if not card.get("# GP") else int(card["# GP"])
        self._pct_gp = None if not card.get("% GP") else float(card["% GP"].strip("%"))
        self._gp_wr = None if not card.get("GP WR") else float(card["GP WR"].strip("%"))
        self._num_oh = None if not card.get("# OH") else int(card["# OH"])
        self._oh_wr = None if not card.get("OH WR") else float(card["OH WR"].strip("%"))
        self._num_gd = None if not card.get("# GD") else int(card["# GD"])
        self._gd_wr = None if not card.get("GD WR") else float(card["GD WR"].strip("%"))
        self._num_gih = None if not card.get("# GIH") else int(card["# GIH"])
        self._gih_wr = (
            None if not card.get("GIH WR") else float(card["GIH WR"].strip("%"))
        )
        self._num_gns = None if not card.get("# GNS") else int(card["# GNS"])
        self._gns_wr = (
            None if not card.get("GNS WR") else float(card["GNS WR"].strip("%"))
        )
        self._iwd = None if not card.get("IWD") else float(card["IWD"].strip("p"))

    @property
    def num_seen(self) -> str:
        return str(self._num_seen) or ""

    @property
    def alsa(self) -> str:
        return f"{self._alsa:.02f}" if self._alsa is not None else ""

    @property
    def num_picked(self) -> str:
        return str(self._num_picked) or ""

    @property
    def ata(self) -> str:
        return f"{self._ata:.02f}" if self._ata is not None else ""

    @property
    def num_gp(self) -> str:
        return str(self._num_gp) or ""

    @property
    def pct_gp(self) -> str:
        return f"{self._pct_gp:02.02f}%" if self._pct_gp is not None else ""

    @property
    def gp_wr(self) -> str:
        return f"{self._gp_wr:02.02f}%" if self._gp_wr is not None else ""

    @property
    def num_oh(self) -> str:
        return str(self._num_oh) or ""

    @property
    def oh_wr(self) -> str:
        return f"{self._oh_wr:02.02f}%" if self._oh_wr is not None else ""

    @property
    def num_gd(self) -> str:
        return str(self._num_gd) or ""

    @property
    def gd_wr(self) -> str:
        return f"{self._gd_wr:02.02f}%" if self._gd_wr is not None else ""

    @property
    def num_gih(self) -> str:
        return str(self._num_gih) or ""

    @property
    def gih_wr(self) -> str:
        return f"{self._gih_wr:02.02f}%" if self._gih_wr is not None else ""

    @property
    def num_gns(self) -> str:
        return str(self._num_gns) or ""

    @property
    def gns_wr(self) -> str:
        return f"{self._gns_wr:02.02f}%" if self._gns_wr is not None else ""

    @property
    def iwd(self) -> str:
        return f"{self._iwd:02.02f}" if self._iwd is not None else ""

    def print_columns(self, ratings_columns: list[str]) -> str:
        return "\t".join(
            f'{k.strip("-").replace(" ", "_")} = '
            f'{getattr(card, columns[k.strip("-")]) or " --- "}'
            for k in ratings_columns
        )


draft_notify_dict = dict[
    Literal[
        "draft_id",
        "event_name",
        "pack_number",
        "pick_number",
        "card_ids",
    ],
    str | int,
]


class DraftPack:
    draft_id: str
    event_name: str
    pack_number: int
    pick_number: int
    card_ids: list[int]
    method: str
    cards: list[CardRating]

    def __init__(
        self,
        ratings_by_id: dict[str, CardRating],
        /,
        draft_id: str,
        event_name: str,
        pack_number: int,
        pick_number: int,
        method: str,
        card_ids: list[int],
    ) -> None:
        self.draft_id = draft_id
        self.event_name = event_name
        self.pack_number = pack_number
        self.pick_number = pick_number
        self.card_ids = card_ids
        self.method = method
        self.cards = [ratings_by_id[str(card_id)] for card_id in card_ids]


@lru_cache(maxsize=1)
def build_dict_by_card_id(
    ratings_file: Path,
    ids_file: Path,
) -> dict[str, CardRating]:
    ratings_dict: dict[str, CardRating] = {}
    cards_by_name: dict[str, dict] = {
        card["Name"].strip(): cast(Card, card)
        for card in DictReader(ids_file.open("rt", encoding="utf-8"))
    }
    for i, ratings in enumerate(
        DictReader(ratings_file.open("rt", encoding="utf-8-sig"))
    ):
        card = cards_by_name[ratings["Name"].strip()]
        ratings_dict[card["CardID"]] = CardRating(
            cast(
                Card,
                card | ratings,
            )
        )
    return ratings_dict


if __name__ == "__main__":
    args = parser.parse_args()
    print(args)
    ratings_by_id = build_dict_by_card_id(args.ratings, args.ids)

    while True:
        line = stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue

        m = draft_notify_re.match(line)
        if not m:
            continue

        pack = DraftPack(ratings_by_id, **eval(m.group("draft_notify")))

        if not pack.cards:
            continue
        pack.cards.sort(
            key=lambda card: tuple(
                (
                    -(getattr(card, f"_{columns[k[1:]]}") or 0)
                    if k[0] == "-"
                    else getattr(card, f"_{columns[k]}") or 0
                )
                for k in args.ratings_column
            ),
            reverse=True,
        )
        print(
            f"\n\nDraft {pack.draft_id} Pack {pack.pack_number} "
            f"Pick {pack.pick_number}:\n"
        )
        for i, card in enumerate(pack.cards):
            if not card:
                continue

            print(
                f"{i+pack.pick_number:02d}:\t"
                f"{card.print_columns(args.ratings_column)}\t"
                f"|\t{card.card_id}\t'{card.name}'\t{card.color}\t"
                f"{card.rarity}"
            )
