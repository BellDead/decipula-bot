<<<<<<< HEAD
# 🎮 DECIPULA Discord Bot

Discord sunucusu için oyun rol sistemi botu.

## ✨ Özellikler

- 🎮 Yeni üyelere otomatik oyun seçim menüsü
- 🏷️ Oyun rolleri ve kanal erişimi
- ⚙️ Admin komutları
- 🌐 Sunucu entegrasyon araçları

## 🎮 Desteklenen Oyunlar

| Oyun | Rol | Metin Kanalları | Ses Kanalları |
|------|-----|-----------------|---------------|
| Minecraft | Minecraft | minecraft-chat, minecraft-tips, minecraft-builds | minecraft-voice, minecraft-survival, minecraft-creative |
| League of Legends | LoL | lol-chat, lol-strategy, lol-meta | lol-voice, lol-ranked, lol-normals |
| Valorant | Valorant | valorant-chat, valorant-tips, valorant-lineups | valorant-voice, valorant-ranked, valorant-unrated |
| CS2 | CS2 | cs2-chat, cs2-strategy, cs2-maps | cs2-voice, cs2-competitive, cs2-casual |
| Fortnite | Fortnite | fortnite-chat, fortnite-builds, fortnite-events | fortnite-voice, fortnite-arena, fortnite-pubs |
| GTA V | GTA | gta-chat, gta-missions, gta-roleplay | gta-voice, gta-heists, gta-freemode |
| Rocket League | RocketLeague | rl-chat, rl-tips, rl-trading | rl-voice, rl-ranked, rl-casual |
| Among Us | AmongUs | amongus-chat, amongus-strategy | amongus-voice, amongus-lobby |

## 🌐 Ortak Alanlar

**Metin Kanalları:** genel-sohbet, duyurular, yardım, memes, anime-manga, teknoloji, spor

**Ses Kanalları:** genel-ses, müzik, afk, toplantı, çalışma-odası

## 🚀 Kurulum

1. Discord Developer Portal'dan bot oluşturun
2. Bot token'ını alın
3. Railway'e deploy edin

## 📋 Komutlar

### Kullanıcı Komutları
- `!oyunlar` - Desteklenen oyunları listeler
- `!rollerim` - Sahip olduğun rolleri gösterir
- `!yardım` - Tüm komutları gösterir

### Admin Komutları
- `!oyun-ekle` - Yeni oyun ekler
- `!oyun-sil` - Oyun siler
- `!yapılandırma` - Bot ayarlarını gösterir

## 🔧 Mevcut Sunucu Entegrasyonu

### Otomatik Kurulum
Bot'u mevcut sunucunuza ekledikten sonra:

1. **Kurulum Rehberi**: `!sunucu-ayarla` komutuyla adım adım rehber alın
2. **Kanal Tarama**: `!kanal-tara` ile mevcut kanalları görün
3. **Rol Kontrolü**: `!rol-kontrol` ile eksik rolleri tespit edin
4. **Kanal Kontrolü**: `!kanal-kontrol` ile eksik kanalları tespit edin
5. **Oyun Analizi**: `!mevcut-oyunlar` ile mevcut oyun kanallarını analiz edin

### Manuel Entegrasyon

#### 1. Rolleri Oluşturma
Eksik rolleri manuel olarak oluşturun:
- Minecraft
- LoL
- Valorant
- CS2
- Fortnite
- GTA
- RocketLeague
- AmongUs

#### 2. Kanal Eşleştirme
`games_config.json` dosyasındaki kanal isimlerini mevcut kanallarınızla eşleştirin:

```json
{
    "games": {
        "Minecraft": {
            "role": "Minecraft",
            "text_channels": ["mevcut-minecraft-chat", "mevcut-minecraft-tips"],
            "voice_channels": ["mevcut-minecraft-voice", "mevcut-minecraft-survival"]
        }
    }
}
```

#### 3. Yeni Oyun Ekleme
Mevcut oyun kanallarınızı bot'a eklemek için:

```bash
!oyun-ekle "Oyun Adı" "Rol Adı" text:mevcut-kanal1 text:mevcut-kanal2 voice:mevcut-ses1 voice:mevcut-ses2
```

Örnek:
```bash
!oyun-ekle "Apex Legends" "Apex" text:apex-chat text:apex-tips voice:apex-voice voice:apex-ranked
```

## ⚙️ Yapılandırma

### Oyun Ekleme
```bash
!oyun-ekle "Oyun Adı" "Rol Adı" text:kanal1 text:kanal2 voice:ses1 voice:ses2
```

### JSON Yapılandırması
`games_config.json` dosyasını düzenleyerek oyunları yönetebilirsiniz:

```json
{
    "games": {
        "Oyun Adı": {
            "role": "Rol Adı",
            "text_channels": ["kanal1", "kanal2"],
            "voice_channels": ["ses1", "ses2"],
            "color": "0xHEXCODE",
            "emoji": "🎮"
        }
    }
}
```

## 🔧 Özelleştirme

### Yeni Oyun Ekleme
1. `games_config.json` dosyasını açın
2. Yeni oyun objesi ekleyin
3. Bot'u yeniden başlatın

### Ortak Alanları Değiştirme
`common_areas` bölümünü düzenleyin:
```json
"common_areas": {
    "text_channels": ["yeni-kanal1", "yeni-kanal2"],
    "voice_channels": ["yeni-ses1", "yeni-ses2"]
}
```

### Ayarları Değiştirme
`settings` bölümünü düzenleyin:
```json
"settings": {
    "welcome_message": "Özel hoş geldin mesajı",
    "timeout_seconds": 300,
    "max_games_per_user": 8
}
```

## 🎯 Kullanım Senaryosu

1. **Yeni Üye Katılır**: Bot otomatik DM gönderir
2. **Oyun Seçimi**: Dropdown menüden oyunlar seçilir
3. **Rol Verme**: Seçilen oyunlara göre roller verilir
4. **Kanal Erişimi**: İlgili kanallara erişim sağlanır
5. **Ortak Alanlar**: Tüm üyeler genel kanallara erişebilir

## 🛠️ Geliştirme

### Dosya Yapısı
```
Decipula/
├── bot.py              # Ana bot kodu
├── games_config.json   # Oyun yapılandırması
└── README.md          # Bu dosya
```

### Katkıda Bulunma
1. Fork yapın
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin

## 📞 Destek

Sorunlarınız için:
- GitHub Issues kullanın
- Discord sunucusuna katılın
- Dokümantasyonu kontrol edin

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

=======
# 🎮 DECIPULA Discord Bot

Discord sunucusu için oyun rol sistemi botu.

## ✨ Özellikler

- 🎮 Yeni üyelere otomatik oyun seçim menüsü
- 🏷️ Oyun rolleri ve kanal erişimi
- ⚙️ Admin komutları
- 🌐 Sunucu entegrasyon araçları

## 🎮 Desteklenen Oyunlar

| Oyun | Rol | Metin Kanalları | Ses Kanalları |
|------|-----|-----------------|---------------|
| Minecraft | Minecraft | minecraft-chat, minecraft-tips, minecraft-builds | minecraft-voice, minecraft-survival, minecraft-creative |
| League of Legends | LoL | lol-chat, lol-strategy, lol-meta | lol-voice, lol-ranked, lol-normals |
| Valorant | Valorant | valorant-chat, valorant-tips, valorant-lineups | valorant-voice, valorant-ranked, valorant-unrated |
| CS2 | CS2 | cs2-chat, cs2-strategy, cs2-maps | cs2-voice, cs2-competitive, cs2-casual |
| Fortnite | Fortnite | fortnite-chat, fortnite-builds, fortnite-events | fortnite-voice, fortnite-arena, fortnite-pubs |
| GTA V | GTA | gta-chat, gta-missions, gta-roleplay | gta-voice, gta-heists, gta-freemode |
| Rocket League | RocketLeague | rl-chat, rl-tips, rl-trading | rl-voice, rl-ranked, rl-casual |
| Among Us | AmongUs | amongus-chat, amongus-strategy | amongus-voice, amongus-lobby |

## 🌐 Ortak Alanlar

**Metin Kanalları:** genel-sohbet, duyurular, yardım, memes, anime-manga, teknoloji, spor

**Ses Kanalları:** genel-ses, müzik, afk, toplantı, çalışma-odası

## 🚀 Kurulum

1. Discord Developer Portal'dan bot oluşturun
2. Bot token'ını alın
3. Railway'e deploy edin

## 📋 Komutlar

### Kullanıcı Komutları
- `!oyunlar` - Desteklenen oyunları listeler
- `!rollerim` - Sahip olduğun rolleri gösterir
- `!yardım` - Tüm komutları gösterir

### Admin Komutları
- `!oyun-ekle` - Yeni oyun ekler
- `!oyun-sil` - Oyun siler
- `!yapılandırma` - Bot ayarlarını gösterir

## 🔧 Mevcut Sunucu Entegrasyonu

### Otomatik Kurulum
Bot'u mevcut sunucunuza ekledikten sonra:

1. **Kurulum Rehberi**: `!sunucu-ayarla` komutuyla adım adım rehber alın
2. **Kanal Tarama**: `!kanal-tara` ile mevcut kanalları görün
3. **Rol Kontrolü**: `!rol-kontrol` ile eksik rolleri tespit edin
4. **Kanal Kontrolü**: `!kanal-kontrol` ile eksik kanalları tespit edin
5. **Oyun Analizi**: `!mevcut-oyunlar` ile mevcut oyun kanallarını analiz edin

### Manuel Entegrasyon

#### 1. Rolleri Oluşturma
Eksik rolleri manuel olarak oluşturun:
- Minecraft
- LoL
- Valorant
- CS2
- Fortnite
- GTA
- RocketLeague
- AmongUs

#### 2. Kanal Eşleştirme
`games_config.json` dosyasındaki kanal isimlerini mevcut kanallarınızla eşleştirin:

```json
{
    "games": {
        "Minecraft": {
            "role": "Minecraft",
            "text_channels": ["mevcut-minecraft-chat", "mevcut-minecraft-tips"],
            "voice_channels": ["mevcut-minecraft-voice", "mevcut-minecraft-survival"]
        }
    }
}
```

#### 3. Yeni Oyun Ekleme
Mevcut oyun kanallarınızı bot'a eklemek için:

```bash
!oyun-ekle "Oyun Adı" "Rol Adı" text:mevcut-kanal1 text:mevcut-kanal2 voice:mevcut-ses1 voice:mevcut-ses2
```

Örnek:
```bash
!oyun-ekle "Apex Legends" "Apex" text:apex-chat text:apex-tips voice:apex-voice voice:apex-ranked
```

## ⚙️ Yapılandırma

### Oyun Ekleme
```bash
!oyun-ekle "Oyun Adı" "Rol Adı" text:kanal1 text:kanal2 voice:ses1 voice:ses2
```

### JSON Yapılandırması
`games_config.json` dosyasını düzenleyerek oyunları yönetebilirsiniz:

```json
{
    "games": {
        "Oyun Adı": {
            "role": "Rol Adı",
            "text_channels": ["kanal1", "kanal2"],
            "voice_channels": ["ses1", "ses2"],
            "color": "0xHEXCODE",
            "emoji": "🎮"
        }
    }
}
```

## 🔧 Özelleştirme

### Yeni Oyun Ekleme
1. `games_config.json` dosyasını açın
2. Yeni oyun objesi ekleyin
3. Bot'u yeniden başlatın

### Ortak Alanları Değiştirme
`common_areas` bölümünü düzenleyin:
```json
"common_areas": {
    "text_channels": ["yeni-kanal1", "yeni-kanal2"],
    "voice_channels": ["yeni-ses1", "yeni-ses2"]
}
```

### Ayarları Değiştirme
`settings` bölümünü düzenleyin:
```json
"settings": {
    "welcome_message": "Özel hoş geldin mesajı",
    "timeout_seconds": 300,
    "max_games_per_user": 8
}
```

## 🎯 Kullanım Senaryosu

1. **Yeni Üye Katılır**: Bot otomatik DM gönderir
2. **Oyun Seçimi**: Dropdown menüden oyunlar seçilir
3. **Rol Verme**: Seçilen oyunlara göre roller verilir
4. **Kanal Erişimi**: İlgili kanallara erişim sağlanır
5. **Ortak Alanlar**: Tüm üyeler genel kanallara erişebilir

## 🛠️ Geliştirme

### Dosya Yapısı
```
Decipula/
├── bot.py              # Ana bot kodu
├── games_config.json   # Oyun yapılandırması
└── README.md          # Bu dosya
```

### Katkıda Bulunma
1. Fork yapın
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin

## 📞 Destek

Sorunlarınız için:
- GitHub Issues kullanın
- Discord sunucusuna katılın
- Dokümantasyonu kontrol edin

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

>>>>>>> 62795702bea0000428067584174e9854641093ed
**🎮 DECIPULA BOT** - Oyun toplulukları için geliştirilmiş Discord botu 