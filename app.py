import streamlit as st
import pandas as pd
import requests
import itertools
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# --- GESTION OLLAMA (POUR DÉPLOIEMENT EN LIGNE) ---
try:
    import ollama
    OLLAMA_ACTIF = True
except ImportError:
    OLLAMA_ACTIF = False

# --- CONFIGURATION ---
st.set_page_config(page_title="LoL AI Coach - Fearless Mode", layout="wide")

# --- MAPPING & ROLES ---
NAME_MAPPING = {
    "MonkeyKing": "Wukong",
    "Renata": "Renata Glasc"
}

def clean_name(name):
    return NAME_MAPPING.get(name, name)

# TA LISTE PERSONNALISÉE
ROLES = {
    "TOP": ["TahmKench", "Ornn", "Garen", "DrMundo", "Shen", "Ambessa", "Malphite", "Sion","Warwick"],
    "JUNGLE": ["Maokai", "XinZhao", "Talon", "Diana", "Elise", "Amumu", "Wukong", "Sejuani"],
    "MID": ["Orianna", "Azir", "Viktor", "Katarina", "Xerath", "Aurora", "Ryze", "Yone", "Ahri"],
    "ADC": ["Kaisa", "Ezreal", "Jinx", "Caitlyn", "Ashe", "Xayah", "Kalista", "MissFortune", "Smolder", "Aphelios"],
    "SUPPORT": ["Soraka", "Milio", "Yuumi", "Lulu", "Nami", "Leona", "Thresh", "Rakan", "Karma", "Morgana", "Braum"]
}

st.title("🏆 LoL AI Coach - V8 (Bans & Fearless)")

# --- 1. FONCTION D'ENTRAÎNEMENT ---
@st.cache_resource
def train_model():
    try:
        df = pd.read_csv('mes_donnees_lol.csv')
        for col in df.columns:
            if 'Pick' in col:
                df[col] = df[col].apply(lambda x: NAME_MAPPING.get(x, x))

        version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        latest_version = requests.get(version_url).json()[0]
        ddragon_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
        data_champions = requests.get(ddragon_url).json()
        
        raw_list = list(data_champions['data'].keys())
        clean_list_riot = sorted(list(set([clean_name(n) for n in raw_list])))
        champ_list_ui = ["(A choisir)"] + clean_list_riot

        encoder = LabelEncoder()
        encoder.fit(champ_list_ui)

        temp_df = df.copy()
        for col in temp_df.columns:
            if 'Pick' in col:
                temp_df = temp_df[temp_df[col].isin(clean_list_riot)]
                temp_df[col] = encoder.transform(temp_df[col])
        
        X = temp_df.drop('Blue_Win', axis=1)
        y = temp_df['Blue_Win']
        
        model = RandomForestClassifier(n_estimators=200, random_state=42)
        model.fit(X, y)
        return model, encoder, champ_list_ui, len(df)
    except Exception as e:
        st.error(f"Erreur technique : {e}")
        return None, None, [], 0

model, encoder, champ_list_ui, nb_matchs = train_model()
if model is None: st.stop()

st.sidebar.success(f"Matches analysés : {nb_matchs}")
if OLLAMA_ACTIF:
    st.sidebar.success("✅ Module Coach (Ollama) Actif")
else:
    st.sidebar.warning("⚠️ Module Coach (Ollama) Inactif")

# --- FONCTION DU COACH (VERSION STRICTE) ---
def ask_ai_coach(my_team, enemy_team, recommended_pick, role, winrate):
    # Sécurité pour le déploiement en ligne
    if not OLLAMA_ACTIF:
        return "⚠️ Le Coach Textuel est désactivé (Module 'ollama' non installé ou serveur cloud)."
        
    my_team_str = ', '.join(my_team)
    enemy_team_str = ', '.join(enemy_team)
    
    prompt = f"""
    Agis comme un analyste de données LoL concis.
    
    CONTEXTE :
    Alliés : [{my_team_str}]
    Ennemis : [{enemy_team_str}]
    Pick Recommandé : {recommended_pick} ({role})
    Winrate : {winrate:.1f}%

    DIRECTIVE :
    Donne 3 raisons techniques courtes (1 phrase max par point).
    N'utilise AUCUN nom de sort ou de compétence.
    Ne fais AUCUNE phrase d'introduction ou de conclusion.
    
    STRUCTURE DE RÉPONSE OBLIGATOIRE :
    1. ⚖️ Dégâts : (AD/AP/Burst/DPS)
    2. 🛡️ Utilité : (CC/Peel/Engage)
    3. ⚔️ Matchup : (Avantage tactique)
    """
    
    try:
        response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}], options={'temperature': 0.3})
        return response['message']['content']
    except Exception as e:
        return f"Erreur Ollama : {e}"

# --- 2. INTERFACE BANS & FEARLESS ---
with st.expander("🚫 GESTION DES BANS & FEARLESS (Tournoi)", expanded=True):
    col_ban1, col_ban2, col_fearless = st.columns([1, 1, 2])
    ban_list = champ_list_ui[1:]
    
    with col_ban1:
        st.caption("🟦 Blue Bans")
        bans_blue = st.multiselect("Bans Blue", ban_list, key="bans_blue", label_visibility="collapsed")
    with col_ban2:
        st.caption("🟥 Red Bans")
        bans_red = st.multiselect("Bans Red", ban_list, key="bans_red", label_visibility="collapsed")
    with col_fearless:
        st.caption("💀 Fearless (Déjà joués)")
        fearless_picks = st.multiselect("Champions indisponibles", ban_list, key="fearless")

FORBIDDEN_CHAMPS = set(bans_blue + bans_red + fearless_picks)

# --- 3. INTERFACE DE DRAFT ---
st.divider()
col1, col2 = st.columns(2)
def pick_menu(label, key, default="Gwenu"):
    idx = 0
    if default in champ_list_ui: idx = champ_list_ui.index(default)
    return st.selectbox(label, champ_list_ui, index=idx, key=key)

with col1:
    st.header("🟦 BLUE SIDE")
    b1 = pick_menu("Pick 1", "b1", "Renekton")
    b2 = pick_menu("Pick 2", "b2", "Sejuani")
    b3 = pick_menu("Pick 3", "b3", "(A choisir)")
    b4 = pick_menu("Pick 4", "b4", "(A choisir)")
    b5 = pick_menu("Pick 5", "b5", "(A choisir)")

with col2:
    st.header("🟥 RED SIDE")
    r1 = pick_menu("Pick 1", "r1", "Aatrox")
    r2 = pick_menu("Pick 2", "r2", "Maokai")
    r3 = pick_menu("Pick 3", "r3", "Orianna")
    r4 = pick_menu("Pick 4", "r4", "Varus")
    r5 = pick_menu("Pick 5", "r5", "Karma")

current_draft = [b1, b2, b3, b4, b5, r1, r2, r3, r4, r5]

# --- 4. ANALYSE SIMPLE (Bouton Ajouté) ---
st.divider()
if st.button("🔮 QUI GAGNE ? (Analyse Rapide)", type="primary", use_container_width=True):
    safe_draft = [c if c != "(A choisir)" else "Aatrox" for c in current_draft]
    try:
        draft_nums = []
        draft_nums.extend(encoder.transform(safe_draft[:5]))
        draft_nums.extend(encoder.transform(safe_draft[5:]))
        cols = [col for col in pd.read_csv('mes_donnees_lol.csv', nrows=1).columns if 'Pick' in col]
        proba = model.predict_proba(pd.DataFrame([draft_nums], columns=cols))[0]
        
        win_blue = proba[1] * 100
        win_red = proba[0] * 100
        
        c1, c2 = st.columns(2)
        with c1: st.metric("Blue", f"{win_blue:.1f}%")
        with c2: st.metric("Red", f"{win_red:.1f}%")
        
        if win_blue > 52: st.success("AVANTAGE BLUE")
        elif win_red > 52: st.error("AVANTAGE RED")
        else: st.info("ÉQUILIBRÉ")
    except: st.error("Erreur de calcul")

# --- 5. TEAM BUILDER ---
st.subheader("🏗️ Coach Tactique & Builder")
use_llm = st.checkbox("Activer l'explication du Coach", value=True, disabled=not OLLAMA_ACTIF)

missing_indices = [i for i, x in enumerate(current_draft) if x == "(A choisir)"]

if len(missing_indices) > 0 and len(missing_indices) <= 3:
    cols_roles = st.columns(len(missing_indices))
    selected_roles = []
    team_color = "BLUE" if missing_indices[0] < 5 else "RED"
    
    for idx, col_role in enumerate(cols_roles):
        match_idx = missing_indices[idx]
        slot_name = f"{'Blue' if match_idx < 5 else 'Red'} Pick {match_idx % 5 + 1}"
        with col_role:
            role = st.selectbox(f"Rôle pour {slot_name}", ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"], key=f"role_{idx}")
            selected_roles.append(role)

    if st.button("✨ GÉNÉRER COMPOSITION (Filtrée)"):
        progress_bar = st.progress(0)
        
        lists_to_combine = []
        for role in selected_roles:
            raw_list = ROLES.get(role, [])
            filtered_list = [c for c in raw_list if c not in FORBIDDEN_CHAMPS]
            lists_to_combine.append(filtered_list)

        if any(len(l) == 0 for l in lists_to_combine):
            st.error("❌ Tous les champions possibles sont bannis !")
            st.stop()

        combinations = list(itertools.product(*lists_to_combine))
        if len(combinations) > 3000: combinations = combinations[:3000]

        simulations = []
        valid_combos = []
        already_picked = [c for c in current_draft if c != "(A choisir)"]
        full_exclusion = set(already_picked).union(FORBIDDEN_CHAMPS)
        cols = [col for col in pd.read_csv('mes_donnees_lol.csv', nrows=1).columns if 'Pick' in col]

        for combo in combinations:
            if len(set(combo)) != len(combo): continue
            if any(c in full_exclusion for c in combo): continue
            
            test_draft = current_draft.copy()
            try:
                for i, champ in enumerate(combo):
                    clean_c = clean_name(champ)
                    test_draft[missing_indices[i]] = clean_c
                nums = encoder.transform(test_draft)
                simulations.append(nums)
                valid_combos.append(combo)
            except: continue
                
        if len(simulations) > 0:
            big_df = pd.DataFrame(simulations, columns=cols)
            all_probas = model.predict_proba(big_df)
            results = []
            for i, p in enumerate(all_probas):
                winrate = p[1] if team_color == "BLUE" else p[0]
                results.append((valid_combos[i], winrate * 100))
            
            results.sort(key=lambda x: x[1], reverse=True)
            progress_bar.progress(100)
            
            best_combo_names, best_winrate = results[0]
            st.success(f"🏆 TOP PICK : {' + '.join(best_combo_names)} ({best_winrate:.1f}%)")
            
            if use_llm and OLLAMA_ACTIF:
                with st.spinner("Le coach analyse..."):
                    my_team_final = [c for c in current_draft[:5] if c != "(A choisir)"] 
                    if team_color == "BLUE": my_team_final.extend(best_combo_names)
                    enemy_team_final = [c for c in current_draft[5:] if c != "(A choisir)"]
                    if team_color == "RED": enemy_team_final.extend(best_combo_names)
                    
                    explication = ask_ai_coach(
                        my_team=my_team_final,
                        enemy_team=enemy_team_final,
                        recommended_pick=' + '.join(best_combo_names),
                        role=', '.join(selected_roles),
                        winrate=best_winrate
                    )
                    st.info(explication)
            
            with st.expander("Autres options valides"):
                for i, (combo_names, score) in enumerate(results[1:6]):
                    st.write(f"**#{i+2}** : {' + '.join(combo_names)} ({score:.1f}%)")

        else:
            st.error("Aucune combinaison trouvée.")