import pandas as pd
import plotly.graph_objects as go

# ==============================================================================
# BASE DE DONNÉES STATS CHAMPIONS (0 à 10)
# ==============================================================================
# AD = Dégâts Physiques | AP = Magiques | Tank = Résistance | CC = Contrôle
# ==============================================================================
# BASE DE DONNÉES STATS CHAMPIONS (0 à 10)
# ==============================================================================
# AD = Physiques | AP = Magiques | Tank = Résistance | CC = Contrôle
# Range = Portée (0=Melee, 10=Artillerie) | Late = Monstre de fin de game (True/False)

ARCHETYPES = {
    # --- A ---
    "Aatrox":       {"AD": 9, "AP": 0, "Tank": 6, "CC": 4, "Range": 2, "Late": False},
    "Ahri":         {"AD": 1, "AP": 9, "Tank": 1, "CC": 5, "Range": 7, "Late": False},
    "Akali":        {"AD": 4, "AP": 9, "Tank": 2, "CC": 1, "Range": 2, "Late": True},
    "Akshan":       {"AD": 9, "AP": 1, "Tank": 1, "CC": 1, "Range": 6, "Late": False},
    "Alistar":      {"AD": 1, "AP": 2, "Tank": 10,"CC": 10,"Range": 1, "Late": False},
    "Ambessa":      {"AD": 9, "AP": 0, "Tank": 4, "CC": 4, "Range": 2, "Late": False},
    "Amumu":        {"AD": 1, "AP": 6, "Tank": 9, "CC": 9, "Range": 2, "Late": True},
    "Anivia":       {"AD": 0, "AP": 10,"Tank": 2, "CC": 8, "Range": 7, "Late": True},
    "Annie":        {"AD": 1, "AP": 9, "Tank": 2, "CC": 6, "Range": 6, "Late": False},
    "Aphelios":     {"AD": 10,"AP": 0, "Tank": 1, "CC": 3, "Range": 8, "Late": True},
    "Ashe":         {"AD": 8, "AP": 0, "Tank": 1, "CC": 8, "Range": 8, "Late": True},
    "AurelionSol":  {"AD": 0, "AP": 10,"Tank": 2, "CC": 5, "Range": 9, "Late": True},
    "Aurora":       {"AD": 1, "AP": 9, "Tank": 2, "CC": 5, "Range": 6, "Late": True},
    "Azir":         {"AD": 1, "AP": 10,"Tank": 1, "CC": 4, "Range": 8, "Late": True},

    # --- B ---
    "Bard":         {"AD": 2, "AP": 5, "Tank": 4, "CC": 7, "Range": 6, "Late": True},
    "Belveth":      {"AD": 9, "AP": 1, "Tank": 4, "CC": 4, "Range": 2, "Late": True},
    "Blitzcrank":   {"AD": 2, "AP": 3, "Tank": 7, "CC": 9, "Range": 1, "Late": False},
    "Brand":        {"AD": 0, "AP": 10,"Tank": 1, "CC": 3, "Range": 7, "Late": True},
    "Braum":        {"AD": 1, "AP": 2, "Tank": 10,"CC": 9, "Range": 1, "Late": True},
    "Briar":        {"AD": 9, "AP": 0, "Tank": 5, "CC": 5, "Range": 1, "Late": False},

    # --- C ---
    "Caitlyn":      {"AD": 10,"AP": 0, "Tank": 0, "CC": 2, "Range": 10,"Late": True},
    "Camille":      {"AD": 9, "AP": 0, "Tank": 5, "CC": 5, "Range": 1, "Late": True},
    "Cassiopeia":   {"AD": 0, "AP": 10,"Tank": 3, "CC": 6, "Range": 6, "Late": True},
    "ChoGath":      {"AD": 2, "AP": 5, "Tank": 10,"CC": 7, "Range": 2, "Late": True},
    "Corki":        {"AD": 6, "AP": 6, "Tank": 1, "CC": 1, "Range": 7, "Late": True},

    # --- D ---
    "Darius":       {"AD": 9, "AP": 0, "Tank": 6, "CC": 4, "Range": 1, "Late": False},
    "Diana":        {"AD": 1, "AP": 9, "Tank": 4, "CC": 4, "Range": 2, "Late": False},
    "DrMundo":      {"AD": 5, "AP": 1, "Tank": 10,"CC": 2, "Range": 1, "Late": True},
    "Draven":       {"AD": 10,"AP": 0, "Tank": 1, "CC": 2, "Range": 6, "Late": False},

    # --- E ---
    "Ekko":         {"AD": 2, "AP": 9, "Tank": 3, "CC": 5, "Range": 2, "Late": True},
    "Elise":        {"AD": 1, "AP": 9, "Tank": 2, "CC": 5, "Range": 6, "Late": False},
    "Evelynn":      {"AD": 1, "AP": 10,"Tank": 1, "CC": 3, "Range": 1, "Late": False},
    "Ezreal":       {"AD": 7, "AP": 3, "Tank": 1, "CC": 0, "Range": 9, "Late": False},

    # --- F ---
    "Fiddlesticks": {"AD": 0, "AP": 9, "Tank": 2, "CC": 7, "Range": 6, "Late": True},
    "Fiora":        {"AD": 10,"AP": 0, "Tank": 4, "CC": 2, "Range": 1, "Late": True},
    "Fizz":         {"AD": 2, "AP": 10,"Tank": 1, "CC": 3, "Range": 2, "Late": False},

    # --- G ---
    "Galio":        {"AD": 1, "AP": 7, "Tank": 8, "CC": 8, "Range": 2, "Late": False},
    "Gangplank":    {"AD": 9, "AP": 2, "Tank": 3, "CC": 3, "Range": 2, "Late": True},
    "Garen":        {"AD": 7, "AP": 0, "Tank": 8, "CC": 1, "Range": 1, "Late": False},
    "Gnar":         {"AD": 6, "AP": 1, "Tank": 7, "CC": 7, "Range": 6, "Late": False},
    "Gragas":       {"AD": 1, "AP": 8, "Tank": 6, "CC": 7, "Range": 4, "Late": False},
    "Graves":       {"AD": 9, "AP": 0, "Tank": 4, "CC": 2, "Range": 5, "Late": True},
    "Gwen":         {"AD": 1, "AP": 10,"Tank": 4, "CC": 1, "Range": 2, "Late": True},

    # --- H ---
    "Hecarim":      {"AD": 8, "AP": 1, "Tank": 5, "CC": 4, "Range": 1, "Late": False},
    "Heimerdinger": {"AD": 0, "AP": 10,"Tank": 2, "CC": 5, "Range": 7, "Late": False},
    "Hwei":         {"AD": 0, "AP": 10,"Tank": 1, "CC": 6, "Range": 10,"Late": True},

    # --- I ---
    "Illaoi":       {"AD": 9, "AP": 0, "Tank": 6, "CC": 1, "Range": 2, "Late": False},
    "Irelia":       {"AD": 8, "AP": 2, "Tank": 5, "CC": 4, "Range": 2, "Late": False},
    "Ivern":        {"AD": 1, "AP": 5, "Tank": 3, "CC": 7, "Range": 5, "Late": False},

    # --- J ---
    "Janna":        {"AD": 0, "AP": 6, "Tank": 1, "CC": 8, "Range": 6, "Late": False},
    "JarvanIV":     {"AD": 7, "AP": 0, "Tank": 6, "CC": 7, "Range": 2, "Late": False},
    "Jax":          {"AD": 7, "AP": 4, "Tank": 6, "CC": 3, "Range": 1, "Late": True},
    "Jayce":        {"AD": 9, "AP": 0, "Tank": 2, "CC": 2, "Range": 8, "Late": False},
    "Jhin":         {"AD": 10,"AP": 0, "Tank": 0, "CC": 2, "Range": 9, "Late": True},
    "Jinx":         {"AD": 10,"AP": 0, "Tank": 0, "CC": 2, "Range": 9, "Late": True},

    # --- K ---
    "Kaisa":        {"AD": 6, "AP": 6, "Tank": 1, "CC": 1, "Range": 5, "Late": True},
    "Kalista":      {"AD": 9, "AP": 0, "Tank": 1, "CC": 3, "Range": 5, "Late": False},
    "Karma":        {"AD": 0, "AP": 8, "Tank": 2, "CC": 5, "Range": 6, "Late": False},
    "Karthus":      {"AD": 0, "AP": 10,"Tank": 1, "CC": 1, "Range": 8, "Late": True},
    "Kassadin":     {"AD": 1, "AP": 10,"Tank": 3, "CC": 2, "Range": 2, "Late": True},
    "Katarina":     {"AD": 4, "AP": 9, "Tank": 1, "CC": 0, "Range": 2, "Late": True},
    "Kayle":        {"AD": 6, "AP": 8, "Tank": 2, "CC": 2, "Range": 7, "Late": True},
    "Kayn":         {"AD": 9, "AP": 0, "Tank": 4, "CC": 2, "Range": 1, "Late": True},
    "Kennen":       {"AD": 2, "AP": 9, "Tank": 2, "CC": 7, "Range": 6, "Late": False},
    "KhaZix":       {"AD": 10,"AP": 0, "Tank": 1, "CC": 2, "Range": 1, "Late": False},
    "Kindred":      {"AD": 9, "AP": 0, "Tank": 1, "CC": 2, "Range": 7, "Late": True},
    "Kled":         {"AD": 8, "AP": 0, "Tank": 7, "CC": 2, "Range": 1, "Late": False},
    "KogMaw":       {"AD": 5, "AP": 7, "Tank": 1, "CC": 2, "Range": 10,"Late": True},
    "Ksante":       {"AD": 5, "AP": 0, "Tank": 8, "CC": 8, "Range": 2, "Late": False},

    # --- L ---
    "Leblanc":      {"AD": 1, "AP": 10,"Tank": 1, "CC": 3, "Range": 6, "Late": False},
    "LeeSin":       {"AD": 8, "AP": 1, "Tank": 4, "CC": 5, "Range": 1, "Late": False},
    "Leona":        {"AD": 1, "AP": 2, "Tank": 10,"CC": 10,"Range": 1, "Late": False},
    "Lillia":       {"AD": 0, "AP": 9, "Tank": 3, "CC": 4, "Range": 3, "Late": True},
    "Lissandra":    {"AD": 0, "AP": 8, "Tank": 3, "CC": 9, "Range": 5, "Late": False},
    "Lucian":       {"AD": 9, "AP": 1, "Tank": 1, "CC": 0, "Range": 5, "Late": False},
    "Lulu":         {"AD": 1, "AP": 6, "Tank": 1, "CC": 7, "Range": 6, "Late": True},
    "Lux":          {"AD": 0, "AP": 10,"Tank": 1, "CC": 5, "Range": 9, "Late": False},

    # --- M ---
    "Malphite":     {"AD": 2, "AP": 5, "Tank": 10,"CC": 9, "Range": 1, "Late": True},
    "Malzahar":     {"AD": 0, "AP": 9, "Tank": 1, "CC": 8, "Range": 6, "Late": False},
    "Maokai":       {"AD": 1, "AP": 6, "Tank": 9, "CC": 8, "Range": 2, "Late": True},
    "MasterYi":     {"AD": 10,"AP": 0, "Tank": 2, "CC": 0, "Range": 1, "Late": True},
    "Milio":        {"AD": 1, "AP": 5, "Tank": 1, "CC": 4, "Range": 7, "Late": True},
    "MissFortune":  {"AD": 10,"AP": 1, "Tank": 1, "CC": 2, "Range": 7, "Late": False},
    "MonkeyKing":   {"AD": 8, "AP": 0, "Tank": 5, "CC": 6, "Range": 2, "Late": False}, # Wukong
    "Mordekaiser":  {"AD": 1, "AP": 8, "Tank": 7, "CC": 4, "Range": 2, "Late": True},
    "Morgana":      {"AD": 0, "AP": 8, "Tank": 2, "CC": 8, "Range": 6, "Late": False},

    # --- N ---
    "Nami":         {"AD": 0, "AP": 6, "Tank": 1, "CC": 7, "Range": 6, "Late": False},
    "Nasus":        {"AD": 8, "AP": 2, "Tank": 7, "CC": 4, "Range": 1, "Late": True},
    "Nautilus":     {"AD": 2, "AP": 3, "Tank": 9, "CC": 10,"Range": 1, "Late": False},
    "Neeko":        {"AD": 2, "AP": 9, "Tank": 2, "CC": 7, "Range": 5, "Late": False},
    "Nidalee":      {"AD": 2, "AP": 9, "Tank": 2, "CC": 1, "Range": 8, "Late": False},
    "Nilah":        {"AD": 9, "AP": 0, "Tank": 3, "CC": 4, "Range": 1, "Late": True},
    "Nocturne":     {"AD": 9, "AP": 0, "Tank": 3, "CC": 4, "Range": 1, "Late": False},
    "Nunu":         {"AD": 1, "AP": 6, "Tank": 8, "CC": 7, "Range": 1, "Late": False},

    # --- O ---
    "Olaf":         {"AD": 9, "AP": 0, "Tank": 6, "CC": 2, "Range": 1, "Late": False},
    "Orianna":      {"AD": 1, "AP": 10,"Tank": 2, "CC": 6, "Range": 7, "Late": True},
    "Ornn":         {"AD": 3, "AP": 4, "Tank": 10,"CC": 9, "Range": 2, "Late": True},

    # --- P ---
    "Pantheon":     {"AD": 9, "AP": 0, "Tank": 4, "CC": 4, "Range": 2, "Late": False},
    "Poppy":        {"AD": 4, "AP": 0, "Tank": 10,"CC": 8, "Range": 1, "Late": False},
    "Pyke":         {"AD": 9, "AP": 0, "Tank": 1, "CC": 7, "Range": 1, "Late": False},

    # --- Q ---
    "Qiyana":       {"AD": 10,"AP": 0, "Tank": 1, "CC": 5, "Range": 2, "Late": True},
    "Quinn":        {"AD": 9, "AP": 0, "Tank": 1, "CC": 3, "Range": 5, "Late": False},

    # --- R ---
    "Rakan":        {"AD": 1, "AP": 4, "Tank": 4, "CC": 8, "Range": 2, "Late": False},
    "Rammus":       {"AD": 3, "AP": 3, "Tank": 10,"CC": 8, "Range": 1, "Late": False},
    "RekSai":       {"AD": 8, "AP": 0, "Tank": 5, "CC": 5, "Range": 1, "Late": False},
    "Rell":         {"AD": 1, "AP": 2, "Tank": 9, "CC": 9, "Range": 1, "Late": False},
    "Renata":       {"AD": 1, "AP": 5, "Tank": 2, "CC": 7, "Range": 6, "Late": True},
    "Renekton":     {"AD": 8, "AP": 0, "Tank": 7, "CC": 4, "Range": 1, "Late": False},
    "Rengar":       {"AD": 10,"AP": 0, "Tank": 2, "CC": 2, "Range": 1, "Late": False},
    "Riven":        {"AD": 10,"AP": 0, "Tank": 4, "CC": 4, "Range": 1, "Late": False},
    "Rumble":       {"AD": 0, "AP": 9, "Tank": 4, "CC": 5, "Range": 3, "Late": False},
    "Ryze":         {"AD": 0, "AP": 10,"Tank": 4, "CC": 4, "Range": 6, "Late": True},

    # --- S ---
    "Samira":       {"AD": 10,"AP": 0, "Tank": 1, "CC": 2, "Range": 4, "Late": True},
    "Sejuani":      {"AD": 2, "AP": 5, "Tank": 9, "CC": 8, "Range": 2, "Late": True},
    "Senna":        {"AD": 8, "AP": 1, "Tank": 1, "CC": 4, "Range": 10,"Late": True},
    "Seraphine":    {"AD": 0, "AP": 8, "Tank": 1, "CC": 6, "Range": 8, "Late": True},
    "Sett":         {"AD": 8, "AP": 0, "Tank": 7, "CC": 5, "Range": 1, "Late": False},
    "Shaco":        {"AD": 7, "AP": 5, "Tank": 1, "CC": 5, "Range": 1, "Late": False},
    "Shen":         {"AD": 2, "AP": 3, "Tank": 9, "CC": 6, "Range": 1, "Late": False},
    "Shyvana":      {"AD": 5, "AP": 7, "Tank": 6, "CC": 2, "Range": 2, "Late": True},
    "Singed":       {"AD": 0, "AP": 7, "Tank": 8, "CC": 5, "Range": 1, "Late": True},
    "Sion":         {"AD": 4, "AP": 1, "Tank": 10,"CC": 7, "Range": 2, "Late": True},
    "Sivir":        {"AD": 10,"AP": 0, "Tank": 1, "CC": 0, "Range": 6, "Late": True},
    "Skarner":      {"AD": 3, "AP": 2, "Tank": 9, "CC": 8, "Range": 1, "Late": False},
    "Smolder":      {"AD": 9, "AP": 2, "Tank": 1, "CC": 1, "Range": 8, "Late": True},
    "Sona":         {"AD": 0, "AP": 7, "Tank": 1, "CC": 5, "Range": 6, "Late": True},
    "Soraka":       {"AD": 0, "AP": 6, "Tank": 2, "CC": 3, "Range": 6, "Late": True},
    "Swain":        {"AD": 0, "AP": 8, "Tank": 5, "CC": 6, "Range": 5, "Late": True},
    "Sylas":        {"AD": 2, "AP": 9, "Tank": 4, "CC": 4, "Range": 2, "Late": True},
    "Syndra":       {"AD": 0, "AP": 10,"Tank": 1, "CC": 5, "Range": 8, "Late": True},

    # --- T ---
    "TahmKench":    {"AD": 2, "AP": 4, "Tank": 10,"CC": 7, "Range": 2, "Late": True},
    "Taliyah":      {"AD": 0, "AP": 9, "Tank": 2, "CC": 5, "Range": 7, "Late": False},
    "Talon":        {"AD": 10,"AP": 0, "Tank": 1, "CC": 1, "Range": 2, "Late": False},
    "Taric":        {"AD": 2, "AP": 2, "Tank": 8, "CC": 6, "Range": 1, "Late": False},
    "Teemo":        {"AD": 2, "AP": 9, "Tank": 1, "CC": 5, "Range": 5, "Late": False},
    "Thresh":       {"AD": 3, "AP": 4, "Tank": 6, "CC": 9, "Range": 4, "Late": False},
    "Tristana":     {"AD": 10,"AP": 1, "Tank": 1, "CC": 2, "Range": 9, "Late": True},
    "Trundle":      {"AD": 9, "AP": 0, "Tank": 6, "CC": 3, "Range": 1, "Late": False},
    "Tryndamere":   {"AD": 10,"AP": 0, "Tank": 4, "CC": 2, "Range": 1, "Late": True},
    "TwistedFate":  {"AD": 3, "AP": 9, "Tank": 1, "CC": 6, "Range": 7, "Late": True},
    "Twitch":       {"AD": 9, "AP": 3, "Tank": 0, "CC": 2, "Range": 9, "Late": True},

    # --- U ---
    "Udyr":         {"AD": 5, "AP": 5, "Tank": 7, "CC": 4, "Range": 1, "Late": False},
    "Urgot":        {"AD": 8, "AP": 0, "Tank": 7, "CC": 3, "Range": 4, "Late": True},

    # --- V ---
    "Varus":        {"AD": 7, "AP": 5, "Tank": 1, "CC": 4, "Range": 9, "Late": False},
    "Vayne":        {"AD": 10,"AP": 0, "Tank": 1, "CC": 3, "Range": 5, "Late": True},
    "Veigar":       {"AD": 0, "AP": 10,"Tank": 2, "CC": 5, "Range": 7, "Late": True},
    "Velkoz":       {"AD": 0, "AP": 10,"Tank": 1, "CC": 4, "Range": 10,"Late": False},
    "Vex":          {"AD": 0, "AP": 10,"Tank": 2, "CC": 5, "Range": 7, "Late": False},
    "Vi":           {"AD": 8, "AP": 0, "Tank": 6, "CC": 6, "Range": 1, "Late": False},
    "Viego":        {"AD": 9, "AP": 0, "Tank": 4, "CC": 5, "Range": 2, "Late": True},
    "Viktor":       {"AD": 0, "AP": 10,"Tank": 2, "CC": 5, "Range": 7, "Late": True},
    "Vladimir":     {"AD": 0, "AP": 9, "Tank": 6, "CC": 1, "Range": 5, "Late": True},
    "Volibear":     {"AD": 5, "AP": 5, "Tank": 8, "CC": 5, "Range": 1, "Late": False},

    # --- W ---
    "Warwick":      {"AD": 6, "AP": 3, "Tank": 7, "CC": 5, "Range": 1, "Late": False},
    "Wukong":       {"AD": 8, "AP": 0, "Tank": 5, "CC": 6, "Range": 2, "Late": False},

    # --- X ---
    "Xayah":        {"AD": 10,"AP": 0, "Tank": 1, "CC": 4, "Range": 5, "Late": True},
    "Xerath":       {"AD": 0, "AP": 10,"Tank": 1, "CC": 4, "Range": 10,"Late": True},
    "XinZhao":      {"AD": 8, "AP": 1, "Tank": 6, "CC": 4, "Range": 1, "Late": False},

    # --- Y ---
    "Yasuo":        {"AD": 10,"AP": 0, "Tank": 2, "CC": 4, "Range": 1, "Late": True},
    "Yone":         {"AD": 9, "AP": 2, "Tank": 2, "CC": 5, "Range": 1, "Late": True},
    "Yorick":       {"AD": 8, "AP": 1, "Tank": 7, "CC": 3, "Range": 1, "Late": True},
    "Yunara":       {"AD": 1, "AP": 10,"Tank": 2, "CC": 5, "Range": 8, "Late": True}, # Nouveau S16
    "Yuumi":        {"AD": 0, "AP": 5, "Tank": 0, "CC": 3, "Range": 5, "Late": True},

    # --- Z ---
    "Zaahen":       {"AD": 9, "AP": 1, "Tank": 4, "CC": 6, "Range": 1, "Late": True}, # Nouveau S16
    "Zac":          {"AD": 1, "AP": 5, "Tank": 9, "CC": 9, "Range": 2, "Late": True},
    "Zed":          {"AD": 10,"AP": 0, "Tank": 1, "CC": 1, "Range": 2, "Late": False},
    "Zeri":         {"AD": 7, "AP": 4, "Tank": 1, "CC": 2, "Range": 7, "Late": True},
    "Ziggs":        {"AD": 0, "AP": 10,"Tank": 1, "CC": 4, "Range": 9, "Late": False},
    "Zilean":       {"AD": 0, "AP": 6, "Tank": 2, "CC": 5, "Range": 6, "Late": True},
    "Zoe":          {"AD": 1, "AP": 10,"Tank": 1, "CC": 4, "Range": 8, "Late": False},
    "Zyra":         {"AD": 0, "AP": 9, "Tank": 1, "CC": 6, "Range": 7, "Late": False}
}

# ==============================================================================
# FONCTIONS UTILITAIRES
# ==============================================================================

def get_team_stats(team_list):
    """Calcule les stats cumulées d'une équipe"""
    total = {"AD": 0, "AP": 0, "Tank": 0, "CC": 0, "Late": 0, "Range": 0}
    for champ in team_list:
        if champ == "(A choisir)": continue
        
        clean = champ.replace(" ", "").replace("'", "").replace(".", "")
        if clean == "MonkeyKing": clean = "Wukong"
        if clean == "RenataGlasc": clean = "Renata"
        if clean == "Nunu&Willump": clean = "Nunu"
        
        # Valeurs par défaut si champion inconnu
        stats = ARCHETYPES.get(clean, {"AD": 5, "AP": 5, "Tank": 5, "CC": 5, "Range": 5, "Late": False}) 
        
        total["AD"] += stats["AD"]
        total["AP"] += stats["AP"]
        total["Tank"] += stats["Tank"]
        total["CC"] += stats["CC"]
        total["Range"] += stats.get("Range", 5)
        if stats.get("Late", False): total["Late"] += 1
            
    return total

def draw_comparison_radar(blue_stats, red_stats):
    """Crée le Radar Chart Comparatif"""
    categories = ['Dégâts Physiques', 'Dégâts Magiques', 'Tankiness', 'Contrôle (CC)', 'Portée (Poke)']
    
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[blue_stats["AD"], blue_stats["AP"], blue_stats["Tank"], blue_stats["CC"], blue_stats["Range"]],
        theta=categories,
        fill='toself', name='Blue Team', line_color='blue', opacity=0.7
    ))

    fig.add_trace(go.Scatterpolar(
        r=[red_stats["AD"], red_stats["AP"], red_stats["Tank"], red_stats["CC"], red_stats["Range"]],
        theta=categories,
        fill='toself', name='Red Team', line_color='red', opacity=0.6
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 45], tickfont=dict(size=10))),
        showlegend=True,
        margin=dict(l=40, r=40, t=20, b=20),
        height=350,
        title="⚔️ Comparatif des Forces"
    )
    return fig