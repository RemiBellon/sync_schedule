from fetcher import download_schedule
from parser import parse_schedule
from calendar_generator import create_ics
import os

def main():
    print("--- Démarrage de la synchronisation de l'emploi du temps ---")

    # Définition des chemins
    # Le fichier main.py étant dans src/schedule_sync/, on recule de 2 dossiers pour atteindre data/
    # Vous pouvez utiliser des chemins absolus via os.path pour être encore plus robuste en prod
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    ods_path = os.path.join(base_dir, "data", "current_schedule.ods")
    ics_path = os.path.join(base_dir, "data", "planning_promo.ics")

    # Étape 1 : Téléchargement depuis NextCloud
    try:
        download_schedule()
        # (Assurez-vous que la fonction download_schedule dans fetcher.py utilise bien eds_path comme destination)
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")
        return

    # Étape 2 : Parsing des données
    events = parse_schedule(ods_path)

    if not events:
        print("Erreur : Aucun événement extrait.")
        return

    # Étape 3 : Génération de l'ICS
    create_ics(events, ics_path)

    print("--- Terminé avec succès ! ---")

if __name__ == "__main__":
    main()