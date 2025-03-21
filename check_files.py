import os

files_to_check = [
    'fichier ancien/users.json',
    'fichier ancien/cards.json',
    'fichier ancien/selected_cards.json',
    'fichier ancien/test_jeux_tt2.py',
    'fichier ancien/gamelogic.py',
    'fichier ancien/ai_logic.py',
    'fichier ancien/drawing.py',
    'fichier ancien/capture_manager.py',
    'fichier ancien/utils.py',
    'fichier ancien/rules.py',
    'fichier ancien/Img',
    'fichier ancien/bgm.mp3',
    'fichier ancien/sound-turn.wav'
]

missing_files = [file for file in files_to_check if not os.path.exists(file)]

if missing_files:
    print("Fichiers manquants :")
    for file in missing_files:
        print(f"- {file}")
else:
    print("Tous les fichiers nécessaires sont présents.")
