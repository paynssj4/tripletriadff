import importlib
import os
from modulefinder import ModuleFinder

finder = ModuleFinder()
modules_to_check = [
    "pygame", "json", "os", "sys", "time", "random", "asyncio", "zmq",
    "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets", "irc.client"
]
print("Modules importés :")
for name, mod in finder.modules.items():
    print(f"{name}: {mod.__file__}")
missing_modules = []

for module in modules_to_check:
    if module in finder.badmodules.keys():
        try:
            importlib.import_module(module)
        except ImportError:
            missing_modules.append(module)

if missing_modules:
    print("Modules manquants :")
    for module in missing_modules:
        print(f"- {module}")
else:
    print("Tous les modules nécessaires sont installés.")

# Dossier racine de votre projet
PROJECT_DIR = "D:/test jeux tt/Nouveau dossier"

# Extensions de fichiers à inclure
INCLUDE_EXTENSIONS = [".py", ".json", ".png", ".jpg", ".jpeg", ".wav", ".mp3"]

# Liste des fichiers nécessaires
def find_files_to_include(root_dir, extensions):
    files_to_include = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                files_to_include.append(os.path.join(root, file))
    return files_to_include

# Générer la liste des fichiers nécessaires
files = find_files_to_include(PROJECT_DIR, INCLUDE_EXTENSIONS)

# Afficher les fichiers trouvés
print("Fichiers nécessaires pour la compilation :")
for file in files:
    print(file)

# Sauvegarder la liste dans un fichier texte (optionnel)
with open("files_to_include.txt", "w") as f:
    for file in files:
        f.write(file + "\n")
