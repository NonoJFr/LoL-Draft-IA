# coach.py
import stats_tools as stt

# On garde la variable pour ne pas casser l'import dans app.py, mais on s'en fiche
OLLAMA_ACTIF = True 
def is_ollama_active(): return True

def get_stats_score(champion_name):
    """Récupère les stats brutes (0-10)"""
    clean = champion_name.replace(" ", "").replace("'", "").replace(".", "")
    if clean == "Wukong": clean = "MonkeyKing"
    # Si Zaahen n'est pas dans la liste, on lui met des stats moyennes pour pas crash
    return stt.ARCHETYPES.get(clean, {"AD": 5, "AP": 5, "Tank": 5, "CC": 5})

def ask_ai_coach(my_team, enemy_team, recommended_pick, role, rec_winrate, my_team_winrates={}, enemy_team_winrates={}):
    
    # 1. ANALYSE DU CHAMPION (Zaahen, etc.)
    pick_stats = get_stats_score(recommended_pick)
    
    # Construction de l'identité du pick
    identity = []
    if pick_stats["AD"] >= 7: identity.append("AD")
    if pick_stats["AP"] >= 7: identity.append("AP")
    if pick_stats["Tank"] >= 7: identity.append("Tank")
    if pick_stats["CC"] >= 7: identity.append("Contrôle")
    if not identity: identity.append("Polyvalent")
    identity_str = "/".join(identity)

    # 2. ANALYSE DE LA COMITION (Winrate)
    analyse_winrate = ""
    if rec_winrate >= 54:
        analyse_winrate = f"🔥 **Forme Olympique** : Avec {rec_winrate:.1f}% de victoire, c'est un pick dominant dans la méta actuelle."
    elif rec_winrate >= 50:
        analyse_winrate = f"✅ **Pick Solide** : Winrate positif ({rec_winrate:.1f}%), un choix fiable."
    elif rec_winrate >= 47:
        analyse_winrate = f"⚠️ **Situationsnel** : Winrate moyen ({rec_winrate:.1f}%), demande de la maîtrise."
    else:
        analyse_winrate = f"💀 **Danger** : Statistiquement faible ({rec_winrate:.1f}%), à jouer seulement si OTP."

    # 3. ANALYSE DE L'ÉQUILIBRE D'ÉQUIPE (Mathématique)
    # On calcule les totaux de TA team
    team_ad = sum([get_stats_score(c)["AD"] for c in my_team])
    team_ap = sum([get_stats_score(c)["AP"] for c in my_team])
    team_tank = sum([get_stats_score(c)["Tank"] for c in my_team])
    
    conseil_equilibre = ""
    
    # Scénario : On manque d'AP et le pick est AP
    if team_ap < 15 and pick_stats["AP"] >= 6:
        conseil_equilibre = "⚖️ **Équilibrage** : Excellent choix, il apporte les dégâts magiques qui manquaient à l'équipe."
    # Scénario : On est déjà Full AD et le pick est AD
    elif team_ad > 30 and pick_stats["AD"] >= 6:
        conseil_equilibre = "⚠️ **Attention Full AD** : Ce pick ajoute encore des dégâts physiques. L'ennemi risque de stacker l'armure."
    # Scénario : On manque de Tank et le pick est Tank
    elif team_tank < 15 and pick_stats["Tank"] >= 6:
        conseil_equilibre = "🛡️ **Frontline** : Vital. L'équipe était trop fragile, ce pick apporte la tankiness nécessaire."
    else:
        conseil_equilibre = f"✨ **Synergie** : Ce champion ({identity_str}) s'intègre au style de jeu global."

    # 4. ASSEMBLAGE DU TEXTE
    # C'est du texte pré-écrit, donc zéro hallucination possible.
    
    rapport = f"""
    ### 🤖 Analyse Tactique (Algorithme V2)
    
    1. {analyse_winrate}
    2. {conseil_equilibre}
    3. **Profil du Pick** : {recommended_pick} est identifié comme **{identity_str}**.
    
    *(Données basées sur {len(my_team_winrates) + len(enemy_team_winrates)} champions analysés)*
    """
    
    return rapport