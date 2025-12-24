import pandas as pd
import requests # Nécessaire pour avoir la liste officielle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 1. CHARGEMENT DES DONNÉES
print("Chargement des données...")
try:
    df = pd.read_csv('mes_donnees_lol.csv')
except FileNotFoundError:
    print("Erreur : Le fichier 'mes_donnees_lol.csv' n'existe pas. Lance d'abord data_lol.py !")
    exit()

# 2. PRÉPARATION INTELLIGENTE (La correction est ici)
print("Récupération de la liste officielle des champions...")

# On demande à Riot la liste de TOUS les champions existants
# Comme ça, l'IA connait même les champions qui ne sont pas dans ton fichier CSV
try:
    version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    latest_version = requests.get(version_url).json()[0]
    ddragon_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
    data_champions = requests.get(ddragon_url).json()
    
    # Voici la liste complète de Aatrox à Zyra
    liste_officielle = list(data_champions['data'].keys())
    
    # On ajoute manuellement 'Fiddlesticks' car Riot l'écrit parfois différemment
    if 'Fiddlesticks' not in liste_officielle: 
        liste_officielle.append('Fiddlesticks')

except Exception as e:
    print(f"Attention : Impossible de joindre Riot ({e}). On utilise seulement les champions du CSV.")
    # Si pas d'internet, on fait comme avant
    liste_officielle = pd.concat([df[col] for col in df.columns if 'Pick' in col]).unique()

# On configure l'encodeur avec la liste COMPLÈTE
encoder = LabelEncoder()
encoder.fit(liste_officielle)

# On transforme tout le tableau en chiffres
# On utilise une astuce pour ignorer les erreurs si un vieux champion bizarre traîne
for col in df.columns:
    if 'Pick' in col:
        # On ne garde que les champions connus de la liste officielle pour éviter les bugs
        df = df[df[col].isin(liste_officielle)]
        df[col] = encoder.transform(df[col])

# 3. SÉPARATION
X = df.drop('Blue_Win', axis=1)
y = df['Blue_Win']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. ENTRAÎNEMENT
print(f"Entraînement sur {len(df)} matchs...")
model = RandomForestClassifier(n_estimators=200, random_state=42) # 200 arbres pour être plus précis
model.fit(X_train, y_train)

# 5. ÉVALUATION
predictions = model.predict(X_test)
precision = accuracy_score(y_test, predictions)
print(f"Précision de l'IA : {precision * 100:.2f}%")

# --- TEST DE DRAFT ---
print("\n--- TEST DE DRAFT ---")
# Tu peux maintenant mettre n'importe quel champion, ça ne plantera plus !
blue_team = ['Malphite', 'Sejuani', 'Katarina', 'Yunara', 'Braum']
red_team =  ['Yone', 'Diana', 'Veigar', 'Ezreal', 'Lulu']

print(f"Blue: {blue_team}")
print(f"Red:  {red_team}")

try:
    draft_numerique = []
    # On transforme les noms
    draft_numerique.extend(encoder.transform(blue_team))
    draft_numerique.extend(encoder.transform(red_team))

    # On crée le DataFrame propre
    colonnes = [col for col in df.columns if 'Pick' in col]
    draft_df = pd.DataFrame([draft_numerique], columns=colonnes)

    # Prédiction
    prediction = model.predict(draft_df)
    proba = model.predict_proba(draft_df)

    gagnant = "BLUE SIDE" if prediction[0] == 1 else "RED SIDE"
    confiance = proba[0][prediction[0]] * 100

    print(f"L'IA prédit une victoire du : {gagnant}")
    print(f"Confiance : {confiance:.2f}%")

except ValueError as e:
    print(f"\nErreur : Un nom de champion est incorrect (Vérifie l'orthographe exacte, ex: 'Wukong' s'écrit 'MonkeyKing' dans l'API).")
    print(f"Détail : {e}")