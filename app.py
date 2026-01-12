import streamlit as st
import pandas as pd
import requests
import itertools
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# --- GESTION OLLAMA ---
try:
    import ollama
    OLLAMA_ACTIF = True
except ImportError:
    OLLAMA_ACTIF = False

# --- CONFIGURATION ---
st.set_page_config(page_title="LoL AI Coach - V10 STABLE", layout="wide")

# --- MAPPING ---
NAME_MAPPING = {
    "MonkeyKing": "Wukong",
    "Renata": "Renata Glasc"
}
def clean_name(name): return NAME_MAPPING.get(name, name)

# 1. LA LISTE DE TES JOUEURS (Celle qui apparait cochée par défaut)
USER_STARTER_POOL = {
    "TOP": ["TahmKench", "Ornn", "Garen", "DrMundo", "Shen", "Ambessa", "Malphite", "Sion", "Renekton", "Aatrox"],
    "JUNGLE": ["Maokai", "Xin Zhao", "Talon", "Diana", "Elise", "Amumu", "Wukong", "Sejuani", "Viego", "Lee Sin"],
    "MID": ["Orianna", "Azir", "Viktor", "Katarina", "Xerath", "Aurora", "Ryze", "Yone", "Ahri", "Syndra"],
    "ADC": ["Kaisa", "Ezreal", "Jinx", "Caitlyn", "Ashe", "Xayah", "Kalista", "Miss Fortune", "Smolder", "Aphelios", "Varus"],
    "SUPPORT": ["Soraka", "Milio", "Yuumi", "Lulu", "Nami", "Leona", "Thresh", "Rakan", "Karma", "Morgana", "Nautilus", "Braum"]
}

# 2. LA LISTE DU JEU COMPLET (Pour l'option "Méta Globale")
GLOBAL_META_ROLES = {
    "TOP": ["Aatrox", "Akali", "Ambessa", "Camille", "ChoGath", "Darius", "DrMundo", "Fiora", "Gangplank", "Garen", "Gnar", "Gragas", "Gwen", "Illaoi", "Irelia", "Jax", "Jayce", "Kayle", "Kennen", "Kled", "Ksante", "Malphite", "Mordekaiser", "Nasus", "Olaf", "Ornn", "Pantheon", "Poppy", "Quinn", "Renekton", "Riven", "Rumble", "Sett", "Shen", "Singed", "Sion", "TahmKench", "Teemo", "Tryndamere", "Urgot", "Vayne", "Volibear", "Wukong", "Yasuo", "Yone", "Yorick", "Zac"],
    "JUNGLE": ["Amumu", "Belveth", "Briar", "Diana", "Ekko", "Elise", "Evelynn", "Fiddlesticks", "Gragas", "Graves", "Hecarim", "Ivern", "JarvanIV", "Karthus", "Kayn", "KhaZix", "Kindred", "LeeSin", "Lillia", "MasterYi", "Maokai", "Nidalee", "Nocturne", "Nunu", "Pantheon", "Poppy", "Rammus", "RekSai", "Rengar", "Sejuani", "Shaco", "Shyvana", "Skarner", "Taliyah", "Talon", "Trundle", "Udyr", "Vi", "Viego", "Volibear", "Warwick", "Wukong", "XinZhao", "Zac", "Zed"],
    "MID": ["Ahri", "Akali", "Akshan", "Anivia", "Annie", "AurelionSol", "Aurora", "Azir", "Cassiopeia", "Corki", "Diana", "Ekko", "Fizz", "Galio", "Hwei", "Irelia", "Jayce", "Kassadin", "Katarina", "Leblanc", "Lissandra", "Lux", "Malzahar", "Naafiri", "Neeko", "Orianna", "Qiyana", "Ryze", "Smolder", "Swain", "Sylas", "Syndra", "Taliyah", "Talon", "TwistedFate", "Veigar", "Vex", "Viktor", "Vladimir", "Xerath", "Yasuo", "Yone", "Zed", "Ziggs", "Zoe"],
    "ADC": ["Aphelios", "Ashe", "Caitlyn", "Draven", "Ezreal", "Jhin", "Jinx", "Kaisa", "Kalista", "KogMaw", "Lucian", "MissFortune", "Nilah", "Samira", "Sivir", "Smolder", "Tristana", "Twitch", "Varus", "Vayne", "Xayah", "Zeri", "Ziggs"],
    "SUPPORT": ["Alistar", "Amumu", "Bard", "Blitzcrank", "Brand", "Braum", "Janna", "Karma", "Leona", "Lulu", "Lux", "Maokai", "Milio", "Morgana", "Nami", "Nautilus", "Neeko", "Pantheon", "Poppy", "Pyke", "Rakan", "Rell", "Renata Glasc", "Senna", "Seraphine", "Sona", "Soraka", "Swain", "TahmKench", "Taric", "Thresh", "Velkoz", "Xerath", "Yuumi", "Zilean", "Zyra"]
}

st.title("🏆 LoL AI Coach - V10 (Stable)")

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
    prompt = f"""
    Agis comme un analyste LoL.
    Alliés: {', '.join(my_team)} | Ennemis: {', '.join(enemy_team)}
    Pick: {recommended_pick} ({role}) | Winrate: {winrate:.1f}%
    Donne 3 points (Dégâts, Utilité, Matchup) sans blabla ni noms de sorts inventés.
    """
    try:
        response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}], options={'temperature': 0.3})
        return response['message']['content']
    except: return "Erreur Ollama."

# --- 2. SIDEBAR : GESTIONNAIRE DE POOL ---
st.sidebar.title("🎛️ Gestion d'Équipe")
st.sidebar.success(f"Data : {nb_matchs} matchs")

with st.sidebar.expander("🏊 MON CHAMPION POOL", expanded=False):
    st.write("Défins ici les champions que TES joueurs savent jouer.")
    MY_POOL = {}
    for role, defaults in USER_STARTER_POOL.items():
        valid_defaults = [c for c in defaults if c in full_champ_list]
        selected = st.multiselect(f"Pool {role}", full_champ_list, default=valid_defaults, key=f"pool_{role}")
        MY_POOL[role] = selected

# --- 3. BANS & FEARLESS ---
with st.expander("🚫 BANS & FEARLESS", expanded=True):
    c1, c2, c3 = st.columns([1,1,2])
    ban_list = champ_list_ui[1:]
    with c1: bans_blue = st.multiselect("Bans Blue", ban_list, key="bb", label_visibility="collapsed")
    with c2: bans_red = st.multiselect("Bans Red", ban_list, key="br", label_visibility="collapsed")
    with c3: fearless = st.multiselect("Fearless (Indisponibles)", ban_list, key="fl")

FORBIDDEN = set(bans_blue + bans_red + fearless)

# --- 4. DRAFT BOARD ---
st.divider()
col1, col2 = st.columns(2)
def p_menu(lbl, k, d="Gwenu"):
    # Si le défaut n'existe pas, on met index 0
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
    r1 = p_menu("Pick 1", "r1", "Zac")
    r2 = p_menu("Pick 2", "r2", "LeeSin")
    r3 = p_menu("Pick 3", "r3", "Ahri")
    r4 = p_menu("Pick 4", "r4", "Kaisa")
    r5 = p_menu("Pick 5", "r5", "Nami")

draft = [b1, b2, b3, b4, b5, r1, r2, r3, r4, r5]

# --- 5. BOUTON D'ANALYSE ---
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
        if wb > 52: 
            st.success("AVANTAGE BLUE")
            st.progress(int(wb))
        elif wr > 52: 
            st.error("AVANTAGE RED")
            st.progress(int(wb))
        else: 
            st.info("ÉQUILIBRÉ")
            st.progress(50)
    except: st.error("Calcul impossible")

# --- 6. BUILDER INTELLIGENT ---
st.subheader("🏗️ Assistant de Draft")

holes = [i for i, x in enumerate(draft) if x == "(A choisir)"]

if len(holes) > 0 and len(holes) <= 3:
    # A. CONFIGURATION DES ROLES
    c_roles = st.columns(len(holes))
    sel_roles = []
    team_color = "BLUE" if holes[0] < 5 else "RED"
    
    for idx, cr in enumerate(c_roles):
        midx = holes[idx]
        sname = f"{'Blue' if midx < 5 else 'Red'} P{midx%5+1}"
        with cr:
            # Clé unique pour éviter les conflits
            r = st.selectbox(f"Rôle {sname}", ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"], key=f"role_select_{idx}")
            sel_roles.append(r)

    # B. OPTIONS
    st.markdown("---")
    col_opt1, col_opt2 = st.columns([2, 1])
    with col_opt1:
        pool_mode = st.radio("Mode de Suggestion :", ["🔒 Mon Pool (Mes Joueurs)", "🌍 Méta Globale (Tout le jeu)"], horizontal=True)
    with col_opt2:
        st.write("")
        st.write("")
        use_llm = st.checkbox("Activer Coach (Ollama)", value=True, disabled=not OLLAMA_ACTIF)

    if st.button("✨ GÉNÉRER SUGGESTIONS"):
        prog = st.progress(0)
        lists = []
        for role in sel_roles:
            if "Mon Pool" in pool_mode:
                # Utilise ce qui est coché dans la Sidebar
                raw = MY_POOL.get(role, [])
                if not raw: st.warning(f"Ton pool {role} est vide ! Je prends tout.")
            else:
                # Utilise la grosse liste globale
                raw = GLOBAL_META_ROLES.get(role, []) 
            
            filt = [c for c in raw if c not in FORBIDDEN]
            lists.append(filt)

        if any(len(l) == 0 for l in lists):
            st.error("Aucun champion disponible avec ces filtres !")
            st.stop()

        combos = list(itertools.product(*lists))
        if len(combos) > 5000: combos = combos[:5000]

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

# 8. FINDER DE DUO (MEILLEURE SYNERGIE CIBLÉE)
# ==============================================================================
st.divider()
st.subheader("🤝 Finder de Duo (Qui jouer avec... ?)")
st.caption("Choisis un champion, l'IA cherche son meilleur partenaire statistique.")

col_find1, col_find2, col_find3 = st.columns([2, 1, 1])

with col_find1:
    # On propose tous les champions connus
    target_champ = st.selectbox("Je veux jouer...", champ_list_ui, index=champ_list_ui.index("Yasuo") if "Yasuo" in champ_list_ui else 0)

with col_find2:
    # Filtre pour ne chercher que des Junglers, des Supports, etc.
    wanted_role = st.selectbox("Je cherche un allié en...", ["TOUS", "TOP", "JUNGLE", "MID", "ADC", "SUPPORT"], index=2)

with col_find3:
    min_duo_games = st.number_input("Min. Games", min_value=1, value=3, step=1)

if st.button("🔍 TROUVER LE MEILLEUR DUO"):
    if target_champ == "(A choisir)":
        st.warning("Choisis d'abord un champion !")
    else:
        with st.spinner(f"Analyse des partenaires de {target_champ}..."):
            df_duo = pd.read_csv('mes_donnees_lol.csv')
            
            # Nettoyage
            for col in df_duo.columns:
                if 'Pick' in col: df_duo[col] = df_duo[col].apply(lambda x: NAME_MAPPING.get(x, x))
            
            # On définit la liste des candidats (soit TOUT le jeu, soit filtré par rôle)
            if wanted_role == "TOUS":
                candidates = full_champ_list # Tous les champions
            else:
                # On utilise la liste GLOBAL_META_ROLES si elle existe, sinon ROLES
                # (Assure-toi que GLOBAL_META_ROLES est bien défini dans ton code plus haut, sinon utilise DEFAULT_ROLES)
                try:
                    candidates = GLOBAL_META_ROLES.get(wanted_role, [])
                except:
                    candidates = DEFAULT_ROLES.get(wanted_role, [])

            results_duo = []

            # On parcourt tous les candidats possibles
            for partner in candidates:
                if partner == target_champ: continue # On ne peut pas jouer avec soi-même
                
                # On cherche les games où Target + Partner sont ENSEMBLE
                # (Soit les deux Blue, soit les deux Red)
                
                # Check Blue Side
                blue_tgt = df_duo[['Blue_Pick_1', 'Blue_Pick_2', 'Blue_Pick_3', 'Blue_Pick_4', 'Blue_Pick_5']].isin([target_champ]).any(axis=1)
                blue_prt = df_duo[['Blue_Pick_1', 'Blue_Pick_2', 'Blue_Pick_3', 'Blue_Pick_4', 'Blue_Pick_5']].isin([partner]).any(axis=1)
                games_blue = df_duo[blue_tgt & blue_prt]
                
                # Check Red Side
                red_tgt = df_duo[['Red_Pick_1', 'Red_Pick_2', 'Red_Pick_3', 'Red_Pick_4', 'Red_Pick_5']].isin([target_champ]).any(axis=1)
                red_prt = df_duo[['Red_Pick_1', 'Red_Pick_2', 'Red_Pick_3', 'Red_Pick_4', 'Red_Pick_5']].isin([partner]).any(axis=1)
                games_red = df_duo[red_tgt & red_prt]
                
                total_games = len(games_blue) + len(games_red)
                
                if total_games >= min_duo_games:
                    # Calcul Winrate
                    wins = games_blue['Blue_Win'].sum() + (len(games_red) - games_red['Blue_Win'].sum())
                    wr = (wins / total_games) * 100
                    results_duo.append((partner, wr, total_games))
            
            # Tri et Affichage
            if not results_duo:
                st.error(f"Aucune donnée pour {target_champ} avec un {wanted_role} (min {min_duo_games} games).")
            else:
                # Tri par Winrate décroissant
                results_duo.sort(key=lambda x: x[1], reverse=True)
                
                st.success(f"Top 5 Partenaires pour {target_champ} ({wanted_role}) :")
                
                for i, (name, score, count) in enumerate(results_duo[:5]):
                    cols = st.columns([1, 3, 1])
                    with cols[0]: st.markdown(f"**#{i+1} {name}**")
                    with cols[1]: st.progress(int(score))
                    with cols[2]: st.write(f"**{score:.1f}%** ({count} games)")
