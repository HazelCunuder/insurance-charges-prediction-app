# Application de prédiction de charges d'assurance

## Contexte

Ce projet est une application web développée en Django qui permet de prédire les charges d'assurance des individus en fonction de diverses caractéristiques. L'application utilise un modèle de machine learning pour effectuer les prédictions et offre une interface utilisateur simple pour interagir avec le modèle.

## Description

Le site contient plusieurs sections principales :

- **Accueil** : Présentation de l'application et de ses fonctionnalités.
- **Inscription/Connexion** : Permet aux utilisateurs de créer un compte ou de se connecter.
- **Prédiction** : Formulaire pour saisir les caractéristiques nécessaires à la prédiction des charges d'assurance.
- **Résultats** : Affichage des résultats de la prédiction.
- **Profil** : Gestion des informations utilisateur.

Selon que l'utilisateur est connecté ou non, certaines fonctionnalités peuvent être restreintes:

- **Utilisateurs non connectés** : Accès limité à l'accueil, l'espace de prédiction, et à la page de connexion/inscription.
- **Utilisateurs connectés** : Accès complet à toutes les fonctionnalités.

## Technologies utilisées

- Django : Framework web utilisé pour développer l'application.
- Python : Langage de programmation principal.
- HTML/CSS : Pour la structure et le style des pages web.
- JavaScript : Pour les interactions côté client.
- Gunicorn : Serveur d'applications WSGI pour déployer l'application.
- Tailwind CSS : Framework CSS pour le design et la mise en page.
- SQLite : Base de données utilisée pour stocker les informations utilisateur.

## Structure du projet

- `InsuranceChargePredictionApp/` : Contient les fichiers principaux de l'application Django.
  - `InsuranceChargePredictionApp/` : Contient les paramètres et la configuration de l'application.
  - `accounts/` : Gère l'authentification et la gestion des utilisateurs.
  - `predict/` : Contient la logique de prédiction et les vues associées.
  - `staticfiles/` : Contient les fichiers statiques (CSS, JavaScript, images).
  - `theme/` : Contient les fichiers de thème pour l'interface utilisateur.
  - `requirements.txt` : Liste des dépendances Python nécessaires.
- `README.md` : Ce fichier de documentation.

## Installation

1. Cloner le dépôt GitHub :

    ```bash
        git clone https://github.com/HazelCunuder/insurance-charges-prediction-app.git
        cd insurance-charges-prediction-app
    ```

2. Installer les dépendances requises :

    ```bash
        pip install -r requirements.txt
    ```

3. Lancer l'application :

    ```bash
        gunicorn InsuranceChargePredictionApp.wsgi
    ```

4. Accéder à l'application via un navigateur web à l'adresse suivante :

    ```bash
        http://127.0.0.1:8000
    ```

## Utilisation

1. Créez un compte utilisateur ou connectez-vous si vous en avez déjà un.
2. Remplissez le formulaire avec les informations requises (âge, sexe, IMC, nombre d'enfants, tabagisme, région).
3. Soumettez le formulaire pour obtenir la prédiction des charges d'assurance.
4. Consultez les résultats affichés à l'écran

## Contribution

Les contributions sont les bienvenues ! Veuillez suivre les étapes suivantes pour contribuer :

1. Forker le dépôt.
2. Créer une branche pour votre fonctionnalité ou correction de bug.
3. Effectuer vos modifications et les valider.
4. Pousser vos modifications vers votre fork.
5. Ouvrir une Pull Request vers le dépôt principal.

## Contributeurs

- Hazel Cunuder - [GitHub](https://github.com/HazelCunuder)
- Amaury Rammanat - [GitHub](https://github.com/John-Do59)
- Flora Trecul - [GitHub](https://github.com/Flora-Trecul)
