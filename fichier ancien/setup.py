import subprocess
import os

# Charger la liste des fichiers nécessaires
with open("files_to_include.txt", "r") as f:
    files = f.read().splitlines()

# Construire la commande PyInstaller
command = ["pyinstaller", "--onefile", "irc_client7.py"]
for file in files:
    # Ajouter chaque fichier avec l'option --add-data
    relative_path = os.path.relpath(file, "D:/test jeux tt/Nouveau dossier")
    command.append(f"--add-data={file};{relative_path}")

# Exécuter la commande
subprocess.run(command)