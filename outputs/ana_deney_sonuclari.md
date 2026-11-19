# Ana deney sonuçları

105 insan tarafından incelenmiş haber, 949 gold varlık. Temperature=0, seed=42.

| Ayar | Ham JSON | Temiz JSON | Şema | Sınıflandırma doğruluğu | Entity micro-F1 |
|---|---:|---:|---:|---:|---:|
| prompt_only | 98.10% | 98.10% | 92.38% | 49.52% | 30.05% |
| schema_constrained | 99.05% | 99.05% | 99.05% | 54.29% | 29.63% |

## Çalıştırma denetimi

- prompt_only: 105 çıktı; çağrı hatası=0; bitiş nedenleri={'stop': 103, 'length': 2}.
- schema_constrained: 105 çıktı; çağrı hatası=0; bitiş nedenleri={'stop': 104, 'length': 1}.

## Yanlış sınıflandırma örnekleri

### prompt_only
- ttc4900-row-2847: gold=saglik, tahmin=ekonomi. Metin başlangıcı: iki reçeteden biri elektronik oldu 1 temmuz tarihinden itibaren yazılan reçetelerin yüzde 50 56 sı elektronik ortamda oluşturuldu sosyal_güvenlik_kurumu 1 temmuz da uygulamaya konu
- ttc4900-row-2444: gold=kultur, tahmin=siyaset. Metin başlangıcı: amy_winehouse un alkol zehirlenmesinden öldüğü doğrulandı ingiliz mahkemesi önceki yıl hayatını kaybeden şarkıcı amy_winehouse un aşırı alkol tüketiminden hayatını kaybettiğini doğ
- ttc4900-row-1540: gold=ekonomi, tahmin=siyaset. Metin başlangıcı: yunan hükümetine kemer sıkma övgüsü alman hükümeti yunanistan da ülke çapında protestolara rağmen parlamentoda kabul edilen kemer sıkma önlemlerini önemli bir adım olarak değerlend
- ttc4900-row-2969: gold=saglik, tahmin=ekonomi. Metin başlangıcı: sigara ile rus ruleti oynuyoruz ingiltere  de sağlık_bakanlığı  nın 2 7 milyon sterline hazırladığı reklam kampanyası tartışmalara neden oldu kampanyada 15 sigaranın dahi kanserl
- ttc4900-row-2633: gold=kultur, tahmin=teknoloji. Metin başlangıcı: enrico macias la düet yapacak fransa nın eski cumhurbaşkanı nicolas sarkzoy nin eşi carla_bruni enrico macias ın son albümüne düet yaparak katkı verecek eski manken ve şarkıcı brun
### schema_constrained
- ttc4900-row-2847: gold=saglik, tahmin=ekonomi. Metin başlangıcı: iki reçeteden biri elektronik oldu 1 temmuz tarihinden itibaren yazılan reçetelerin yüzde 50 56 sı elektronik ortamda oluşturuldu sosyal_güvenlik_kurumu 1 temmuz da uygulamaya konu
- ttc4900-row-2444: gold=kultur, tahmin=siyaset. Metin başlangıcı: amy_winehouse un alkol zehirlenmesinden öldüğü doğrulandı ingiliz mahkemesi önceki yıl hayatını kaybeden şarkıcı amy_winehouse un aşırı alkol tüketiminden hayatını kaybettiğini doğ
- ttc4900-row-1540: gold=ekonomi, tahmin=siyaset. Metin başlangıcı: yunan hükümetine kemer sıkma övgüsü alman hükümeti yunanistan da ülke çapında protestolara rağmen parlamentoda kabul edilen kemer sıkma önlemlerini önemli bir adım olarak değerlend
- ttc4900-row-2969: gold=saglik, tahmin=ekonomi. Metin başlangıcı: sigara ile rus ruleti oynuyoruz ingiltere  de sağlık_bakanlığı  nın 2 7 milyon sterline hazırladığı reklam kampanyası tartışmalara neden oldu kampanyada 15 sigaranın dahi kanserl
- ttc4900-row-2633: gold=kultur, tahmin=teknoloji. Metin başlangıcı: enrico macias la düet yapacak fransa nın eski cumhurbaşkanı nicolas sarkzoy nin eşi carla_bruni enrico macias ın son albümüne düet yaparak katkı verecek eski manken ve şarkıcı brun

## Yorumlama

Şema geçerliliği doğru sınıf veya doğru varlık garantisi değildir. Görev metrikleri bütün 105 örnek üzerinden hesaplanır; geçersiz çıktı yanlış sınıf ve boş varlık tahmini sayılır. Varlıklar tür ve Türkçe normalizasyonlu tam metin eşleşmesiyle değerlendirilir.

Bu tablo ana temperature=0 deneyidir. Video için iki sıcaklık ve beş yeni örnek deneyi ayrıca yapılmalıdır.