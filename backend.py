import pandas as pd
import requests
import streamlit as st
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from constantes import clean_name, NAME_MAPPING
import backend as bk # <--- AJOUTE CET IMPORT TOUT EN HAUT DU FICHIER

@st.cache_resource
def train_model():
    """
    Charge les données, nettoie les noms et entraîne le modèle XGBoost.
    """
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
        
        model = XGBClassifier(n_estimators=300, learning_rate=0.05, max_depth=4, random_state=42, n_jobs=-1)
        model.fit(X, y)
        
        return model, encoder, champ_list_ui, len(df), clean_list_riot
    
    except Exception as e:
        st.error(f"Erreur technique dans backend.py : {e}")
        return None, None, [], 0, []

def find_best_duo(target_champ, wanted_role, min_games, global_roles, default_roles):
    """
    Calcule les meilleurs partenaires pour un champion donné.
    """
    try:
        df = pd.read_csv('mes_donnees_lol.csv')
        for col in df.columns:
            if 'Pick' in col: df[col] = df[col].apply(lambda x: NAME_MAPPING.get(x, x))
            
        if wanted_role == "TOUS":
            candidates = set(df[['Blue_Pick_1', 'Blue_Pick_2', 'Blue_Pick_3', 'Blue_Pick_4', 'Blue_Pick_5']].values.flatten())
        else:
            candidates = global_roles.get(wanted_role, default_roles.get(wanted_role, []))

        results = []
        mask_target = df.apply(lambda x: target_champ in x.values, axis=1)
        df_target = df[mask_target]

        for partner in candidates:
            if partner == target_champ: continue
            
            mask_partner = df_target.apply(lambda x: partner in x.values, axis=1)
            games_together = df_target[mask_partner]
            
            valid_games = []
            wins = 0
            
            for row in games_together.itertuples(index=False):
                blue = {row.Blue_Pick_1, row.Blue_Pick_2, row.Blue_Pick_3, row.Blue_Pick_4, row.Blue_Pick_5}
                red = {row.Red_Pick_1, row.Red_Pick_2, row.Red_Pick_3, row.Red_Pick_4, row.Red_Pick_5}
                
                is_blue_duo = (target_champ in blue) and (partner in blue)
                is_red_duo = (target_champ in red) and (partner in red)
                
                if is_blue_duo:
                    valid_games.append(1)
                    if row.Blue_Win == 1: wins += 1
                elif is_red_duo:
                    valid_games.append(1)
                    if row.Blue_Win == 0: wins += 1 
            
            total = len(valid_games)
            if total >= min_games:
                wr = (wins / total) * 100
                results.append((partner, wr, total))
                
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:5]

    except Exception as e:
        return str(e)

def get_draft_impact(blue_team, red_team):
    """
    Calcule le winrate moyen de chaque champion de la draft dans la base de données actuelle.
    C'est cette fonction qui manquait !
    """
    try:
        df = pd.read_csv('mes_donnees_lol.csv')
        for col in df.columns:
            if 'Pick' in col: df[col] = df[col].apply(lambda x: NAME_MAPPING.get(x, x))
        
        impact_data = []
        
        # On fusionne les deux listes pour analyser tout le monde
        all_champs = blue_team + red_team
        
        for champ in all_champs:
            if champ == "(A choisir)": continue
            
            # On cherche toutes les games où ce champion est présent
            mask = df.apply(lambda x: champ in x.values, axis=1)
            df_champ = df[mask]
            
            total = len(df_champ)
            if total < 5:
                # Pas assez de données pour juger
                impact_data.append((champ, 50.0, 0, "Neutre"))
                continue
                
            # Calcul du Winrate spécifique à ce champion
            wins = 0
            for row in df_champ.itertuples(index=False):
                blue_side = {row.Blue_Pick_1, row.Blue_Pick_2, row.Blue_Pick_3, row.Blue_Pick_4, row.Blue_Pick_5}
                
                # Si le champion était chez les Bleus et qu'ils ont gagné
                if champ in blue_side and row.Blue_Win == 1: wins += 1
                # Si le champion était chez les Rouges et qu'ils ont gagné (Blue_Win = 0)
                elif champ not in blue_side and row.Blue_Win == 0: wins += 1 
            
            wr = (wins / total) * 100
            team_color = "Blue" if champ in blue_team else "Red"
            impact_data.append((champ, wr, total, team_color))
            
        return impact_data

    except Exception as e:
        # En cas d'erreur, on renvoie une liste vide pour ne pas faire planter l'appli
        return []
def get_head_to_head_stats(champ_a, champ_b):
    """
    Calcule le taux de victoire de Champ A lorsqu'il joue CONTRE Champ B.
    Retourne : (Winrate de A, Nombre de matchs)
    """
    try:
        df = pd.read_csv('mes_donnees_lol.csv')
        # On ne nettoie pas tout le DF pour gagner du temps, on suppose les noms corrects
        # ou on le fait à la volée si besoin (ici on suppose que l'input vient déjà du code propre)
        
        # 1. Cas : A est Blue, B est Red
        # On cherche les lignes où A est dans les colonnes Blue ET B dans les colonnes Red
        blue_cols = ['Blue_Pick_1', 'Blue_Pick_2', 'Blue_Pick_3', 'Blue_Pick_4', 'Blue_Pick_5']
        red_cols = ['Red_Pick_1', 'Red_Pick_2', 'Red_Pick_3', 'Red_Pick_4', 'Red_Pick_5']
        
        # Masque : A est Blue
        mask_a_blue = df[blue_cols].isin([champ_a]).any(axis=1)
        # Masque : B est Red
        mask_b_red = df[red_cols].isin([champ_b]).any(axis=1)
        
        # Matchs A vs B
        matchs_avsb = df[mask_a_blue & mask_b_red]
        wins_a_blue = matchs_avsb['Blue_Win'].sum()
        total_avsb = len(matchs_avsb)
        
        # 2. Cas : A est Red, B est Blue
        mask_a_red = df[red_cols].isin([champ_a]).any(axis=1)
        mask_b_blue = df[blue_cols].isin([champ_b]).any(axis=1)
        
        matchs_bvsa = df[mask_a_red & mask_b_blue]
        # A gagne si Blue_Win est 0
        wins_a_red = len(matchs_bvsa) - matchs_bvsa['Blue_Win'].sum()
        total_bvsa = len(matchs_bvsa)
        
        # Total
        grand_total = total_avsb + total_bvsa
        total_wins = wins_a_blue + wins_a_red
        
        if grand_total == 0:
            return None, 0
            
        wr = (total_wins / grand_total) * 100
        return wr, grand_total

    except:
        return None, 0
def get_duo_winrate(champ_a, champ_b):
    """
    Calcule le taux de victoire quand A et B sont dans la MÊME équipe.
    """
    try:
        df = pd.read_csv('mes_donnees_lol.csv')
        # Nettoyage rapide (pas besoin de tout si le code appelant est propre)
        
        # Cas 1 : Ils sont tous les deux Blue
        blue_cols = ['Blue_Pick_1', 'Blue_Pick_2', 'Blue_Pick_3', 'Blue_Pick_4', 'Blue_Pick_5']
        mask_blue = df[blue_cols].isin([champ_a]).any(axis=1) & df[blue_cols].isin([champ_b]).any(axis=1)
        games_blue = df[mask_blue]
        wins_blue = games_blue['Blue_Win'].sum()
        
        # Cas 2 : Ils sont tous les deux Red
        red_cols = ['Red_Pick_1', 'Red_Pick_2', 'Red_Pick_3', 'Red_Pick_4', 'Red_Pick_5']
        mask_red = df[red_cols].isin([champ_a]).any(axis=1) & df[red_cols].isin([champ_b]).any(axis=1)
        games_red = df[mask_red]
        wins_red = len(games_red) - games_red['Blue_Win'].sum()
        
        total = len(games_blue) + len(games_red)
        total_wins = wins_blue + wins_red
        
        if total < 3: return None, 0 # Pas assez de données
        
        return (total_wins / total) * 100, total
    except:
        return None, 0