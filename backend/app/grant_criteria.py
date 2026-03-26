"""Oliy ta'lim granti bo'yicha ijtimoiy faollik — 11 ta mezon (jami 100 ball)."""

from typing import List, TypedDict


class GrantCriterion(TypedDict):
    id: int
    name: str
    max_points: int


# T/r bo'yicha rasmiy ko'rsatkichlar (ball oralig'i jadvalga muvofiq)
GRANT_CRITERIA: List[GrantCriterion] = [
    {"id": 1, "name": "Kitobxonlik madaniyati", "max_points": 20},
    {
        "id": 2,
        "name": "“5 muhim tashabbus” doirasidagi to‘garaklarda faol ishtiroki",
        "max_points": 20,
    },
    {"id": 3, "name": "Talabaning akademik o‘zlashtirishi", "max_points": 10},
    {
        "id": 4,
        "name": "Talabaning oliy ta’lim tashkilotining ichki tartib qoidalari va Odob-axloq kodeksiga rioya etishi",
        "max_points": 5,
    },
    {
        "id": 5,
        "name": "Xalqaro, respublika, viloyat miqyosidagi ko‘rik-tanlov, fan olimpiadalari va sport musobaqalarida erishgan natijalari",
        "max_points": 10,
    },
    {
        "id": 6,
        "name": "Talabaning darslarga to‘liq va kechikmasdan kelishi",
        "max_points": 5,
    },
    {
        "id": 7,
        "name": "Talabalarning “Ma’rifat darslari”dagi faol ishtiroki",
        "max_points": 10,
    },
    {
        "id": 8,
        "name": "Volontyorlik va jamoat ishlaridagi faolligi",
        "max_points": 5,
    },
    {
        "id": 9,
        "name": "Teatr va muzey, xiyobon, kino, tarixiy qadamjolarga tashriflar",
        "max_points": 5,
    },
    {
        "id": 10,
        "name": "Talabalarning sport bilan shug‘ullanishi va sog‘lom turmush tarziga amal qilishi",
        "max_points": 5,
    },
    {
        "id": 11,
        "name": "Ma’naviy-ma’rifiy sohaga oid boshqa yo‘nalishlardagi faolligi",
        "max_points": 5,
    },
]

TOTAL_GRANT_POINTS = 100
