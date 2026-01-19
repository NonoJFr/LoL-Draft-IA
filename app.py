# app.py
import streamlit as st #python -m streamlit run app.py

import pandas as pd
import itertools
import stats_tools as stt
# --- IMPORTS DE NOS FICHIERS ---
import constantes as c
import backend as bk
import coach

# --- CONFIGURATION ---
st.set_page_config(page_title="LoL AI Coach - Modular", layout="wide")
st.title("🏆 LoL AI Coach - V11 (Modular)")
#Image champion
def get_champ_icon(champ_name):
    # L'URL magique de Riot (Data Dragon)
    # Attention: Wukong s'appelle MonkeyKing dans les fichiers images
    img_name = "MonkeyKing" if champ_name == "Wukong" else champ_name
    img_name = "Renata" if champ_name == "Renata Glasc" else img_name # Fix Renata
    # On enlève les espaces et les apostrophes pour les images (ex: Lee Sin -> LeeSin, Kai'sa -> Kaisa)
    img_name = img_name.replace(" ", "").replace("'", "").replace(".", "")
    
    return f"https://ddragon.leagueoflegends.com/cdn/16.1.1/img/champion/{img_name}.png"

# --- CHARGEMENT DU MODÈLE (VIA BACKEND) ---
model, encoder, champ_list_ui, nb_matchs, full_champ_list = bk.train_model()
if model is None: st.stop()

# --- SIDEBAR : GESTIONNAIRE DE POOL ---
st.sidebar.title("🎛️ Gestion d'Équipe")
st.sidebar.success(f"Data : {nb_matchs} matchs")


with st.sidebar.expander("🏊 MON CHAMPION POOL", expanded=False):
    st.write("Défins ici les champions que TES joueurs savent jouer.")
    MY_POOL = {}
    for role, defaults in c.USER_STARTER_POOL.items():
        valid_defaults = [ch for ch in defaults if ch in full_champ_list]
        selected = st.multiselect(f"Pool {role}", full_champ_list, default=valid_defaults, key=f"pool_{role}")
        MY_POOL[role] = selected

# --- BANS & FEARLESS ---
with st.expander("🚫 BANS & FEARLESS", expanded=True):
    col1, col2, col3 = st.columns([1,1,2])
    ban_list = champ_list_ui[1:]
    with col1: bans_blue = st.multiselect("Bans Blue", ban_list, key="bb", label_visibility="collapsed")
    with col2: bans_red = st.multiselect("Bans Red", ban_list, key="br", label_visibility="collapsed")
    with col3: fearless = st.multiselect("Fearless (Indisponibles)", ban_list, key="fl")

FORBIDDEN = set(bans_blue + bans_red + fearless)

# --- DRAFT BOARD ---
st.divider()
c1, c2 = st.columns(2)

def p_menu(lbl, k, d="Gwenu"):
    i = champ_list_ui.index(d) if d in champ_list_ui else 0
    return st.selectbox(lbl, champ_list_ui, index=i, key=k)

with c1:
    st.header("🟦 BLUE SIDE")
    b1, b2, b3 = p_menu("Pick 1", "b1", "TahmKench"), p_menu("Pick 2", "b2", "(A choisir)"), p_menu("Pick 3", "b3", "Katarina")
    b4, b5 = p_menu("Pick 4", "b4", "Ezreal"), p_menu("Pick 5", "b5", "(A choisir)")

with c2:
    st.header("🟥 RED SIDE")
    r1, r2, r3 = p_menu("Pick 1", "r1", "Zaahen"), p_menu("Pick 2", "r2", "Jayce"), p_menu("Pick 3", "r3", "Ryze")
    r4, r5 = p_menu("Pick 4", "r4", "Yunara"), p_menu("Pick 5", "r5", "Lulu")

draft = [b1, b2, b3, b4, b5, r1, r2, r3, r4, r5]

# --- 5. BOUTON D'ANALYSE ---
st.divider()

# On compte les trous
nb_trous = draft.count("(A choisir)")

if st.button("🔮 ANALYSER LA DRAFT", type="primary", use_container_width=True):
    
    # --- A. PRÉDICTION DU GAGNANT (Seulement si complet) ---
    if nb_trous > 0:
        st.warning(f"⚠️ La draft n'est pas complète ({nb_trous} manquants). Le % de victoire global est masqué pour éviter les erreurs.")
    else:
        # On ne fait le calcul IA que si tout le monde est là
        try:
            d_nums = encoder.transform(draft[:5]).tolist() + encoder.transform(draft[5:]).tolist()
            cols = [col for col in pd.read_csv('mes_donnees_lol.csv', nrows=1).columns if 'Pick' in col]
            p = model.predict_proba(pd.DataFrame([d_nums], columns=cols))[0]
            wb, wr = p[1]*100, p[0]*100
            
            # Affichage Score
            ca, cb = st.columns(2)
            
            with ca:
                cols_imgs = st.columns(5)
                for i, ch in enumerate(draft[:5]):
                    img = get_champ_icon(ch)
                    if img: cols_imgs[i].image(img, use_container_width=True)
                st.metric("Blue", f"{wb:.1f}%")

            with cb:
                cols_imgs = st.columns(5)
                for i, ch in enumerate(draft[5:]):
                    img = get_champ_icon(ch)
                    if img: cols_imgs[i].image(img, use_container_width=True)
                st.metric("Red", f"{wr:.1f}%")
            
            if wb > 52: st.success("AVANTAGE BLUE"); st.progress(int(wb))
            elif wr > 52: st.error("AVANTAGE RED"); st.progress(int(wb))
            else: st.info("ÉQUILIBRÉ"); st.progress(50)
            st.write("---")
            st.subheader("🧠 Analyse de l'Expert IA")
        
            # 1. On récupère les données précises
            impacts = bk.get_draft_impact(draft[:5], draft[5:])
            blue_wr = {name: wr for name, wr, count, col in impacts if col == "Blue"}
            red_wr = {name: wr for name, wr, count, col in impacts if col == "Red"}
        
            # 2. On génère le rapport
            rapport = coach.generate_deep_analysis(draft[:5], draft[5:], blue_wr, red_wr, wb)
        
            # 3. Affichage stylé
            for line in rapport:
                if "Danger" in line or "Fragilité" in line or "Cible" in line:
                    st.error(line) # Rouge
                elif "Avantage" in line or "Solidité" in line or "Facteur X" in line:
                    st.success(line) # Vert
                elif "Niveau de Jeu" in line:
                    st.info(line) # Bleu
                else:
                    st.write(line) # Neutre

        except Exception as e: st.error(f"Calcul impossible : {e}")

    # --- B. RADAR & IMPACT (Même si incomplet) ---
    # C'est ici la correction : On utilise 'draft' (la vraie), pas 'safe' (la fausse avec Aatrox)
    
    st.write("---")
    c_radar, c_impact = st.columns([1, 1])
    
    with c_radar:
        st.subheader("🕸️ Comparatif Forces")
        # On passe la VRAIE liste. La fonction get_team_stats ignorera "(A choisir)"
        s_blue = stt.get_team_stats(draft[:5])
        s_red = stt.get_team_stats(draft[5:])
        st.plotly_chart(stt.draw_comparison_radar(s_blue, s_red), use_container_width=True)

    with c_impact:
        st.subheader("📊 Forme des Champions")
        # On passe la VRAIE liste. La fonction get_draft_impact ignorera "(A choisir)"
        impacts = bk.get_draft_impact(draft[:5], draft[5:])
        
        if not impacts:
            st.info("Ajoute des champions pour voir leurs stats.")
        else:
            impacts.sort(key=lambda x: x[1], reverse=True)
            for name, wr, count, color in impacts:
                if wr >= 53: bar_c = "green"
                elif wr <= 47: bar_c = "red"
                else: bar_c = "gray"
                
                txt, bar = st.columns([2, 3])
                with txt:
                    prefix = "🟦" if color == "Blue" else "🟥"
                    st.write(f"{prefix} **{name}**")
                    st.caption(f"{wr:.1f}% ({count} games)")
                with bar:
                    st.progress(int(wr))

# --- BUILDER INTELLIGENT ---
st.subheader("🏗️ Assistant de Draft")
holes = [i for i, x in enumerate(draft) if x == "(A choisir)"]

if 0 < len(holes) <= 3:
    c_roles = st.columns(len(holes))
    sel_roles = []
    team_color = "BLUE" if holes[0] < 5 else "RED"
    
    for idx, cr in enumerate(c_roles):
        midx = holes[idx]
        sname = f"{'Blue' if midx < 5 else 'Red'} P{midx%5+1}"
        with cr:
            r = st.selectbox(f"Rôle {sname}", ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"], key=f"role_select_{idx}")
            sel_roles.append(r)

    st.markdown("---")
    co1, co2 = st.columns([2, 1])
    with co1:
        pool_mode = st.radio("Mode :", ["🔒 Mon Pool", "🌍 Méta Globale"], horizontal=True)

    if st.button("✨ GÉNÉRER SUGGESTIONS"):
        prog = st.progress(0)
        lists = []
        for role in sel_roles:
            if "Mon Pool" in pool_mode:
                raw = MY_POOL.get(role, [])
                if not raw: st.warning(f"Pool {role} vide !")
            else:
                raw = c.GLOBAL_META_ROLES.get(role, [])
            
            # Filtre interdit + nettoyage nom
            filt = [c.clean_name(ch) for ch in raw if c.clean_name(ch) not in FORBIDDEN]
            lists.append(filt)

        if any(len(l) == 0 for l in lists): st.error("Aucun champion dispo !"); st.stop()

        combos = list(itertools.product(*lists))
        if len(combos) > 5000: combos = combos[:5000]

        sims, v_combos = [], []
        picked = [ch for ch in draft if ch != "(A choisir)"]
        excl = set(picked).union(FORBIDDEN)
        cols = [col for col in pd.read_csv('mes_donnees_lol.csv', nrows=1).columns if 'Pick' in col]

        for cmb in combos:
            if len(set(cmb)) != len(cmb): continue
            if any(ch in excl for ch in cmb): continue
            td = draft.copy()
            try:
                for i, ch in enumerate(cmb): td[holes[i]] = ch
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
            st.success(f"🏆 TOP : {' + '.join(best)} ({b_score:.1f}%)")
            
            current_team = [ch for ch in draft[:5] if ch != "(A choisir)"]
            if team_color == "BLUE": current_team.extend(best)
            st.info(coach.generate_pick_advice(
                pick_name=' + '.join(best), 
                role=', '.join(sel_roles),
                winrate=b_score,
                my_team=current_team
            ))
            with st.expander("Autres options"):
                for i, (n, s) in enumerate(res[1:11]):
                    st.write(f"**#{i+2}** {', '.join(n)} ({s:.1f}%)")
        else:
            st.error("Aucune combinaison trouvée.")
# 7. FINDER DE DUO
st.divider()
st.subheader("🤝 Finder de Duo")

c1, c2, c3 = st.columns([2,1,1])
with c1: 
    idx = champ_list_ui.index("Yasuo") if "Yasuo" in champ_list_ui else 0
    target = st.selectbox("Champion", champ_list_ui, index=idx)
with c2: 
    role = st.selectbox("Partenaire", ["TOUS", "TOP", "JUNGLE", "MID", "ADC", "SUPPORT"], index=2)
with c3: 
    min_g = st.number_input("Min Games", 1, 10, 3)

if st.button("🔍 CHERCHER"):
    with st.spinner("Calcul..."):
        # APPEL AU BACKEND (C'est propre !)
        # On passe les listes c.GLOBAL_META_ROLES et c.USER_STARTER_POOL pour qu'il sache où chercher
        res = bk.find_best_duo(target, role, min_g, c.GLOBAL_META_ROLES, c.USER_STARTER_POOL)
        
        if isinstance(res, str): # C'est une erreur
            st.error(f"Erreur : {res}")
        elif not res:
            st.warning("Aucun duo trouvé.")
        else:
            for i, (name, score, count) in enumerate(res):
                cols = st.columns([1, 4])
                with cols[0]: st.write(f"**#{i+1} {name}**")
                with cols[1]: st.progress(int(score)); st.caption(f"{score:.1f}% ({count} games)")