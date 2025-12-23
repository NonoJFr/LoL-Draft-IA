import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 1. CHARGEMENT DES DONNÉES
print("Chargement des données...")
# On lit ton fichier CSV
df = pd.read_csv('mes_donnees_lol.csv')

# 2. PRÉPARATION (TRADUCTION)
# L'IA ne sait pas lire "Aatrox". On doit créer un dictionnaire (Encodeur).
# On va dire à l'encodeur : "Apprends tous les noms de champions qui existent dans ce fichier".

encoder = LabelEncoder()

# On prend toutes les colonnes de champions (Blue 1-5 et Red 1-5)
all_champs = pd.concat([df[col] for col in df.columns if 'Pick' in col])
encoder.fit(all_champs) # L'encodeur apprend la liste (ex: Aatrox=0, Ahri=1...)

# Maintenant, on remplace les noms par des chiffres dans tout le tableau
for col in df.columns:
    if 'Pick' in col:
        df[col] = encoder.transform(df[col])

# 3. SÉPARATION
# X = Les données du match (les 10 champions)
# y = Le résultat (Qui a gagné ?)
X = df.drop('Blue_Win', axis=1)
y = df['Blue_Win']

# On coupe en deux : 80% pour s'entraîner (Train), 20% pour passer l'examen (Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. ENTRAÎNEMENT DU MODÈLE
print("Entraînement de l'IA en cours...")
# On utilise une "Forêt Aléatoire". C'est excellent pour les données de ce type.
model = RandomForestClassifier(n_estimators=100) 
model.fit(X_train, y_train) # C'est ici que la magie opère !

# 5. ÉVALUATION
predictions = model.predict(X_test)
precision = accuracy_score(y_test, predictions)
print(f"Précision de l'IA : {precision * 100:.2f}%")

# --- BONUS : TESTER UNE DRAFT (CORRIGÉ) ---
print("\n--- TEST DE DRAFT ---")
# Tes champions choisis (Attention à l'orthographe exacte ! "Zaahen" n'existe pas, attention aux crashs)
blue_team = ['Malphite', 'Sejuani', 'Katarina', 'Yunara', 'Braum']
red_team =  ['Yasuo', 'Diana', 'Veigar', 'Ezreal', 'Lulu'] 
# J'ai remplacé Zaahen par Ornn pour l'exemple, car Zaahen fera planter si l'IA ne connait pas.

print(f"Blue: {blue_team}")
print(f"Red:  {red_team}")

try:
    # 1. On transforme les noms en numéros
    draft_numerique = []
    draft_numerique.extend(encoder.transform(blue_team))
    draft_numerique.extend(encoder.transform(red_team))

    # 2. ON CRÉE UN PETIT DATAFRAME (C'est ça qui corrige l'avertissement rouge !)
    # On reprend les mêmes noms de colonnes que le fichier d'entraînement
    colonnes = [col for col in df.columns if 'Pick' in col]
    draft_df = pd.DataFrame([draft_numerique], columns=colonnes)

    # 3. Prédiction
    prediction = model.predict(draft_df)
    proba = model.predict_proba(draft_df)

    gagnant = "BLUE SIDE" if prediction[0] == 1 else "RED SIDE"
    confiance = proba[0][prediction[0]] * 100

    print(f"L'IA prédit une victoire du : {gagnant}")
    print(f"Confiance : {confiance:.2f}%")

except ValueError as e:
    print("\nERREUR CRITIQUE : Un champion est mal orthographié ou inconnu !")
    print(f"Détail : {e}")
    print("Conseil : Vérifie que le champion existe bien dans ton fichier 'mes_donnees_lol.csv'.")