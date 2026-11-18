"""Prompt construction. Both settings deliberately use the same messages."""

from __future__ import annotations

import json

from .schema import OUTPUT_JSON_SCHEMA

SYSTEM_PROMPT = """Sen bir Türkçe haber sınıflandırma ve varlık çıkarma sistemisin.
Yalnızca geçerli bir JSON nesnesi döndür. Markdown, açıklama veya kod bloğu ekleme.
category tam olarak şu değerlerden biri olmalı:
- dunya: uluslararası ilişkiler, yabancı ülkelerdeki genel olaylar
- ekonomi: finans, şirketler, piyasalar, ticaret ve para politikası
- kultur: sanat, sinema, müzik, edebiyat ve kültürel etkinlikler
- saglik: hastalık, tedavi, tıp ve halk sağlığı
- siyaset: hükümet, parlamento, seçimler, partiler ve kamu politikası
- spor: maçlar, sporcular, takımlar ve spor organizasyonları
- teknoloji: yazılım, donanım, internet, bilimsel-teknolojik ürün ve gelişmeler
entities.persons yalnızca açık kişi adlarını içermeli.
entities.organizations kurum/şirket/siyasi parti/spor takımı adlarını içermeli.
entities.locations ülke/şehir/coğrafi yer adlarını içermeli.
Bir meslek veya görev adı tek başına PERSON değildir. Bir spor kulübü ORGANIZATION türündedir.
Varlık metnini girdide göründüğü yüzey biçimiyle kopyala. Her farklı varlığı en fazla bir kez yaz; tekrarlama.
Ürün, etkinlik, tarih ve para miktarlarını varlık olarak çıkarma. Her listede en fazla 20 varlık döndür.
Bir türde varlık yoksa o tür için boş liste kullan."""


def build_messages(text: str) -> list[dict[str, str]]:
    """Build identical messages for prompt-only and schema-constrained runs."""

    schema_text = json.dumps(OUTPUT_JSON_SCHEMA, ensure_ascii=False, separators=(",", ":"))
    user_prompt = (
        "Aşağıdaki haberi sınıflandır ve varlıklarını çıkar.\n"
        f"Uyman gereken JSON şeması: {schema_text}\n"
        "HABER BAŞLANGICI\n"
        f"{text.strip()}\n"
        "HABER SONU"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

