import importlib

modules_to_check = [
    "pygame", "json", "os", "sys", "time", "random", "asyncio", "zmq",
    "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets", "irc.client"
]

missing_modules = []

for module in modules_to_check:
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
