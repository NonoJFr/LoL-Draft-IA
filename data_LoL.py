mport requests
import pandas as pd
import time
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
API_KEY = 'st.secrets["RIOT_API_KEY"]'  # <--- REMETS TA CLÉ API ICI !
REGION = 'euw1'
REGION_MASS = 'europe'

# Combien de joueurs du TOP Challenger on scanne ? (Max 300)
# Pour une clé DEV (gratuite), mets 30 à 50 sinon ça va prendre 4 heures.
NB_JOUEURS_A_SCANNER = 40 

# Combien de matchs récents par joueur ?
MATCHS_PAR_JOUEUR = 20

# Date de début de la Saison (ou "il y a 2 semaines" pour être sûr d'avoir la méta actuelle)
# On prend les matchs joués depuis 14 jours seulement.
START_TIME = int((datetime.now() - timedelta(days=14)).timestamp())

# --- FONCTIONS UTILES ---
def get_headers():
    return {"X-Riot-Token": API_KEY}

def save_checkpoint(data, filename='mes_donnees_lol.csv'):
    """Sauvegarde incrémentale pour ne pas tout perdre"""
    if not data: return
    df = pd.DataFrame(data)
    # Si le fichier existe, on n'écrit pas l'en-tête (header)
    hdr = not os.path.exists(filename)
    df.to_csv(filename, mode='a', header=hdr, index=False)
    print(f"💾 Sauvegarde intermédiaire : {len(data)} matchs ajoutés.")

# --- 1. RÉCUPÉRER LE LADDER CHALLENGER ---
print(f"📡 Connexion au serveur {REGION} pour récupérer le Top Ladder...")

url_challenger = f"https://{REGION}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
response = requests.get(url_challenger, headers=get_headers())

if response.status_code != 200:
    print(f"❌ Erreur API ({response.status_code}). Vérifie ta clé API.")
    exit()

entries = response.json()['entries']
# On trie par LP (League Points) pour avoir les meilleurs en premier
entries.sort(key=lambda x: x['leaguePoints'], reverse=True)

top_players = entries[:NB_JOUEURS_A_SCANNER]
print(f"✅ Liste récupérée : {len(top_players)} joueurs Challenger prêts à être scannés.")

# --- 2. LA BOUCLE D'ASPIRATION (CORRIGÉE & ROBUSTE) ---
matchs_deja_vus = set()
buffer_data = [] 
match_count_session = 0

if os.path.exists('mes_donnees_lol.csv'):
    try:
        # On lit juste pour éviter de planter, le tri se fera à la fin
        existing_df = pd.read_csv('mes_donnees_lol.csv')
    except: pass

print("\n🚀 Démarrage de la collecte massive...")

for i, player in enumerate(top_players):
    
    # --- DEBUG : Affiche les infos du premier joueur pour vérifier ---
    if i == 0:
        print(f"🔍 DEBUG - Clés reçues de Riot : {list(player.keys())}")

    try:
        # ÉTAPE A : TROUVER LE PUUID (L'IDENTIFIANT UNIQUE)
        puuid = None
        
        # Cas 1 : Riot nous donne directement le PUUID (Nouveau système)
        if 'puuid' in player:
            puuid = player['puuid']
            
        # Cas 2 : Riot nous donne le SummonerID (Ancien système), on doit le convertir
        elif 'summonerId' in player:
            summoner_id = player['summonerId']
            print(f"\n👤 Joueur {i+1}/{len(top_players)} (SummonerID: {summoner_id[:8]}...)")
            
            url_sum = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}"
            r_sum = requests.get(url_sum, headers=get_headers())
            
            if r_sum.status_code == 429:
                print("⏳ Trop rapide ! Pause 10 sec...")
                time.sleep(10)
                r_sum = requests.get(url_sum, headers=get_headers())
                
            if r_sum.status_code == 200:
                puuid = r_sum.json()['puuid']
            else:
                print(f"⚠️ Impossible de convertir l'ID : {r_sum.status_code}")
                continue

        else:
            print(f"❌ Joueur {i+1} ignoré : Pas d'ID valide trouvé.")
            continue

        # Si on n'a pas de PUUID à ce stade, on passe
        if not puuid:
            print("❌ PUUID non trouvé.")
            continue

        # ÉTAPE B : RÉCUPÉRER LES MATCHS
        # (Le reste du code est identique, mais sécurisé dans le Try)
        url_matchs = f"https://{REGION_MASS}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {
            "queue": 420, 
            "start": 0,
            "count": MATCHS_PAR_JOUEUR,
            "startTime": START_TIME 
        }
        r_ids = requests.get(url_matchs, headers=get_headers(), params=params)
        
        if r_ids.status_code == 429:
            time.sleep(5)
            r_ids = requests.get(url_matchs, headers=get_headers(), params=params)

        if r_ids.status_code != 200:
            print(f"⚠️ Erreur liste matchs : {r_ids.status_code}")
            continue

        match_ids = r_ids.json()
        
        # ÉTAPE C : ANALYSER CHAQUE MATCH
        for mid in match_ids:
            if mid in matchs_deja_vus: continue
            
            time.sleep(1.2) # Respect API
            
            url_detail = f"https://{REGION_MASS}.api.riotgames.com/lol/match/v5/matches/{mid}"
            r_det = requests.get(url_detail, headers=get_headers())
            
            if r_det.status_code == 429:
                print("🛑 Rate Limit Riot. Pause 30s...")
                time.sleep(30)
                r_det = requests.get(url_detail, headers=get_headers())
            
            if r_det.status_code != 200: continue
            
            data = r_det.json()
            info = data['info']
            
            if info['gameDuration'] < 900: continue
            
            row = {}
            blue_team = []
            red_team = []
            blue_win = False
            
            for p in info['participants']:
                if p['teamId'] == 100:
                    blue_team.append(p['championName'])
                    if p['win']: blue_win = True
                else:
                    red_team.append(p['championName'])
            
            if len(blue_team) == 5 and len(red_team) == 5:
                row['Blue_Pick_1'] = blue_team[0]
                row['Blue_Pick_2'] = blue_team[1]
                row['Blue_Pick_3'] = blue_team[2]
                row['Blue_Pick_4'] = blue_team[3]
                row['Blue_Pick_5'] = blue_team[4]
                row['Red_Pick_1'] = red_team[0]
                row['Red_Pick_2'] = red_team[1]
                row['Red_Pick_3'] = red_team[2]
                row['Red_Pick_4'] = red_team[3]
                row['Red_Pick_5'] = red_team[4]
                row['Blue_Win'] = 1 if blue_win else 0
                
                buffer_data.append(row)
                matchs_deja_vus.add(mid)
                match_count_session += 1
                print(f"   + Match ajouté (Total session: {match_count_session})")
        
        # Sauvegarde intermédiaire
        if len(buffer_data) >= 50:
            save_checkpoint(buffer_data)
            buffer_data = [] 
            
    except Exception as e:
        print(f"⚠️ Erreur générale sur ce joueur : {e}")
        time.sleep(1)

