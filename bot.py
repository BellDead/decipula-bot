import discord
from discord.ext import commands
from discord.ui import Select, View
import json
import os
import ssl
import certifi

# SSL sertifika sorununu çözmek için
ssl_context = ssl.create_default_context(cafile=certifi.where())

intents = discord.Intents.all()  
bot = commands.Bot(command_prefix="!", intents=intents)

def load_config():
    """JSON dosyasından yapılandırmayı yükler"""
    try:
        with open('games_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ games_config.json dosyası bulunamadı!")
        return None

def save_config(config):
    """Yapılandırmayı JSON dosyasına kaydeder"""
    try:
        with open('games_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Yapılandırma kaydedilemedi: {e}")
        return False

def load_token():
    """Token'ı güvenli bir şekilde yükler"""
    # Önce environment variable'dan dene
    token = os.getenv('DISCORD_TOKEN')
    if token:
        return token
    
    # Sonra token.txt dosyasından dene
    try:
        with open('token.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and line != 'YOUR_BOT_TOKEN_HERE':
                    return line
    except FileNotFoundError:
        pass
    
    return None

# Yapılandırmayı yükle
config = load_config()
if config:
    games_config = config["games"]
    common_areas = config["common_areas"]
    settings = config["settings"]
else:
    # Varsayılan yapılandırma
    games_config = {}
    common_areas = {"text_channels": [], "voice_channels": []}
    settings = {"welcome_message": "Hoş geldin!", "timeout_seconds": 300}

# Kullanıcı tercihlerini saklamak için
user_preferences = {}

# Konsol loglarını saklamak için bir liste
console_logs = []

# Konsola yazılan her mesajı da bu listeye ekleyecek yardımcı fonksiyon
def log_console(msg):
    print(msg)
    console_logs.append(msg)
    if len(console_logs) > 20:
        console_logs.pop(0)

@bot.event
async def on_ready():
    print(f"🎮 DECIPULA BOT aktif: {bot.user}")
    print(f"📊 {len(games_config)} oyun destekleniyor")
    print(f"🌐 {len(common_areas['text_channels'])} ortak metin kanalı")
    print(f"🔊 {len(common_areas['voice_channels'])} ortak ses kanalı")

@bot.event
async def on_member_join(member):
    """
    Sunucuya yeni birisi katıldığında, kullanıcıya DM'den hoş geldin ve rol-alma kanalına yönlendirme mesajı gönderilecek.
    """
    try:
        await member.send("Merhaba, Decipula'ya hoş geldin! Rollerini almak için #rol-alma kanalına gidebilirsin.")
    except Exception as e:
        print(f"❌ {member.name} kullanıcısına DM gönderilemedi. Hata: {e}")

class GameSelect(discord.ui.Select):
    def __init__(self, member):
        """
        Çoklu seçim dropdown menüsü
        """
        self.member = member
        options = []
        
        for name, game_info in games_config.items():
            emoji = game_info.get("emoji", "🎮")
            text_count = len(game_info["text_channels"])
            voice_count = len(game_info["voice_channels"])
            
            options.append(
                discord.SelectOption(
                    label=name, 
                    description=f"{text_count} metin, {voice_count} ses kanalı",
                    emoji=emoji
                )
            )
        
        max_values = min(len(games_config), settings.get("max_games_per_user", 8))
        
        super().__init__(
            placeholder="Oynamak istediğin oyunları seç... (Birden fazla seçebilirsin)",
            options=options,
            min_values=1,
            max_values=max_values
        )
    
    async def callback(self, interaction):
        selected_games = self.values
        guild = interaction.guild
        member = interaction.user
        if guild and not isinstance(member, discord.Member):
            member = guild.get_member(interaction.user.id)
        if not member or not isinstance(member, discord.Member):
            await interaction.response.send_message("❌ Kullanıcı bulunamadı, lütfen tekrar deneyin.", ephemeral=True)
            return
        
        # DM'den gelen istekleri kontrol et
        if not guild:
            user_preferences[self.member.id] = selected_games
            
            # DM'den gelen istek için özel mesaj
            embed = discord.Embed(
                title="🎮 Oyun Seçiminiz Alındı!",
                description="Seçtiğiniz oyunlar sunucuya katıldığınızda otomatik olarak verilecektir.",
                color=0x00FF00
            )
            
            embed.add_field(
                name="✅ Seçtiğiniz Oyunlar:",
                value="\n".join([f"• {game}" for game in selected_games]),
                inline=False
            )
            
            embed.add_field(
                name="📋 Sonraki Adımlar:",
                value="1. Sunucuya katılın\n2. Roller otomatik olarak verilecek\n3. İlgili kanallara erişim kazanacaksınız",
                inline=False
            )
            
            embed.add_field(
                name="🌐 Ortak Alanlar:",
                value="Tüm üyeler genel sohbet, duyurular, yardım kanallarına erişebilir.",
                inline=False
            )
            
            embed.set_footer(text="Sunucuya katıldığınızda rolleriniz otomatik olarak verilecektir!")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Sunucudan gelen istekler için normal işlem
        # Seçilen oyunlara göre roller ver
        roles_added = []
        for game_name in selected_games:
            if game_name in games_config:
                game_info = games_config[game_name]
                role = discord.utils.get(guild.roles, name=game_info["role"])
                log_console(f"Rol arandı: {game_info['role']} - Bulundu mu: {bool(role)}")
                if role and role not in member.roles:
                    try:
                        await member.add_roles(role)
                        log_console(f"Rol verildi: {role.name} -> {member.name}")
                        roles_added.append(game_name)
                    except Exception as e:
                        log_console(f"Rol verilemedi: {role.name} -> {member.name} | Hata: {e}")
                else:
                    log_console(f"Rol zaten var veya bulunamadı: {game_info['role']} -> {member.name}")
        
        # Başarı mesajı oluştur
        embed = discord.Embed(
            title="✅ Roller Başarıyla Verildi!",
            color=0x00FF00
        )
        
        if roles_added:
            embed.add_field(
                name="🎮 Erişim Kazandığın Oyunlar:",
                value="\n".join([f"• {game}" for game in roles_added]),
                inline=False
            )
        
        # Kanal bilgilerini ekle
        channel_info = []
        for game_name in selected_games:
            if game_name in games_config:
                game_info = games_config[game_name]
                text_channels = ", ".join(game_info["text_channels"])
                voice_channels = ", ".join(game_info["voice_channels"])
                channel_info.append(f"**{game_name}:**\n📝 {text_channels}\n🔊 {voice_channels}")
        
        if channel_info:
            embed.add_field(
                name="📋 Erişim Kazandığın Kanallar:",
                value="\n\n".join(channel_info),
                inline=False
            )
        
        embed.add_field(
            name="🌐 Ortak Alanlar:",
            value="Tüm üyeler genel sohbet, duyurular, yardım kanallarına erişebilir.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class GameSelectView(discord.ui.View):
    def __init__(self, member):
        timeout = 900  # 15 dakika
        super().__init__(timeout=timeout)
        self.add_item(GameSelect(member))

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Select):
                item.disabled = True

# Kullanıcı komutları
@bot.command(name="oyunlar")
async def list_games(ctx):
    """Desteklenen oyunları listeler"""
    embed = discord.Embed(
        title="🎮 Desteklenen Oyunlar",
        description="Sunucumuzda desteklenen oyunlar ve kanalları:",
        color=0x7289DA
    )
    
    for game_name, game_info in games_config.items():
        emoji = game_info.get("emoji", "🎮")
        text_channels = ", ".join(game_info["text_channels"])
        voice_channels = ", ".join(game_info["voice_channels"])
        
        embed.add_field(
            name=f"{emoji} {game_name}",
            value=f"**Metin Kanalları:** {text_channels}\n**Ses Kanalları:** {voice_channels}",
            inline=False
        )
    
    embed.add_field(
        name="🌐 Ortak Alanlar",
        value=f"**Metin:** {', '.join(common_areas['text_channels'])}\n**Ses:** {', '.join(common_areas['voice_channels'])}",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="rollerim")
async def my_roles(ctx):
    """Kullanıcının rollerini gösterir"""
    user_roles = []
    for role in ctx.author.roles:
        for game_info in games_config.values():
            if role.name == game_info["role"]:
                user_roles.append(role.name)
                break
    
    if user_roles:
        embed = discord.Embed(
            title="🎮 Oyun Rollerin",
            description=f"**{ctx.author.name}** için aktif oyun rolleri:",
            color=0x00FF00
        )
        embed.add_field(name="Roller:", value="\n".join([f"• {role}" for role in user_roles]), inline=False)
    else:
        embed = discord.Embed(
            title="❌ Oyun Rolü Yok",
            description="Henüz hiçbir oyun rolüne sahip değilsin. DM'den oyun seçimi yapabilirsin!",
            color=0xFF0000
        )
    
    await ctx.send(embed=embed)

@bot.command(name="yardım")
async def help_command(ctx):
    """Bot komutlarını gösterir"""
    embed = discord.Embed(
        title="🤖 DECIPULA BOT Komutları",
        description="Kullanabileceğin komutlar:",
        color=0x7289DA
    )
    
    commands_info = [
        ("!oyunlar", "Desteklenen oyunları ve kanalları listeler"),
        ("!rollerim", "Sahip olduğun oyun rollerini gösterir"),
        ("!yardım", "Bu yardım mesajını gösterir"),
        ("!ortak-alanlar", "Ortak alanları listeler")
    ]
    
    # Admin komutları varsa ekle
    if ctx.author.guild_permissions.administrator:
        commands_info.extend([
            ("!oyun-ekle", "Yeni oyun ekler (Admin)"),
            ("!oyun-sil", "Oyun siler (Admin)"),
            ("!yapılandırma", "Mevcut yapılandırmayı gösterir (Admin)"),
            ("!kanal-tara", "Mevcut kanalları tarar (Admin)"),
            ("!rol-kontrol", "Gerekli rolleri kontrol eder (Admin)"),
            ("!kanal-kontrol", "Gerekli kanalları kontrol eder (Admin)"),
            ("!sunucu-ayarla", "Kurulum rehberi gösterir (Admin)"),
            ("!mevcut-oyunlar", "Mevcut oyun kanallarını analiz eder (Admin)"),
            ("!ortak-alanlar-kontrol", "Ortak alanların mevcut olup olmadığını kontrol eder (Admin)"),
            ("!ortak-alanlar-güncelle", "Ortak alanları günceller (Admin)"),
            ("!rolmenusu", "Rol seçme menüsünü gönderir (Admin)"),
            ("!yuklu-komutlar", "Yüklü komutları listeler"),
            ("!konsol-kontrol", "Son 20 konsol logu gösterir (Admin)")
        ])
    
    for cmd, desc in commands_info:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.add_field(
        name="📝 Not",
        value="Yeni üyeler otomatik olarak DM alır ve oyun seçimi yapabilir.",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="ortak-alanlar")
async def list_common_areas(ctx):
    """Ortak alanları listeler"""
    embed = discord.Embed(
        title="🌐 Ortak Alanlar",
        description="Tüm üyeler tarafından erişilebilir kanallar:",
        color=0x7289DA
    )
    
    text_channels = ", ".join(common_areas["text_channels"])
    voice_channels = ", ".join(common_areas["voice_channels"])
    
    embed.add_field(
        name="📝 Metin Kanalları",
        value=text_channels if text_channels else "Yok",
        inline=False
    )
    
    embed.add_field(
        name="🔊 Ses Kanalları",
        value=voice_channels if voice_channels else "Yok",
        inline=False
    )
    
    embed.add_field(
        name="💡 Bilgi",
        value="Bu kanallar tüm üyeler tarafından kullanılabilir. Oyun rolleri olmayan üyeler de erişebilir.",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Admin komutları
@bot.command(name="oyun-ekle")
@commands.has_permissions(administrator=True)
async def add_game(ctx, game_name: str, role_name: str, *, channels: str):
    """Yeni oyun ekler (Admin)"""
    try:
        # Kanal listesini parse et
        channel_parts = channels.split()
        text_channels = []
        voice_channels = []
        
        for part in channel_parts:
            if part.startswith("text:"):
                text_channels.append(part[5:])
            elif part.startswith("voice:"):
                voice_channels.append(part[6:])
        
        # Yeni oyun ekle
        games_config[game_name] = {
            "role": role_name,
            "text_channels": text_channels,
            "voice_channels": voice_channels,
            "color": "0x7289DA",
            "emoji": "🎮"
        }
        
        # JSON dosyasını güncelle
        if config:
            config["games"] = games_config
            if save_config(config):
                embed = discord.Embed(
                    title="✅ Oyun Eklendi!",
                    description=f"**{game_name}** başarıyla eklendi.",
                    color=0x00FF00
                )
                embed.add_field(name="Rol", value=role_name, inline=True)
                embed.add_field(name="Metin Kanalları", value=", ".join(text_channels) if text_channels else "Yok", inline=True)
                embed.add_field(name="Ses Kanalları", value=", ".join(voice_channels) if voice_channels else "Yok", inline=True)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Oyun eklenirken hata oluştu!")
        else:
            await ctx.send("❌ Yapılandırma dosyası yüklenemedi!")
            
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}\n\nKullanım: `!oyun-ekle \"Oyun Adı\" \"Rol Adı\" text:kanal1 text:kanal2 voice:ses1 voice:ses2`")

@bot.command(name="oyun-sil")
@commands.has_permissions(administrator=True)
async def remove_game(ctx, game_name: str):
    """Oyun siler (Admin)"""
    if game_name in games_config:
        del games_config[game_name]
        
        if config:
            config["games"] = games_config
            
            if save_config(config):
                embed = discord.Embed(
                    title="✅ Oyun Silindi!",
                    description=f"**{game_name}** başarıyla silindi.",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Oyun silinirken hata oluştu!")
        else:
            await ctx.send("❌ Yapılandırma dosyası yüklenemedi!")
    else:
        await ctx.send(f"❌ **{game_name}** oyunu bulunamadı!")

@bot.command(name="yapılandırma")
@commands.has_permissions(administrator=True)
async def show_config(ctx):
    """Mevcut yapılandırmayı gösterir (Admin)"""
    embed = discord.Embed(
        title="⚙️ Bot Yapılandırması",
        color=0x7289DA
    )
    
    embed.add_field(
        name="🎮 Oyunlar",
        value=f"Toplam: {len(games_config)} oyun",
        inline=True
    )
    
    embed.add_field(
        name="🌐 Ortak Alanlar",
        value=f"Metin: {len(common_areas['text_channels'])}, Ses: {len(common_areas['voice_channels'])}",
        inline=True
    )
    
    embed.add_field(
        name="⏱️ Timeout",
        value=f"{settings.get('timeout_seconds', 300)} saniye",
        inline=True
    )
    
    await ctx.send(embed=embed)

# Sunucu entegrasyon komutları
@bot.command(name="kanal-tara")
@commands.has_permissions(administrator=True)
async def scan_channels(ctx):
    """Mevcut sunucudaki kanalları tarar ve listeler"""
    guild = ctx.guild
    
    embed = discord.Embed(
        title="🔍 Sunucu Kanal Taraması",
        description=f"**{guild.name}** sunucusundaki mevcut kanallar:",
        color=0x7289DA
    )
    
    # Metin kanalları
    text_channels = [channel.name for channel in guild.text_channels]
    embed.add_field(
        name=f"📝 Metin Kanalları ({len(text_channels)})",
        value=", ".join(text_channels[:20]) + ("..." if len(text_channels) > 20 else ""),
        inline=False
    )
    
    # Ses kanalları
    voice_channels = [channel.name for channel in guild.voice_channels]
    embed.add_field(
        name=f"🔊 Ses Kanalları ({len(voice_channels)})",
        value=", ".join(voice_channels[:20]) + ("..." if len(voice_channels) > 20 else ""),
        inline=False
    )
    
    # Roller
    roles = [role.name for role in guild.roles if not role.managed and role.name != "@everyone"]
    embed.add_field(
        name=f"👥 Roller ({len(roles)})",
        value=", ".join(roles[:15]) + ("..." if len(roles) > 15 else ""),
        inline=False
    )
    
    embed.add_field(
        name="💡 Öneri",
        value="Bu kanalları `games_config.json` dosyasına ekleyebilir veya `!oyun-ekle` komutuyla yeni oyunlar oluşturabilirsiniz.",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="rol-kontrol")
@commands.has_permissions(administrator=True)
async def check_roles(ctx):
    """Bot için gerekli rollerin mevcut olup olmadığını kontrol eder"""
    guild = ctx.guild
    missing_roles = []
    existing_roles = []
    
    for game_name, game_info in games_config.items():
        role_name = game_info["role"]
        role = discord.utils.get(guild.roles, name=role_name)
        
        if role:
            existing_roles.append(f"✅ {game_name} ({role_name})")
        else:
            missing_roles.append(f"❌ {game_name} ({role_name})")
    
    embed = discord.Embed(
        title="🔍 Rol Kontrolü",
        description=f"**{guild.name}** sunucusundaki oyun rolleri:",
        color=0x7289DA
    )
    
    if existing_roles:
        embed.add_field(
            name="✅ Mevcut Roller",
            value="\n".join(existing_roles),
            inline=False
        )
    
    if missing_roles:
        embed.add_field(
            name="❌ Eksik Roller",
            value="\n".join(missing_roles),
            inline=False
        )
        embed.add_field(
            name="🛠️ Çözüm",
            value="Eksik rolleri manuel olarak oluşturmanız gerekiyor. Roller oluşturulduktan sonra bot otomatik olarak kullanacaktır.",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name="kanal-kontrol")
@commands.has_permissions(administrator=True)
async def check_channels(ctx):
    """Bot için gerekli kanalların mevcut olup olmadığını kontrol eder"""
    guild = ctx.guild
    missing_channels = []
    existing_channels = []
    
    for game_name, game_info in games_config.items():
        # Metin kanalları kontrolü
        for channel_name in game_info["text_channels"]:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                existing_channels.append(f"✅ {game_name} - {channel_name} (metin)")
            else:
                missing_channels.append(f"❌ {game_name} - {channel_name} (metin)")
        
        # Ses kanalları kontrolü
        for channel_name in game_info["voice_channels"]:
            channel = discord.utils.get(guild.voice_channels, name=channel_name)
            if channel:
                existing_channels.append(f"✅ {game_name} - {channel_name} (ses)")
            else:
                missing_channels.append(f"❌ {game_name} - {channel_name} (ses)")
    
    embed = discord.Embed(
        title="🔍 Kanal Kontrolü",
        description=f"**{guild.name}** sunucusundaki oyun kanalları:",
        color=0x7289DA
    )
    
    if existing_channels:
        embed.add_field(
            name="✅ Mevcut Kanallar",
            value="\n".join(existing_channels[:15]) + ("..." if len(existing_channels) > 15 else ""),
            inline=False
        )
    
    if missing_channels:
        embed.add_field(
            name="❌ Eksik Kanallar",
            value="\n".join(missing_channels[:15]) + ("..." if len(missing_channels) > 15 else ""),
            inline=False
        )
        embed.add_field(
            name="🛠️ Çözüm",
            value="Eksik kanalları manuel olarak oluşturmanız veya `games_config.json` dosyasındaki kanal isimlerini mevcut kanallarla eşleştirmeniz gerekiyor.",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name="sunucu-ayarla")
@commands.has_permissions(administrator=True)
async def setup_server(ctx):
    """Sunucu kurulum rehberi gösterir"""
    embed = discord.Embed(
        title="🛠️ Sunucu Kurulum Rehberi",
        description="DECIPULA BOT'u mevcut sunucunuzla entegre etmek için:",
        color=0x7289DA
    )
    
    steps = [
        "1️⃣ **Rol Kontrolü**: `!rol-kontrol` komutuyla eksik rolleri tespit edin",
        "2️⃣ **Kanal Kontrolü**: `!kanal-kontrol` komutuyla eksik kanalları tespit edin",
        "3️⃣ **Kanal Tarama**: `!kanal-tara` komutuyla mevcut kanalları görün",
        "4️⃣ **Rol Oluşturma**: Eksik rolleri manuel olarak oluşturun",
        "5️⃣ **Kanal Eşleştirme**: `games_config.json` dosyasındaki kanal isimlerini mevcut kanallarla eşleştirin",
        "6️⃣ **Test**: Yeni bir üye davet ederek sistemi test edin"
    ]
    
    for step in steps:
        embed.add_field(name="", value=step, inline=False)
    
    embed.add_field(
        name="💡 İpucu",
        value="Mevcut kanallarınızı korumak için `games_config.json` dosyasını düzenleyerek kanal isimlerini değiştirebilirsiniz.",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="mevcut-oyunlar")
@commands.has_permissions(administrator=True)
async def list_existing_games(ctx):
    """Mevcut sunucudaki oyun kanallarını analiz eder"""
    guild = ctx.guild
    
    # Oyun isimlerini tespit etmeye çalış
    game_patterns = {
        "minecraft": ["minecraft", "mc"],
        "lol": ["lol", "league", "leagueoflegends"],
        "valorant": ["valorant", "val"],
        "cs2": ["cs2", "csgo", "counter-strike"],
        "fortnite": ["fortnite", "fn"],
        "gta": ["gta", "grandtheftauto"],
        "rocket": ["rocket", "rl"],
        "among": ["among", "amongus"]
    }
    
    detected_games = {}
    
    # Metin kanallarını analiz et
    for channel in guild.text_channels:
        channel_lower = channel.name.lower()
        for game, patterns in game_patterns.items():
            if any(pattern in channel_lower for pattern in patterns):
                if game not in detected_games:
                    detected_games[game] = {"text": [], "voice": []}
                detected_games[game]["text"].append(channel.name)
    
    # Ses kanallarını analiz et
    for channel in guild.voice_channels:
        channel_lower = channel.name.lower()
        for game, patterns in game_patterns.items():
            if any(pattern in channel_lower for pattern in patterns):
                if game not in detected_games:
                    detected_games[game] = {"text": [], "voice": []}
                detected_games[game]["voice"].append(channel.name)
    
    embed = discord.Embed(
        title="🎮 Tespit Edilen Oyunlar",
        description=f"**{guild.name}** sunucusunda tespit edilen oyun kanalları:",
        color=0x7289DA
    )
    
    if detected_games:
        for game, channels in detected_games.items():
            text_channels = ", ".join(channels["text"]) if channels["text"] else "Yok"
            voice_channels = ", ".join(channels["voice"]) if channels["voice"] else "Yok"
            
            embed.add_field(
                name=f"🎮 {game.title()}",
                value=f"**Metin:** {text_channels}\n**Ses:** {voice_channels}",
                inline=False
            )
    else:
        embed.add_field(
            name="❌ Oyun Tespit Edilemedi",
            value="Mevcut kanallarda standart oyun isimleri bulunamadı. Manuel olarak `!oyun-ekle` komutuyla ekleyebilirsiniz.",
            inline=False
        )
    
    embed.add_field(
        name="💡 Öneri",
        value="Bu tespit edilen oyunları `games_config.json` dosyasına ekleyebilir veya mevcut yapılandırmayı güncelleyebilirsiniz.",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="ortak-alanlar-kontrol")
@commands.has_permissions(administrator=True)
async def check_common_areas(ctx):
    """Ortak alanların mevcut olup olmadığını kontrol eder"""
    guild = ctx.guild
    missing_channels = []
    existing_channels = []
    
    # Metin kanalları kontrolü
    for channel_name in common_areas["text_channels"]:
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel:
            existing_channels.append(f"✅ {channel_name} (metin)")
        else:
            missing_channels.append(f"❌ {channel_name} (metin)")
    
    # Ses kanalları kontrolü
    for channel_name in common_areas["voice_channels"]:
        channel = discord.utils.get(guild.voice_channels, name=channel_name)
        if channel:
            existing_channels.append(f"✅ {channel_name} (ses)")
        else:
            missing_channels.append(f"❌ {channel_name} (ses)")
    
    embed = discord.Embed(
        title="🌐 Ortak Alanlar Kontrolü",
        description=f"**{guild.name}** sunucusundaki ortak alanlar:",
        color=0x7289DA
    )
    
    if existing_channels:
        embed.add_field(
            name="✅ Mevcut Kanallar",
            value="\n".join(existing_channels),
            inline=False
        )
    
    if missing_channels:
        embed.add_field(
            name="❌ Eksik Kanallar",
            value="\n".join(missing_channels),
            inline=False
        )
        embed.add_field(
            name="🛠️ Kurulum Rehberi",
            value="Eksik kanalları manuel olarak oluşturun veya `games_config.json` dosyasındaki kanal isimlerini mevcut kanallarla eşleştirin.",
            inline=False
        )
    
    embed.add_field(
        name="💡 Bilgi",
        value="Ortak alanlar tüm üyeler tarafından erişilebilir kanallardır. Oyun rolleri olmayan üyeler de bu kanalları kullanabilir.",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="ortak-alanlar-güncelle")
@commands.has_permissions(administrator=True)
async def update_common_areas(ctx, channel_type: str, *, channel_names: str):
    """Ortak alanları günceller (Admin)"""
    try:
        channel_list = [name.strip() for name in channel_names.split(",")]
        
        if channel_type.lower() in ["text", "metin", "txt"]:
            common_areas["text_channels"] = channel_list
            channel_type_display = "Metin Kanalları"
        elif channel_type.lower() in ["voice", "ses", "voice_channels"]:
            common_areas["voice_channels"] = channel_list
            channel_type_display = "Ses Kanalları"
        else:
            await ctx.send("❌ Geçersiz kanal tipi! 'text' veya 'voice' kullanın.")
            return
        
        # JSON dosyasını güncelle
        if config:
            config["common_areas"] = common_areas
            if save_config(config):
                embed = discord.Embed(
                    title="✅ Ortak Alanlar Güncellendi!",
                    description=f"**{channel_type_display}** başarıyla güncellendi.",
                    color=0x00FF00
                )
                embed.add_field(
                    name=f"📋 {channel_type_display}",
                    value="\n".join([f"• {name}" for name in channel_list]),
                    inline=False
                )
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Güncelleme sırasında hata oluştu!")
        else:
            await ctx.send("❌ Yapılandırma dosyası yüklenemedi!")
            
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}\n\nKullanım: `!ortak-alanlar-güncelle text genel-sohbet, duyurular, yardım`")

@bot.command(name="roller")
async def roller_command(ctx):
    # Sadece 'rol-alma' kanalında çalışsın
    if ctx.channel.name != "rol-alma":
        await ctx.send("❌ Bu komut sadece #rol-alma kanalında kullanılabilir.")
        return
    try:
        embed = discord.Embed(
            title="Hangi oyunları oynamak istersin?",
            description="Aşağıdaki menüden istediğin oyunları seçebilirsin. Seçtiğin oyunların rolleri otomatik olarak verilecektir.",
            color=0x7289DA
        )
        embed.set_footer(text="Birden fazla oyun seçebilirsin!")
        view = GameSelectView(ctx.author)
        await ctx.send(embed=embed, view=view)
    except Exception as e:
        print(f"❌ roller komutunda hata: {e}")

# Sunucu kanalında menüyü gönderen komut
def get_welcome_embed():
    embed = discord.Embed(
        title=settings.get("welcome_message", "🎮 DECIPULA Sunucusuna Hoş Geldin!"),
        description="Oynamak istediğin oyunları seç ve ilgili kanallara erişim kazan!",
        color=0x7289DA
    )
    embed.add_field(
        name="📋 Nasıl Çalışır?",
        value="1. Aşağıdaki menüden oyunları seç\n2. Seçtiğin oyunlara göre roller verilir\n3. İlgili kanallara erişim kazanırsın",
        inline=False
    )
    embed.add_field(
        name="🌐 Ortak Alanlar",
        value="Tüm üyeler genel sohbet, duyurular, yardım kanallarına erişebilir.",
        inline=False
    )
    embed.set_footer(text="Birden fazla oyun seçebilirsin!")
    return embed

@bot.command(name="yuklu-komutlar")
async def yuklu_komutlar(ctx):
    komutlar = [c.name for c in bot.commands]
    await ctx.send("Yüklü komutlar: " + ", ".join(komutlar))

# Konsol loglarını Discord'dan gösterecek komut
def format_logs():
    if not console_logs:
        return "Konsolda hiç log yok."
    return '\n'.join(console_logs[-20:])

@bot.command(name="konsol-kontrol")
@commands.has_permissions(administrator=True)
async def konsol_kontrol(ctx):
    await ctx.send(f"Son 20 konsol logu:\n```\n{format_logs()}\n```")

# Bot token'ını buraya ekleyin
try:
    print("🤖 Bot başlatılıyor...")
    print("📡 Discord sunucularına bağlanılıyor...")
    
    print("Çalışılan dizin:", os.getcwd())
    print("token.txt var mı:", os.path.exists('token.txt'))
    if os.path.exists('token.txt'):
        with open('token.txt', 'r', encoding='utf-8') as f:
            print("token.txt içeriği:", f.read())
    
    token = load_token()
    if not token:
        print("❌ Bot token'ı bulunamadı!")
        print("💡 Çözüm seçenekleri:")
        print("1. token.txt dosyasına token'ınızı ekleyin")
        print("2. Environment variable olarak DISCORD_TOKEN ekleyin")
        print("3. PowerShell'de: $env:DISCORD_TOKEN='your_token'")
        exit(1)
    
    print("Yüklü komutlar:", [c.name for c in bot.commands])
    bot.run(token)
except discord.LoginFailure:
    print("❌ Bot token'ı geçersiz! Lütfen doğru token'ı kullandığınızdan emin olun.")
except discord.HTTPException as e:
    print(f"❌ HTTP hatası: {e}")
    print("💡 Discord sunucularına erişim sorunu olabilir.")
except Exception as e:
    print(f"❌ Beklenmeyen hata: {e}")
    print("💡 Çözüm önerileri:")
    print("1. İnternet bağlantınızı kontrol edin")
    print("2. Bot token'ının doğru olduğundan emin olun")
    print("3. Discord sunucularının erişilebilir olduğunu kontrol edin")
    print("4. Proxy veya VPN kullanıyorsanız kapatmayı deneyin")
