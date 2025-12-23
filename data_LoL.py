from riotwatcher import LolWatcher, ApiError
import pandas as pd
import requests
import time # Indispensable pour les pauses

# --- 1. CONFIGURATION ---
api_key = 'MA CLE'  # <--- REMETS TA CLÉ API ICI !
watcher = LolWatcher(api_key)
region = 'euw1'
region_account = 'europe'

# Liste des joueurs à espionner (Pseudo, Tag)
# Tu peux en ajouter d'autres !
targets = [
    ('NPC Corsikanet', '7350'), # Toplaner
    ('int like Neron', 'NBO'),  # Jungler
    ('NonoJ', 'WIN'),   # Midlaner
    ('NPC Peraste', '9447'),    # Adc 
    ('ωee ωoo ωee', 'Yuumi')    # Support
]

nb_matchs_par_joueur = 40 # 40 x 3 joueurs = 120 matchs au total

# --- 2. LE MOTEUR DE RÉCOLTE ---
all_data_list = []
matchs_deja_vus = set() # Pour éviter les doublons (matchs joués ensemble)

print(f"Démarrage de la récolte sur {len(targets)} joueurs...")

for pseudo, tag in targets:
    print(f"\n--- Récupération pour : {pseudo}#{tag} ---")
    
    try:
        # A. Trouver le PUUID (Méthode requests)
        url = f"https://{region_account}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{pseudo}/{tag}"
        response = requests.get(url, headers={"X-Riot-Token": api_key})
        
        if response.status_code != 200:
            print(f"Joueur introuvable ou erreur API : {response.status_code}")
            continue # On passe au joueur suivant

        me = response.json()
        my_puuid = me['puuid']

        # B. Récupérer la liste des matchs
        my_matches = watcher.match.matchlist_by_puuid(region, my_puuid, count=nb_matchs_par_joueur, queue=420)
        
        # C. Analyser chaque match
        for i, match_id in enumerate(my_matches):
            
            # Vérification anti-doublon
            if match_id in matchs_deja_vus:
                print(f"Match {i+1}/{nb_matchs_par_joueur} déjà enregistré (doublon).")
                continue

            try:
                # PAUSE OBLIGATOIRE (Rate Limit)
                # Riot autorise 100 requêtes toutes les 2 minutes.
                # 1.2 seconde de pause est la sécurité parfaite.
                time.sleep(0.5) 

                match_detail = watcher.match.by_id(region, match_id)
                participants = match_detail['info']['participants']
                
                row = {} 
                blue_team = []
                red_team = []
                blue_win = False

                for p in participants:
                    champ_name = p['championName']
                    if p['teamId'] == 100:
                        blue_team.append(champ_name)
                        if p['win']: blue_win = True
                    else:
                        red_team.append(champ_name)

                # On vérifie que le match est valide (5v5)
                if len(blue_team) == 5 and len(red_team) == 5:
                    # Enregistrement
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
                    
                    all_data_list.append(row)
                    matchs_deja_vus.add(match_id) # On le note comme "vu"
                    print(f"Match {i+1}/{nb_matchs_par_joueur} ajouté (Total: {len(all_data_list)})")
                
            except Exception as e:
                print(f"Erreur lecture match : {e}")
                continue

    except Exception as e:
        print(f"Erreur générale sur le joueur {pseudo} : {e}")

# --- 3. SAUVEGARDE FINALE ---
print("\n--- FIN DU TRAITEMENT ---")
if len(all_data_list) > 0:
    df = pd.DataFrame(all_data_list)
    df.to_csv('mes_donnees_lol.csv', index=False)
    print(f"BRAVO ! Fichier 'mes_donnees_lol.csv' mis à jour avec {len(all_data_list)} matchs.")
else:
    print("Zut, aucun match récupéré. Vérifie ta clé API.")