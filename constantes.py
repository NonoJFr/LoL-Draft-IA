# constantes.py

# --- MAPPING ---
NAME_MAPPING = {
    "MonkeyKing": "Wukong",
    "Renata": "Renata Glasc"
}
def clean_name(name): return NAME_MAPPING.get(name, name)

# 1. LA LISTE DE TES JOUEURS (Celle qui apparait cochée par défaut)
USER_STARTER_POOL = {
    "TOP": ["TahmKench", "Ornn", "Garen", "DrMundo", "Shen", "Ambessa", "Malphite", "Sion", "Gnar", "Warwick", "Tryndamere", "Fiora"],
    "JUNGLE": ["Maokai", "Xin Zhao", "Talon", "Diana", "Elise", "Amumu", "Wukong", "Sejuani", "jarvanIV"],
    "MID": ["Orianna", "Azir", "Viktor", "Katarina", "Xerath", "Aurora", "Ryze", "Yone", "Ahri", "Leblanc", "Sylas", "Hwei", "Yasuo"],
    "ADC": ["Kaisa", "Ezreal", "Jinx", "Caitlyn", "Ashe", "Xayah", "Kalista", "Miss Fortune", "Smolder", "Aphelios", "Tristana","Zeri","Jhin","Ziggs"],
    "SUPPORT": ["Milio","Lulu", "Nami", "Leona", "Thresh", "Rakan", "Nautilus", "Braum", "Séraphine", "Blitzcrank", "Lux", "Zilean", "Brand", "Ashe", "Zyra" ]
}

# 2. LA LISTE DU JEU COMPLET (Pour l'option "Méta Globale")
GLOBAL_META_ROLES = {
    "TOP": ["Aatrox", "Akali", "Ambessa", "Camille", "ChoGath", "Darius", "DrMundo", "Fiora", "Gangplank", "Garen", "Gnar", "Gragas", "Gwen", "Irelia", "Jax", "Jayce", "Kayle", "Kennen", "Kled", "Ksante", "Malphite", "Mordekaiser", "Olaf", "Ornn", "Poppy", "Renekton", "Rumble", "Sett", "Shen", "Singed", "Sion", "TahmKench", "Teemo", "Tryndamere", "Urgot", "Vayne", "Volibear", "Yasuo", "Yone", "Yorick", "Zaahen"],
    "JUNGLE": ["Amumu", "Belveth", "Briar", "Diana", "Ekko", "Elise", "Fiddlesticks", "Gragas", "Graves", "Hecarim", "Ivern", "JarvanIV", "Karthus", "Kayn", "Kindred", "LeeSin", "Lillia", "Maokai", "Nidalee", "Nocturne", "Nunu", "Pantheon", "Poppy", "Rammus", "RekSai", "Rengar", "Sejuani", "Shaco", "Shyvana", "Skarner", "Taliyah", "Talon", "Trundle", "Vi", "Viego", "Volibear", "Warwick", "Wukong", "XinZhao", "Zac", "Zed"],
    "MID": ["Ahri", "Akali", "Anivia", "Annie", "AurelionSol", "Aurora", "Azir", "Cassiopeia", "Corki", "Diana", "Galio", "Hwei", "Irelia", "Jayce", "Kassadin", "Katarina", "Leblanc", "Lissandra", "Lux", "Malzahar", "Naafiri", "Neeko", "Orianna", "Qiyana", "Ryze", "Smolder", "Swain", "Sylas", "Syndra", "Taliyah", "Talon", "TwistedFate", "Veigar", "Vex", "Viktor", "Vladimir", "Xerath", "Yasuo", "Yone", "Zed", "Ziggs", "Zoe"],
    "ADC": ["Aphelios", "Ashe", "Caitlyn", "Draven", "Ezreal", "Jhin", "Jinx", "Kaisa", "Kalista", "KogMaw", "Lucian", "MissFortune", "Nilah", "Samira", "Sivir", "Smolder", "Tristana", "Twitch", "Varus", "Vayne", "Xayah", "Zeri", "Ziggs", "Corki"],
    "SUPPORT": ["Alistar", "Amumu", "Bard", "Blitzcrank", "Brand", "Braum", "Janna", "Karma", "Leona", "Lulu", "Lux", "Maokai", "Milio", "Morgana", "Nami", "Nautilus", "Neeko", "Pantheon", "Poppy", "Pyke", "Rakan", "Rell", "Renata Glasc", "Senna", "Seraphine", "Sona", "Soraka", "Swain", "TahmKench", "Taric", "Thresh", "Yuumi", "Zilean", "Zyra"]
}