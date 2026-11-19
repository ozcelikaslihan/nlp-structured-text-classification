"""Create a readable results table and audit from the frozen reviewed run."""
import json
from pathlib import Path
from collections import Counter

root = Path('outputs/main_reviewed')
summary = json.loads((root / 'summary.json').read_text(encoding='utf-8'))
rows = [json.loads(x) for x in (root / 'generations.jsonl').read_text(encoding='utf-8').splitlines()]
gold = {r['id']: r for r in map(json.loads, Path('outputs/reviewed_annotations_20261119.jsonl').read_text(encoding='utf-8').splitlines())}
assert len(rows) == 210
assert len({(r['sample_id'],r['setting']) for r in rows}) == 210
lines = ['# Ana deney sonuçları', '', '105 insan tarafından incelenmiş haber, 949 gold varlık. Temperature=0, seed=42.', '',
         '| Ayar | Ham JSON | Temiz JSON | Şema | Sınıflandırma doğruluğu | Entity micro-F1 |',
         '|---|---:|---:|---:|---:|---:|']
for setting, values in summary['settings'].items():
    fields = ['raw_json_success_rate','cleaned_json_success_rate','schema_validity_rate','classification_accuracy','entity_f1_micro']
    lines.append('| '+setting+' | '+' | '.join(f'{values[k]*100:.2f}%' for k in fields)+' |')
lines += ['', '## Çalıştırma denetimi', '']
for setting in summary['settings']:
    subset = [r for r in rows if r['setting']==setting]
    errors = sum(bool(r['generation_error']) for r in subset)
    reasons = dict(Counter(r.get('done_reason') for r in subset))
    lines.append(f'- {setting}: {len(subset)} çıktı; çağrı hatası={errors}; bitiş nedenleri={reasons}.')
lines += ['', '## Yanlış sınıflandırma örnekleri', '']
for setting in summary['settings']:
    lines.append(f'### {setting}')
    wrong = [r for r in rows if r['setting']==setting and r['schema_valid'] and r['parsed_output']['category'] != gold[r['sample_id']]['gold_category']]
    for r in wrong[:5]:
        g = gold[r['sample_id']]
        lines.append(f"- {r['sample_id']}: gold={g['gold_category']}, tahmin={r['parsed_output']['category']}. Metin başlangıcı: {g['text'][:180]}")
lines += ['', '## Yorumlama', '', 'Şema geçerliliği doğru sınıf veya doğru varlık garantisi değildir. Görev metrikleri bütün 105 örnek üzerinden hesaplanır; geçersiz çıktı yanlış sınıf ve boş varlık tahmini sayılır. Varlıklar tür ve Türkçe normalizasyonlu tam metin eşleşmesiyle değerlendirilir.', '', 'Bu tablo ana temperature=0 deneyidir. Video için iki sıcaklık ve beş yeni örnek deneyi ayrıca yapılmalıdır.']
Path('outputs/ana_deney_sonuclari.md').write_text('\n'.join(lines), encoding='utf-8')
print('\n'.join(lines[:14]))
