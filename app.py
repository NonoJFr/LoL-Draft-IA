import streamlit as st
import pandas as pd
import requests
import itertools
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import random
from math import prod

# --- GESTION OLLAMA ---
try:
    import ollama
    OLLAMA_ACTIF = True
except ImportError:
    OLLAMA_ACTIF = False

# --- CONFIGURATION ---
st.set_page_config(page_title="LoL AI Coach V10 - Pool Manager", layout="wide")

MAX_COMBINATIONS = 25000
TOP_K_PER_ROLE = 8   # réduction intelligente par rôle

# --- MAPPING ---
NAME_MAPPING = {
    "MonkeyKing": "Wukong",
    "Renata": "Renata Glasc"
}
def clean_name(name): return NAME_MAPPING.get(name, name)

# --- STARTER PACK (Tes favoris par défaut) ---
# Ce sont les champions cochés par défaut au démarrage
USER_STARTER_POOL = {
    "TOP": ["TahmKench", "Ornn", "Garen", "DrMundo", "Shen", "Ambessa", "Malphite", "Sion","Warwick"],
    "JUNGLE": ["Maokai", "XinZhao", "Talon", "Diana", "Elise", "Amumu", "Wukong", "Sejuani"],
    "MID": ["Orianna", "Azir", "Viktor", "Katarina", "Xerath", "Aurora", "Ryze", "Yone", "Ahri"],
    "ADC": ["Kaisa", "Ezreal", "Jinx", "Caitlyn", "Ashe", "Xayah", "Kalista", "MissFortune", "Smolder", "Aphelios"],
    "SUPPORT": ["Soraka", "Milio", "Yuumi", "Lulu", "Nami", "Leona", "Thresh", "Rakan", "Karma", "Morgana", "Braum"]
}

# 2. LA LISTE DU JEU COMPLET (Pour l'option "Méta Globale")
# -> J'ai rempli ça avec quasiment tous les champions viables par rôle en S14/S15.
GLOBAL_META_ROLES = {
    "TOP": ["Aatrox", "Akali", "Ambessa", "Camille", "ChoGath", "Darius", "DrMundo", "Fiora", "Gangplank", "Garen", "Gnar", "Gragas", "Gwen","Irelia", "Jax", "Jayce", "Kayle", "Kennen", "Kled", "Ksante", "Malphite", "Mordekaiser", "Nasus", "Olaf", "Ornn","Poppy","Renekton", "Riven", "Rumble", "Sett", "Shen", "Singed", "Sion", "TahmKench", "Teemo", "Tryndamere", "Urgot", "Vayne", "Volibear", "Yasuo", "Yone", "Yorick", "Zaahen"],
    "JUNGLE": ["Amumu", "Diana","Elise", "Fiddlesticks","Graves", "Hecarim", "Ivern", "JarvanIV", "Karthus", "Kayn", "KhaZix", "Kindred", "LeeSin", "Lillia","Maokai", "Nidalee", "Nocturne", "Nunu", "Pantheon", "Poppy","RekSai", "Rengar", "Sejuani", "Shaco","Skarner","Talon", "Trundle","Vi", "Viego", "Volibear","Wukong", "XinZhao", "Zac", "Zed"],
    "MID": ["Ahri", "Akali","Anivia", "Annie", "AurelionSol", "Aurora", "Azir", "Cassiopeia", "Corki", "Diana","Galio", "Hwei", "Irelia", "Jayce","Katarina", "Leblanc", "Lissandra", "Lux", "Malzahar","Neeko", "Orianna", "Qiyana", "Ryze", "Smolder", "Swain", "Sylas", "Syndra", "Taliyah", "Talon", "TwistedFate", "Veigar", "Vex", "Viktor", "Vladimir", "Xerath", "Yasuo", "Yone", "Zed", "Ziggs", "Zoe"],
    "ADC": ["Aphelios", "Ashe", "Caitlyn", "Draven", "Ezreal", "Jhin", "Jinx", "Kaisa", "Kalista", "KogMaw", "Lucian", "MissFortune", "Nilah", "Samira", "Sivir", "Smolder", "Tristana", "Twitch", "Varus", "Vayne", "Xayah", "Zeri", "Ziggs"],
    "SUPPORT": ["Alistar", "Amumu", "Bard", "Blitzcrank", "Brand", "Braum", "Janna", "Karma", "Leona", "Lulu", "Lux", "Maokai", "Milio", "Morgana", "Nami", "Nautilus", "Neeko", "Pantheon", "Poppy", "Pyke", "Rakan", "Rell", "Renata Glasc", "Senna", "Seraphine", "Sona", "Soraka", "Swain", "TahmKench", "Taric", "Thresh", "Velkoz", "Xerath", "Yuumi", "Zilean", "Zyra"]
}

st.title("🏆 LoL AI Coach - V10 (Pool Manager)")

# --- 1. FONCTION D'ENTRAÎNEMENT ---
@st.cache_resource
def train_model():
    try:
        df = pd.read_csv('mes_donnees_lol.csv')
        for col in df.columns:
            if 'Pick' in col: df[col] = df[col].apply(lambda x: NAME_MAPPING.get(x, x))

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
        return model, encoder, champ_list_ui, len(df), clean_list_riot
    except Exception as e:
        st.error(f"Erreur technique : {e}")
        return None, None, [], 0, []

model, encoder, champ_list_ui, nb_matchs, full_champ_list = train_model()
if model is None: st.stop()

# --- COACH OLLAMA ---
def ask_ai_coach(my_team, enemy_team, recommended_pick, role, winrate):
    if not OLLAMA_ACTIF: return "⚠️ Coach Inactif."
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
    except:
        return "Ollama n'est pas lancé."

# ==============================================================================
# 2. SIDEBAR : GESTIONNAIRE DE POOL (LA NOUVEAUTÉ)
# ==============================================================================
st.sidebar.title("🎛️ Gestion d'Équipe")
st.sidebar.success(f"Data : {nb_matchs} matchs")

with st.sidebar.expander("🏊 MON CHAMPION POOL", expanded=False):
    st.write("Défins ici les champions que TES joueurs savent jouer.")
    MY_POOL = {}
    # ICI : On utilise USER_STARTER_POOL pour l'initialisation
    for role, defaults in USER_STARTER_POOL.items():
        valid_defaults = [c for c in defaults if c in full_champ_list]
        selected = st.multiselect(f"Pool {role}", full_champ_list, default=valid_defaults, key=f"pool_{role}")
        MY_POOL[role] = selected

# ==============================================================================
# 3. INTERFACE BANS & FEARLESS
# ==============================================================================
with st.expander("🚫 BANS & FEARLESS", expanded=True):
    c1, c2, c3 = st.columns([1,1,2])
    ban_list = champ_list_ui[1:]
    with c1: bans_blue = st.multiselect("Bans Blue", ban_list, key="bb", label_visibility="collapsed")
    with c2: bans_red = st.multiselect("Bans Red", ban_list, key="br", label_visibility="collapsed")
    with c3: fearless = st.multiselect("Fearless (Indisponibles)", ban_list, key="fl")

FORBIDDEN = set(bans_blue + bans_red + fearless)

# ==============================================================================
# 4. DRAFT BOARD
# ==============================================================================
st.divider()
col1, col2 = st.columns(2)
def p_menu(lbl, k, d="Gwenu"):
    i = champ_list_ui.index(d) if d in champ_list_ui else 0
    return st.selectbox(lbl, champ_list_ui, index=i, key=k)

with col1:
    st.header("🟦 BLUE SIDE")
    b1 = p_menu("Pick 1", "b1", "TahmKench")
    b2 = p_menu("Pick 2", "b2", "(A choisir)")
    b3 = p_menu("Pick 3", "b3", "Katarina")
    b4 = p_menu("Pick 4", "b4", "Ezreal")
    b5 = p_menu("Pick 5", "b5", "(A choisir)")

with col2:
    st.header("🟥 RED SIDE")
    r1 = p_menu("Pick 1", "r1", "Zaahen")
    r2 = p_menu("Pick 2", "r2", "LeeSin")
    r3 = p_menu("Pick 3", "r3", "Ahri")
    r4 = p_menu("Pick 4", "r4", "Kaisa")
    r5 = p_menu("Pick 5", "r5", "Nami")

draft = [b1, b2, b3, b4, b5, r1, r2, r3, r4, r5]

# ==============================================================================
# 5. BOUTON D'ANALYSE
# ==============================================================================
st.divider()
if st.button("🔮 QUI GAGNE ?", type="primary", use_container_width=True):
    safe = [c if c != "(A choisir)" else "Aatrox" for c in draft]
    try:
        d_nums = encoder.transform(safe[:5]).tolist() + encoder.transform(safe[5:]).tolist()
        cols = [col for col in pd.read_csv('mes_donnees_lol.csv', nrows=1).columns if 'Pick' in col]
        p = model.predict_proba(pd.DataFrame([d_nums], columns=cols))[0]
        wb, wr = p[1]*100, p[0]*100
        c1, c2 = st.columns(2)
        c1.metric("Blue", f"{wb:.1f}%")
        c2.metric("Red", f"{wr:.1f}%")
        if wb > 52: st.success("AVANTAGE BLUE")
        elif wr > 52: st.error("AVANTAGE RED")
        else: st.info("ÉQUILIBRÉ")
    except: st.error("Calcul impossible")

# ==============================================================================
# 6. BUILDER INTELLIGENT
# ==============================================================================
st.subheader("🏗️ Assistant de Draft")

holes = [i for i, x in enumerate(draft) if x == "(A choisir)"]

if len(holes) > 0 and len(holes) <= 5:
    # A. CONFIGURATION DES ROLES
    c_roles = st.columns(len(holes))
    sel_roles = []
    team_color = "BLUE" if holes[0] < 5 else "RED"
    
    for idx, cr in enumerate(c_roles):
        midx = holes[idx]
        sname = f"{'Blue' if midx < 5 else 'Red'} P{midx%5+1}"
        with cr:
            # CORRECTION ICI : on change key=f"r{idx}" par key=f"role_select_{idx}"
            # pour éviter le conflit avec les picks Red Side (r1, r2...)
            r = st.selectbox(f"Rôle {sname}", ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"], key=f"role_select_{idx}")
            sel_roles.append(r)

    # B. LE SWITCH STRATÉGIQUE (LA NOUVELLE OPTION)
    st.markdown("---")
    col_opt1, col_opt2 = st.columns([2, 1])
    
    with col_opt1:
        st.write("Quel pool de champions utiliser ?")
        # C'est ici que tu décides si tu limites l'IA ou si tu ouvres les vannes
        pool_mode = st.radio(
            "Mode de Suggestion :", 
            ["🔒 Mon Pool (Mes Joueurs)", "🌍 Méta Globale (Tout le jeu)"],
            horizontal=True
        )
    
    with col_opt2:
        st.write("")
        st.write("")
        use_llm = st.checkbox("Activer Coach (Ollama)", value=True, disabled=not OLLAMA_ACTIF)

    if st.button("✨ GÉNÉRER SUGGESTIONS"):
        prog = st.progress(0)
        lists = []
        for role in sel_roles:
            if "Mon Pool" in pool_mode:
                # Mode 1 : Ce qui est coché dans la Sidebar
                raw = MY_POOL.get(role, [])
                filt = [c for c in raw if c not in FORBIDDEN]
                if not raw: st.warning(f"Ton pool {role} est vide ! Je prends tout.")
            else:
                # Mode 2 : La GRANDE liste globale définie dans le code
                raw = GLOBAL_META_ROLES.get(role, []) 
                filt = [c for c in raw if c not in FORBIDDEN]
                filt = filt[:11]
            # Filtre Bans/Fearless
            lists.append(filt)

        if any(len(l) == 0 for l in lists):
            st.error("Aucun champion disponible avec ces filtres !")
            st.stop()

        is_global_meta = "Méta Globale" in pool_mode
        total_combinations = prod(len(l) for l in lists)
        def smart_sample(lists, n):
            res = set()
            tries = 0
            while len(res) < n and tries < n * 5:
                pick = tuple(random.choice(l) for l in lists)
                if len(set(pick)) == len(pick):
                    res.add(pick)
                    tries += 1
            return list(res)
        if total_combinations > MAX_COMBINATIONS:
            st.warning(
                f"⚠️ {total_combinations:,} combinaisons possibles → "
                f"échantillonnage de {MAX_COMBINATIONS:,}"
            )
            combos = smart_sample(lists, MAX_COMBINATIONS)
        else:
            combos = list(itertools.product(*lists))

        sims, v_combos = [], []
        picked = [c for c in draft if c != "(A choisir)"]
        excl = set(picked).union(FORBIDDEN)
        cols = [col for col in pd.read_csv('mes_donnees_lol.csv', nrows=1).columns if 'Pick' in col]

        for cmb in combos:
            if len(set(cmb)) != len(cmb): continue
            if any(c in excl for c in cmb): continue
            td = draft.copy()
            try:
                for i, c in enumerate(cmb): td[holes[i]] = clean_name(c)
                sims.append(encoder.transform(td))
                v_combos.append(cmb)
            except: continue
        
        if len(sims) > 0:
            probs = model.predict_proba(pd.DataFrame(sims, columns=cols))
            res = []
            for i, p in enumerate(probs):
                w = p[1] if team_color == "BLUE" else p[0]
                res.append((v_combos[i], w*100))
            
            res.sort(key=lambda x: x[1], reverse=True)
            prog.progress(100)
            
            best, b_score = res[0]
            st.success(f"🏆 TOP PICK : {' + '.join(best)} ({b_score:.1f}%)")
            
            if use_llm and OLLAMA_ACTIF:
                with st.spinner("Analyse..."):
                    m_team = [c for c in draft[:5] if c != "(A choisir)"] 
                    if team_color == "BLUE": m_team.extend(best)
                    e_team = [c for c in draft[5:] if c != "(A choisir)"]
                    if team_color == "RED": e_team.extend(best)
                    st.info(ask_ai_coach(m_team, e_team, ' + '.join(best), ', '.join(sel_roles), b_score))
            
            with st.expander("Voir plus d'options"):
                for i, (n, s) in enumerate(res[1:11]):
                    st.write(f"**#{i+2}** {', '.join(n)} ({s:.1f}%)")
        else:
            st.error("Aucune combinaison trouvée.")