# Video hazırlık kartı

Bu notlar okunacak bir konuşma metni değildir. İngilizce anlatımı kendi cümlelerinle yap.

## Bölümler (hedef süreler)

- 00:00-08:00: yüzün görünür giriş, veri, manuel anotasyon, prompt, Ollama çağrısı, temizleme ve metrik kodu.
- 08:00-16:00: kesintisiz canlı test. Gerçek süreyi prova sonunda ayarla.
- 16:00-29:00: A1-A4 ve B1, C1, D1, E1, F6, G1.

## Çalıştırma

Proje klasöründe `.venv\Scripts\python.exe -u scripts/live_demo.py` çalıştır.
İlk iki veri örneği ve beş yeni metin, iki sıcaklıkta ve iki ayarda gösterilir (28 çağrı).
Yeni metinler birer test cümlesidir; güncel haber olarak sunma. NEW-5 bütçe düzenlemesi
ekonomi/siyaset sınırındadır. Beklenen hata gerçekleşmeyebilir; gözlediğini anlat.
Bu komutun ekran ve ses kaydı kesintisiz olmalı. Önceki prova kaydı canlı test yerine geçmez.

## Savunma için konuşma noktaları

1. **A1:** `_first_balanced_json_object` içindeki `return text[start : index + 1]` satırını göster.
   `.venv\Scripts\python.exe scripts/defense_ablation.py`: satır varken True,
   fonksiyonun bellekteki kopyasından bu satır kaldırılınca False ve yakalanan JSONDecodeError.
   `pass` yalnızca boş if bloğunun geçerli Python kalmasını sağlar. Sentetik test olduğunu belirt.
2. **A2:** Karar günlüğünü incele. Ek kategori kuralları geliştirme accuracy'sini %60'tan
   %57,1'e düşürdüğü için geri alındı. AI'nın önerisini değerlendirmenin önemini anlat.
3. **A3:** Şema geçerliliği artmasına rağmen entity F1'in düşmesi: daha fazla doğru varlığın
   yanında daha fazla yanlış varlık çıktı. Raporun TP/FP/FN değerlerini kullan.
4. **A4:** Temperature=0 tablosunu göster. Aynı prompt/seed, tek fark format argümanı.
   Şema doğruluk garantisi vermez. Geçersiz çıktılar accuracy hesabında yanlış sayılır.
5. **B1:** N-gram sabit uzunlukta geçmiş üzerinden sayımlarla olasılık tahmin eder.
   Transformer attention ile bağlam temsili üretir; logits/softmax sonraki token dağılımını verir.
   Decoding bu dağılımdan seçim yapar; model bir sonraki cümleyi tek adımda seçmez.
6. **C1:** Rapordaki temperature=0 ve 1 satırlarını karşılaştır. Yüksek sıcaklık dağılımı
   yumuşatır, daha az olası tokenlar seçilebilir. Bu çalışmanın gözlemini söyle; bütün
   modellerde accuracy mutlaka düşer gibi bir iddia kurma. Canlı sıcaklık testi deney kanıtıdır.
7. **D1:** `ollama show qwen2.5:3b` çalıştır. Quantization alanı Q4_K_M.
   Kuantizasyon ağırlıkların temsil hassasiyetini azaltır; bellek ile kalite arasında tercih vardır.
8. **E1:** Türkçenin eklemeli yapısı ve tokenizer eğitim dağılımı daha çok alt parçaya
   neden olabilir. Türkçe her zaman daha çok token olur deme; model ve metne bağlıdır.
9. **F6:** Prompt denemeleri 35 geliştirme örneğinde yapıldı. Nihai 105 örnek üzerinde
   sonuç görüldükten sonra prompt değiştirilmedi. Başlangıçta split dondurulmadan önce
   bir örnek incelendiğini gizleme. Testte sürekli ayar yapmak sonuçları iyimserleştirir.
10. **G1:** Yeterli etiketli ve alan içi veri varsa TF-IDF + lojistik regresyon küçük
    zero-shot LLM'den daha iyi olabilir. Bu projede klasik baseline çalıştırılmadı;
    ölçülmüş bir üstünlük iddiasında bulunma. Entity extraction ayrıca çözülmelidir.

## Teslim öncesi

Rapor en fazla dört sayfa; model ve parametreleri videoyla aynı. Videonun dili İngilizce,
süresi en fazla 30 dakika; başlangıçta yüz, boyunca ekran ve ses. YouTube görünürlüğü
Unlisted. Açıklamada gerçek bölüm zamanlarını yaz. Forma canlı test ve savunma başlangıçlarını
gir. Kod + rapor bağlantısının görüntüleme erişimini kontrol et. Son tarih 22 Kasım 2026 23:59.
