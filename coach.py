# coach.py
import stats_tools as stt
import numpy as np
import backend as bk 
import itertools 

# ==============================================================================
# 1. LES OUTILS (DÉFINIS EN PREMIER POUR ÉVITER LES ERREURS)
# ==============================================================================

def get_stats_score(champion_name):
    """Récupère les stats (0-10) en nettoyant le nom"""
    clean = champion_name.replace(" ", "").replace("'", "").replace(".", "")
    if clean == "Wukong": clean = "MonkeyKing"
    return stt.ARCHETYPES.get(clean, {"AD": 5, "AP": 5, "Tank": 5, "CC": 5, "Late": False, "Range": 5})

def analyze_composition(team_list):
    """Calcule les scores cumulés d'une équipe"""
    return stt.get_team_stats(team_list)

def get_mvp_and_weak_link(team_list, winrates):
    """Trouve le meilleur et le pire champion selon le winrate"""
    # On filtre pour ne garder que ceux qui sont dans la team et pas vides
    valid = {c: wr for c, wr in winrates.items() if c in team_list and c != "(A choisir)"}
    
    if not valid: return None, None
    
    # Le MVP est celui avec le WR max
    mvp_name = max(valid, key=valid.get)
    mvp = (mvp_name, valid[mvp_name])
    
    # Le maillon faible est celui avec le WR min
    weak_name = min(valid, key=valid.get)
    weak = (weak_name, valid[weak_name])
    
    return mvp, weak

def find_best_combo(team_list):
    """Cherche le duo le plus fort statistiquement dans l'équipe"""
    best_duo = None
    best_score = 0
    best_count = 0
    
    # On teste toutes les paires possibles
    clean_list = [c for c in team_list if c != "(A choisir)"]
    if len(clean_list) < 2: return None, 0, 0

    pairs = list(itertools.combinations(clean_list, 2))
    
    for a, b in pairs:
        wr, count = bk.get_duo_winrate(a, b)
        if wr and count >= 3:
            if wr > best_score:
                best_score = wr
                best_duo = (a, b)
                best_count = count
                
    return best_duo, best_score, best_count

def qualify_combo(champ_a, champ_b):
    """Donne un nom stylé au combo"""
    s_a = get_stats_score(champ_a)
    s_b = get_stats_score(champ_b)
    
    if s_a["CC"] + s_b["CC"] >= 16: return "❄️ **Perma-CC**"
    if s_a["Tank"] + s_b["Tank"] >= 16: return "🛡️ **Mur de Briques**"
    if s_a["AD"] + s_b["AD"] >= 18: return "⚔️ **Double AD Burst**"
    if s_a["AP"] + s_b["AP"] >= 18: return "🔮 **Double Magic Burst**"
    if s_a["Range"] + s_b["Range"] >= 16: return "🏹 **Sniper Duo**"
    if s_a["Late"] and s_b["Late"]: return "⏳ **Time Bomb**"
    return "✨ **Synergie**"

# ==============================================================================
# 2. LE CERVEAU : ANALYSE DE MATCH (BOUTON 'QUI GAGNE')
# ==============================================================================

def generate_deep_analysis(blue_team, red_team, blue_wr_dict, red_wr_dict, global_blue_score):
    report = []
    
    # A. DÉFINITION DU VAINQUEUR
    if global_blue_score >= 50:
        winner_name = "BLUE"
        win_team, lose_team = blue_team, red_team
        win_wr, lose_wr = blue_wr_dict, red_wr_dict
    else:
        winner_name = "RED"
        win_team, lose_team = red_team, blue_team
        win_wr, lose_wr = red_wr_dict, blue_wr_dict

    report.append(f"### 🏆 Pourquoi {winner_name} SIDE a l'avantage ?")

    # B. MATCHUPS (LANING)
    lanes = ["Top", "Jungle", "Mid", "ADC", "Support"]
    gap_detected = False
    
    for i, lane in enumerate(lanes):
        try:
            w_c, l_c = win_team[i], lose_team[i]
            if w_c == "(A choisir)" or l_c == "(A choisir)": continue
            
            # Duel Direct
            h2h_wr, h2h_count = bk.get_head_to_head_stats(w_c, l_c)
            
            if h2h_count >= 3:
                if h2h_wr > 55:
                    report.append(f"✅ **{lane} Gap** : Historiquement, **{w_c}** bat {l_c} ({h2h_wr:.1f}% duel).")
                    gap_detected = True
            else:
                # Différence de forme globale
                diff = win_wr.get(w_c, 50) - lose_wr.get(l_c, 50)
                if diff > 5:
                    report.append(f"📈 **Forme {lane}** : **{w_c}** surperforme actuellement {l_c}.")
                    gap_detected = True
        except: pass

    # C. SYNERGIE DUO
    duo, duo_wr, duo_count = find_best_combo(win_team)
    if duo and duo_wr > 55:
        combo_name = qualify_combo(duo[0], duo[1])
        report.append(f"{combo_name} : Le duo **{duo[0]} + {duo[1]}** est très fort ({duo_wr:.1f}% WR).")

    # D. SCALING & TEMPO
    s_win = analyze_composition(win_team)
    s_lose = analyze_composition(lose_team)
    
    scaling_diff = s_win["Late"] - s_lose["Late"]
    if scaling_diff >= 1:
        report.append("⏳ **Condition : SCALING**. Jouez safe, le temps joue pour vous.")
    elif scaling_diff <= -2:
        report.append("🔥 **Condition : SNOWBALL**. Il faut gagner les lanes et finir vite.")

    # E. STRUCTURE
    if s_win["Tank"] > s_lose["Tank"] + 6:
        report.append("🛡️ **Frontline Gap** : Vous êtes beaucoup plus solides.")
    if s_win["CC"] > s_lose["CC"] + 6:
        report.append("❄️ **Control Gap** : Vous avez les outils pour catch n'importe qui.")

    # F. MVP (LE FACTEUR X)
    # C'est ici que ça plantait avant, maintenant la fonction est bien définie au début
    mvp, _ = get_mvp_and_weak_link(win_team, win_wr)
    if mvp and mvp[1] > 54:
        report.append(f"🌟 **MVP** : La game repose sur **{mvp[0]}** ({mvp[1]:.1f}% WR).")

    return report

# ==============================================================================
# 3. LE GÉNÉRATEUR DE PICK (TEAM BUILDER)
# ==============================================================================

def generate_pick_advice(pick_name, role, winrate, my_team):
    # Gestion des Multi-Picks (Duo ou Trio) pour éviter le crash
    if " + " in pick_name:
        picks = pick_name.split(" + ")
        
        if len(picks) == 2:
            p1, p2 = picks
            combo_txt = qualify_combo(p1, p2)
            return f"**{pick_name}** : {combo_txt} ({winrate:.1f}% WR)\n> Duo statistiquement dominant."
        else:
            return f"**{pick_name}** : 🔥 Synergie Groupée ({winrate:.1f}% WR)\n> Meilleure combinaison pour ces {len(picks)} rôles."
    
    # Gestion Solo Pick
    stats = get_stats_score(pick_name)
    team_stats = analyze_composition(my_team)
    
    if winrate > 53: forme = "🔥 Top Tier"
    elif winrate > 50: forme = "✅ Solide"
    else: forme = "⚠️ Risqué"
    
    conseil = "Bon pick standard."
    if stats["Late"] and team_stats["Late"] < 2:
        conseil = "⏳ Ajoute une assurance Late Game."
    elif stats["Range"] > 7 and team_stats["Range"] < 20:
        conseil = "🏹 Apporte du Poke indispensable."
    elif stats["Tank"] > 7 and team_stats["Tank"] < 10:
        conseil = "🛡️ Enfin une vraie Frontline."
    elif stats["AP"] > 7 and team_stats["AP"] < 10:
        conseil = "🔮 Vital : Apporte les dégâts magiques."

    return f"**{pick_name}** : {forme} ({winrate:.1f}% WR)\n> {conseil}"