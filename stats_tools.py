import pandas as pd
import plotly.graph_objects as go

# ==============================================================================
# BASE DE DONNÉES STATS CHAMPIONS (0 à 10)
# ==============================================================================
# AD = Dégâts Physiques | AP = Magiques | Tank = Résistance | CC = Contrôle
ARCHETYPES = {
    # --- A ---
    "Aatrox":       {"AD": 9, "AP": 0, "Tank": 6, "CC": 4},
    "Ahri":         {"AD": 1, "AP": 9, "Tank": 1, "CC": 5},
    "Akali":        {"AD": 4, "AP": 9, "Tank": 2, "CC": 1},
    "Akshan":       {"AD": 9, "AP": 1, "Tank": 1, "CC": 1},
    "Alistar":      {"AD": 1, "AP": 2, "Tank": 10,"CC": 10},
    "Amumu":        {"AD": 1, "AP": 6, "Tank": 9, "CC": 9},
    "Anivia":       {"AD": 0, "AP": 10,"Tank": 2, "CC": 8},
    "Annie":        {"AD": 1, "AP": 9, "Tank": 2, "CC": 6},
    "Aphelios":     {"AD": 10,"AP": 0, "Tank": 1, "CC": 3},
    "Ashe":         {"AD": 8, "AP": 0, "Tank": 1, "CC": 8},
    "AurelionSol":  {"AD": 0, "AP": 10,"Tank": 2, "CC": 5},
    "Ambessa":      {"AD": 9, "AP": 0, "Tank": 4, "CC": 4},
    "Aurora":       {"AD": 1, "AP": 9, "Tank": 2, "CC": 5},
    "Azir":         {"AD": 1, "AP": 10,"Tank": 1, "CC": 4},

    # --- B ---
    "Bard":         {"AD": 2, "AP": 5, "Tank": 4, "CC": 7},
    "Belveth":      {"AD": 9, "AP": 1, "Tank": 4, "CC": 4},
    "Blitzcrank":   {"AD": 2, "AP": 3, "Tank": 7, "CC": 9},
    "Brand":        {"AD": 0, "AP": 10,"Tank": 1, "CC": 3},
    "Braum":        {"AD": 1, "AP": 2, "Tank": 10,"CC": 9},
    "Briar":        {"AD": 9, "AP": 0, "Tank": 5, "CC": 5},

    # --- C ---
    "Caitlyn":      {"AD": 10,"AP": 0, "Tank": 0, "CC": 2},
    "Camille":      {"AD": 9, "AP": 0, "Tank": 5, "CC": 5},
    "Cassiopeia":   {"AD": 0, "AP": 10,"Tank": 3, "CC": 6},
    "ChoGath":      {"AD": 2, "AP": 5, "Tank": 10,"CC": 7},
    "Corki":        {"AD": 6, "AP": 6, "Tank": 1, "CC": 1}, # Hybride/True Dmg

    # --- D ---
    "Darius":       {"AD": 9, "AP": 0, "Tank": 6, "CC": 4},
    "Diana":        {"AD": 1, "AP": 9, "Tank": 4, "CC": 4},
    "DrMundo":      {"AD": 5, "AP": 1, "Tank": 10,"CC": 2},
    "Draven":       {"AD": 10,"AP": 0, "Tank": 1, "CC": 2},

    # --- E ---
    "Ekko":         {"AD": 2, "AP": 9, "Tank": 3, "CC": 5},
    "Elise":        {"AD": 1, "AP": 9, "Tank": 2, "CC": 5},
    "Evelynn":      {"AD": 1, "AP": 10,"Tank": 1, "CC": 3},
    "Ezreal":       {"AD": 7, "AP": 3, "Tank": 1, "CC": 0},

    # --- F ---
    "Fiddlesticks": {"AD": 0, "AP": 9, "Tank": 2, "CC": 7},
    "Fiora":        {"AD": 10,"AP": 0, "Tank": 4, "CC": 2},
    "Fizz":         {"AD": 2, "AP": 10,"Tank": 1, "CC": 3},

    # --- G ---
    "Galio":        {"AD": 1, "AP": 7, "Tank": 8, "CC": 8},
    "Gangplank":    {"AD": 9, "AP": 2, "Tank": 3, "CC": 3},
    "Garen":        {"AD": 7, "AP": 0, "Tank": 8, "CC": 1},
    "Gnar":         {"AD": 6, "AP": 1, "Tank": 7, "CC": 7},
    "Gragas":       {"AD": 1, "AP": 8, "Tank": 6, "CC": 7},
    "Graves":       {"AD": 9, "AP": 0, "Tank": 4, "CC": 2},
    "Gwen":         {"AD": 1, "AP": 10,"Tank": 4, "CC": 1},

    # --- H ---
    "Hecarim":      {"AD": 8, "AP": 1, "Tank": 5, "CC": 4},
    "Heimerdinger": {"AD": 0, "AP": 10,"Tank": 2, "CC": 5},
    "Hwei":         {"AD": 0, "AP": 10,"Tank": 1, "CC": 6},

    # --- I ---
    "Illaoi":       {"AD": 9, "AP": 0, "Tank": 6, "CC": 1},
    "Irelia":       {"AD": 8, "AP": 2, "Tank": 5, "CC": 4},
    "Ivern":        {"AD": 1, "AP": 5, "Tank": 3, "CC": 7},

    # --- J ---
    "Janna":        {"AD": 0, "AP": 6, "Tank": 1, "CC": 8},
    "JarvanIV":     {"AD": 7, "AP": 0, "Tank": 6, "CC": 7},
    "Jax":          {"AD": 7, "AP": 4, "Tank": 6, "CC": 3},
    "Jayce":        {"AD": 9, "AP": 0, "Tank": 2, "CC": 2},
    "Jhin":         {"AD": 10,"AP": 0, "Tank": 0, "CC": 2},
    "Jinx":         {"AD": 10,"AP": 0, "Tank": 0, "CC": 2},

    # --- K ---
    "Kaisa":        {"AD": 6, "AP": 6, "Tank": 1, "CC": 1}, # Hybride
    "Kalista":      {"AD": 9, "AP": 0, "Tank": 1, "CC": 3},
    "Karma":        {"AD": 0, "AP": 8, "Tank": 2, "CC": 5},
    "Karthus":      {"AD": 0, "AP": 10,"Tank": 1, "CC": 1},
    "Kassadin":     {"AD": 1, "AP": 10,"Tank": 3, "CC": 2},
    "Katarina":     {"AD": 4, "AP": 9, "Tank": 1, "CC": 0},
    "Kayle":        {"AD": 6, "AP": 8, "Tank": 2, "CC": 2},
    "Kayn":         {"AD": 9, "AP": 0, "Tank": 4, "CC": 2},
    "Kennen":       {"AD": 2, "AP": 9, "Tank": 2, "CC": 7},
    "KhaZix":       {"AD": 10,"AP": 0, "Tank": 1, "CC": 2},
    "Kindred":      {"AD": 9, "AP": 0, "Tank": 1, "CC": 2},
    "Kled":         {"AD": 8, "AP": 0, "Tank": 7, "CC": 2},
    "KogMaw":       {"AD": 5, "AP": 7, "Tank": 1, "CC": 2}, # Hybride %PV
    "Ksante":       {"AD": 5, "AP": 0, "Tank": 8, "CC": 8},

    # --- L ---
    "Leblanc":      {"AD": 1, "AP": 10,"Tank": 1, "CC": 3},
    "LeeSin":       {"AD": 8, "AP": 1, "Tank": 4, "CC": 5},
    "Leona":        {"AD": 1, "AP": 2, "Tank": 10,"CC": 10},
    "Lillia":       {"AD": 0, "AP": 9, "Tank": 3, "CC": 4},
    "Lissandra":    {"AD": 0, "AP": 8, "Tank": 3, "CC": 9},
    "Lucian":       {"AD": 9, "AP": 1, "Tank": 1, "CC": 0},
    "Lulu":         {"AD": 1, "AP": 6, "Tank": 1, "CC": 7},
    "Lux":          {"AD": 0, "AP": 10,"Tank": 1, "CC": 5},

    # --- M ---
    "Malphite":     {"AD": 2, "AP": 5, "Tank": 10,"CC": 9},
    "Malzahar":     {"AD": 0, "AP": 9, "Tank": 1, "CC": 8},
    "Maokai":       {"AD": 1, "AP": 6, "Tank": 9, "CC": 8},
    "MasterYi":     {"AD": 10,"AP": 0, "Tank": 2, "CC": 0},
    "Milio":        {"AD": 1, "AP": 5, "Tank": 1, "CC": 4},
    "MissFortune":  {"AD": 10,"AP": 1, "Tank": 1, "CC": 2},
    "MonkeyKing":   {"AD": 8, "AP": 0, "Tank": 5, "CC": 6}, # Wukong
    "Mordekaiser":  {"AD": 1, "AP": 8, "Tank": 7, "CC": 4},
    "Morgana":      {"AD": 0, "AP": 8, "Tank": 2, "CC": 8},

    # --- N ---
    "Nami":         {"AD": 0, "AP": 6, "Tank": 1, "CC": 7},
    "Nasus":        {"AD": 8, "AP": 2, "Tank": 7, "CC": 4},
    "Nautilus":     {"AD": 2, "AP": 3, "Tank": 9, "CC": 10},
    "Neeko":        {"AD": 2, "AP": 9, "Tank": 2, "CC": 7},
    "Nidalee":      {"AD": 2, "AP": 9, "Tank": 2, "CC": 1},
    "Nilah":        {"AD": 9, "AP": 0, "Tank": 3, "CC": 4},
    "Nocturne":     {"AD": 9, "AP": 0, "Tank": 3, "CC": 4},
    "Nunu":         {"AD": 1, "AP": 6, "Tank": 8, "CC": 7},

    # --- O ---
    "Olaf":         {"AD": 9, "AP": 0, "Tank": 6, "CC": 2},
    "Orianna":      {"AD": 1, "AP": 10,"Tank": 2, "CC": 6},
    "Ornn":         {"AD": 3, "AP": 4, "Tank": 10,"CC": 9},

    # --- P ---
    "Pantheon":     {"AD": 9, "AP": 0, "Tank": 4, "CC": 4},
    "Poppy":        {"AD": 4, "AP": 0, "Tank": 10,"CC": 8},
    "Pyke":         {"AD": 9, "AP": 0, "Tank": 1, "CC": 7},

    # --- Q ---
    "Qiyana":       {"AD": 10,"AP": 0, "Tank": 1, "CC": 5},
    "Quinn":        {"AD": 9, "AP": 0, "Tank": 1, "CC": 3},

    # --- R ---
    "Rakan":        {"AD": 1, "AP": 4, "Tank": 4, "CC": 8},
    "Rammus":       {"AD": 3, "AP": 3, "Tank": 10,"CC": 8},
    "RekSai":       {"AD": 8, "AP": 0, "Tank": 5, "CC": 5},
    "Rell":         {"AD": 1, "AP": 2, "Tank": 9, "CC": 9},
    "Renata":       {"AD": 1, "AP": 5, "Tank": 2, "CC": 7}, # Renata Glasc
    "Renekton":     {"AD": 8, "AP": 0, "Tank": 7, "CC": 4},
    "Rengar":       {"AD": 10,"AP": 0, "Tank": 2, "CC": 2},
    "Riven":        {"AD": 10,"AP": 0, "Tank": 4, "CC": 4},
    "Rumble":       {"AD": 0, "AP": 9, "Tank": 4, "CC": 5},
    "Ryze":         {"AD": 0, "AP": 10,"Tank": 4, "CC": 4},

    # --- S ---
    "Samira":       {"AD": 10,"AP": 0, "Tank": 1, "CC": 2},
    "Sejuani":      {"AD": 2, "AP": 5, "Tank": 9, "CC": 8},
    "Senna":        {"AD": 8, "AP": 1, "Tank": 1, "CC": 4},
    "Seraphine":    {"AD": 0, "AP": 8, "Tank": 1, "CC": 6},
    "Sett":         {"AD": 8, "AP": 0, "Tank": 7, "CC": 5},
    "Shaco":        {"AD": 7, "AP": 5, "Tank": 1, "CC": 5},
    "Shen":         {"AD": 2, "AP": 3, "Tank": 9, "CC": 6},
    "Shyvana":      {"AD": 5, "AP": 7, "Tank": 6, "CC": 2},
    "Singed":       {"AD": 0, "AP": 7, "Tank": 8, "CC": 5},
    "Sion":         {"AD": 4, "AP": 1, "Tank": 10,"CC": 7},
    "Sivir":        {"AD": 10,"AP": 0, "Tank": 1, "CC": 0},
    "Skarner":      {"AD": 3, "AP": 2, "Tank": 9, "CC": 8},
    "Smolder":      {"AD": 9, "AP": 2, "Tank": 1, "CC": 1},
    "Sona":         {"AD": 0, "AP": 7, "Tank": 1, "CC": 5},
    "Soraka":       {"AD": 0, "AP": 6, "Tank": 2, "CC": 3},
    "Swain":        {"AD": 0, "AP": 8, "Tank": 5, "CC": 6},
    "Sylas":        {"AD": 2, "AP": 9, "Tank": 4, "CC": 4},
    "Syndra":       {"AD": 0, "AP": 10,"Tank": 1, "CC": 5},

    # --- T ---
    "TahmKench":    {"AD": 2, "AP": 4, "Tank": 10,"CC": 7},
    "Taliyah":      {"AD": 0, "AP": 9, "Tank": 2, "CC": 5},
    "Talon":        {"AD": 10,"AP": 0, "Tank": 1, "CC": 1},
    "Taric":        {"AD": 2, "AP": 2, "Tank": 8, "CC": 6},
    "Teemo":        {"AD": 2, "AP": 9, "Tank": 1, "CC": 5},
    "Thresh":       {"AD": 3, "AP": 4, "Tank": 6, "CC": 9},
    "Tristana":     {"AD": 10,"AP": 1, "Tank": 1, "CC": 2},
    "Trundle":      {"AD": 9, "AP": 0, "Tank": 6, "CC": 3},
    "Tryndamere":   {"AD": 10,"AP": 0, "Tank": 4, "CC": 2},
    "TwistedFate":  {"AD": 3, "AP": 9, "Tank": 1, "CC": 6},
    "Twitch":       {"AD": 9, "AP": 3, "Tank": 0, "CC": 2},

    # --- U ---
    "Udyr":         {"AD": 5, "AP": 5, "Tank": 7, "CC": 4},
    "Urgot":        {"AD": 8, "AP": 0, "Tank": 7, "CC": 3},

    # --- V ---
    "Varus":        {"AD": 7, "AP": 5, "Tank": 1, "CC": 4},
    "Vayne":        {"AD": 10,"AP": 0, "Tank": 1, "CC": 3},
    "Veigar":       {"AD": 0, "AP": 10,"Tank": 2, "CC": 5},
    "Velkoz":       {"AD": 0, "AP": 10,"Tank": 1, "CC": 4},
    "Vex":          {"AD": 0, "AP": 10,"Tank": 2, "CC": 5},
    "Vi":           {"AD": 8, "AP": 0, "Tank": 6, "CC": 6},
    "Viego":        {"AD": 9, "AP": 0, "Tank": 4, "CC": 5},
    "Viktor":       {"AD": 0, "AP": 10,"Tank": 2, "CC": 5},
    "Vladimir":     {"AD": 0, "AP": 9, "Tank": 6, "CC": 1},
    "Volibear":     {"AD": 5, "AP": 5, "Tank": 8, "CC": 5},

    # --- W ---
    "Warwick":      {"AD": 6, "AP": 3, "Tank": 7, "CC": 5},
    "Wukong":       {"AD": 8, "AP": 0, "Tank": 5, "CC": 6},

    # --- X ---
    "Xayah":        {"AD": 10,"AP": 0, "Tank": 1, "CC": 4},
    "Xerath":       {"AD": 0, "AP": 10,"Tank": 1, "CC": 4},
    "XinZhao":      {"AD": 8, "AP": 1, "Tank": 6, "CC": 4},

    # --- Y ---
    "Yasuo":        {"AD": 10,"AP": 0, "Tank": 2, "CC": 4},
    "Yone":         {"AD": 9, "AP": 2, "Tank": 2, "CC": 5},
    "Yorick":       {"AD": 8, "AP": 1, "Tank": 7, "CC": 3},
    "Yuumi":        {"AD": 0, "AP": 5, "Tank": 0, "CC": 3},

    # --- Z ---
    "Zaahen":       {"AD": 10, "AP": 0, "Tank": 5, "CC": 3},
    "Zac":          {"AD": 1, "AP": 5, "Tank": 9, "CC": 9},
    "Zed":          {"AD": 10,"AP": 0, "Tank": 1, "CC": 1},
    "Zeri":         {"AD": 7, "AP": 4, "Tank": 1, "CC": 2},
    "Ziggs":        {"AD": 0, "AP": 10,"Tank": 1, "CC": 4},
    "Zilean":       {"AD": 0, "AP": 6, "Tank": 2, "CC": 5},
    "Zoe":          {"AD": 1, "AP": 10,"Tank": 1, "CC": 4},
    "Zyra":         {"AD": 0, "AP": 9, "Tank": 1, "CC": 6}
}

# ==============================================================================
# FONCTIONS UTILITAIRES
# ==============================================================================

def get_team_stats(team_list):
    """Calcule les stats cumulées d'une équipe"""
    total = {"AD": 0, "AP": 0, "Tank": 0, "CC": 0}
    for champ in team_list:
        if champ == "(A choisir)": continue
        
        # Nettoyage nom pour correspondre à la liste
        clean = champ.replace(" ", "").replace("'", "").replace(".", "")
        if clean == "MonkeyKing": clean = "Wukong"
        if clean == "RenataGlasc": clean = "Renata"
        if clean == "Nunu&Willump": clean = "Nunu"
        
        stats = ARCHETYPES.get(clean, {"AD": 5, "AP": 5, "Tank": 5, "CC": 5}) # Valeur moyenne si inconnu
        total["AD"] += stats["AD"]
        total["AP"] += stats["AP"]
        total["Tank"] += stats["Tank"]
        total["CC"] += stats["CC"]
    return total

def draw_comparison_radar(blue_stats, red_stats):
    """Crée le Radar Chart Comparatif"""
    categories = ['Dégâts Physiques', 'Dégâts Magiques', 'Tankiness', 'Contrôle (CC)']
    
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[blue_stats["AD"], blue_stats["AP"], blue_stats["Tank"], blue_stats["CC"]],
        theta=categories,
        fill='toself', name='Blue Team', line_color='blue', opacity=0.7
    ))

    fig.add_trace(go.Scatterpolar(
        r=[red_stats["AD"], red_stats["AP"], red_stats["Tank"], red_stats["CC"]],
        theta=categories,
        fill='toself', name='Red Team', line_color='red', opacity=0.6
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 40], tickfont=dict(size=10))),
        showlegend=True,
        margin=dict(l=40, r=40, t=20, b=20),
        height=350,
        title="⚔️ Comparatif des Forces"
    )
    return fig