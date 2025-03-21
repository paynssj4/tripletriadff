# Triple Triad Client

Bienvenue sur le projet Triple Triad Client ! Ce projet combine un client de chat avec un jeu de cartes Triple Triad, le tout intégré dans une interface graphique conviviale.

## Description

Ce projet est composé de deux parties principales :

1.  **Client de Chat et Gestion de Deck (`irc_client7.py`) :**
    *   Permet aux utilisateurs de se connecter à un serveur de chat via le protocole ZeroMQ.
    *   Possibilité d'envoyer des messages publics et privés.
    *   Gestion des utilisateurs connectés.
    *   Système d'authentification par nom d'utilisateur.
    *   Intégration d'un système d'inventaire et de gestion de deck pour le jeu Triple Triad.
    *   Possibilité de défier d'autres utilisateurs en duel.
    *   Gestion de l'or (monnaie virtuelle).
    *   Sauvegarde et chargement du deck de l'utilisateur.
    *   Gestion de la sélection des cartes.
    *   Possibilité de lancer une partie solo.

2.  **Jeu Triple Triad (`test_jeux_tt2.py`) :**
    *   Implémentation du jeu de cartes Triple Triad.
    *   Possibilité de jouer en solo contre une IA.
    *   Gestion des règles du jeu.
    *   Interface graphique pour le plateau de jeu.
    *   Gestion des cartes et de leurs attributs.
    *   Gestion des sons.

## Fonctionnalités

*   **Chat :** Communiquez avec d'autres joueurs en temps réel.
*   **Triple Triad :** Jouez au célèbre jeu de cartes.
*   **Inventaire :** Gérez votre collection de cartes.
*   **Gestion de Deck :** Créez et personnalisez votre deck de 5 cartes.
*   **Défis :** Défiez d'autres joueurs en duel.
*   **Partie Solo :** Affrontez une IA pour vous entraîner.
*   **Gestion de l'or :** Gérer votre argent virtuel.
*   **Sauvegarde :** Sauvegarder votre deck et votre sélection de cartes.
*   **Interface graphique :** Interface utilisateur intuitive et agréable.
*   **Gestion des sons :** Des sons pour une meilleure immersion.

## Règles du Jeu

Le jeu Triple Triad implémente plusieurs règles :

1. **Base :** Les cartes sont placées sur le plateau et les captures sont effectuées en fonction des chiffres sur les cartes adjacentes.
2. **Identique :** Si deux cartes adjacentes ont le même chiffre sur les côtés en contact, elles sont capturées.
3. **Plus :** Si la somme des chiffres de deux cartes adjacentes est égale à la somme des chiffres de deux autres cartes adjacentes, elles sont capturées.
4. **Aléatoire + Combo :** Les cartes sont distribuées aléatoirement et les captures en chaîne sont possibles.

## Défauts Actuels et Améliorations en Cours

* **Captures en Cascade :** Les captures en cascade fonctionnent dans toutes les règles au lieu d'être appliquées uniquement à la règle "Aléatoire + Combo".
* **Rotation des Cartes :** La rotation des cartes sera modifiée pour une meilleure animation.
* **Logique du Jeu :** La logique du jeu est en cours d'amélioration pour corriger les bugs et améliorer l'expérience de jeu.
* **Interface de Chat :** L'interface pour le chat est en cours d'amélioration pour une meilleure convivialité et fonctionnalité.

## Installation

1.  **Prérequis :**
    *   Python 3.x
    *   Les librairies suivantes :
        *   `PyQt5`
        *   `pygame`
        *   `zmq`
        *   `irc`
        *   `json`
        *   `logging`
        *   `os`
        *   `random`
        *   `socket`
        *   `subprocess`
        *   `sys`
        *   `threading`
        *   `asyncio`
        *   `PIL`

    Vous pouvez les installer avec pip :

    ```bash
    pip install PyQt5 pygame pyzmq irc Pillow
    ```

2.  **Téléchargement :**
    *   Téléchargez les fichiers du projet.

3.  **Exécution :**
    *   Naviguez jusqu'au répertoire du projet dans votre terminal.
    *   Exécutez le client avec la commande :

    ```bash
    python irc_client7.py
    ```

    *   Pour lancer une partie solo, vous devez d'abord sélectionner 5 cartes dans l'onglet "Inventaire" et cliquer sur "Sauvegarder". Ensuite, cliquez sur "Démarrer une partie solo".

## Structure du projet

*   `irc_client7.py` : Fichier principal du client de chat et de l'interface graphique.
*   `test_jeux_tt2.py` : Fichier principal du jeu Triple Triad.
*   `card.py` : Classe pour la gestion des cartes.
*   `users.json` : Fichier de données pour les utilisateurs (deck, or).
*   `cards.json` : Fichier de données pour les cartes.
*   `selected_cards.json` : Fichier de données pour les cartes sélectionnées.
*   `Img/` : Dossier contenant les images des cartes.
*   `ai_logic.py` : Fichier pour la logique de l'IA.
*   `capture_manager.py` : Fichier pour la gestion des captures.
*   `drawing.py` : Fichier pour la gestion des dessins.
*   `gamelogic.py` : Fichier pour la logique du jeu.
*   `inventory_manager.py` : Fichier pour la gestion de l'inventaire.
*   `rules.py` : Fichier pour les règles du jeu.
*   `ai.py` : Fichier pour l'IA.
*   `utils.py` : Fichier pour les fonctions utilitaires.
*   `bgm.mp3` : Fichier de musique de fond.
*   `sound-turn.wav` : Fichier de son pour le tour.
*   `irc_client7.spec` : Fichier de configuration pour PyInstaller.

## Utilisation

1.  **Lancement :** Exécutez `irc_client7.py`.
2.  **Authentification :** Entrez votre nom d'utilisateur.
3.  **Chat :** Utilisez la zone de texte pour envoyer des messages.
4.  **Inventaire :** Allez dans l'onglet "Inventaire" pour voir vos cartes.
5.  **Sélection de cartes :** Cliquez sur les cartes pour les sélectionner (5 maximum).
6.  **Sauvegarde :** Cliquez sur "Sauvegarder" pour enregistrer votre sélection.
7.  **Partie Solo :** Cliquez sur "Démarrer une partie solo" pour lancer une partie contre l'IA.
8.  **Défis :** Faites un clic droit sur un utilisateur dans la liste pour le défier.

## Compilation avec PyInstaller

Le fichier `irc_client7.spec` est fourni pour vous aider à compiler le projet avec PyInstaller.

1.  **Installation de PyInstaller :**

    ```bash
    pip install pyinstaller
    ```

2.  **Compilation :**

    ```bash
    pyinstaller irc_client7.spec
    ```

    Ou pour compiler directement :
    ```bash
    python irc_client7.py compile
    ```

    Cela créera un dossier `dist` contenant l'exécutable.

## Contribuer

Les contributions sont les bienvenues ! Veuillez soumettre une pull request ou ouvrir une issue pour discuter des changements que vous souhaitez apporter.

