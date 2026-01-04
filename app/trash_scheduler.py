import csv
import logging
from datetime import datetime, timedelta
import schedule
import time
import os
import sys
from threading import Timer

# WLED-Konfiguration
WLED_IP = "192.168.1.246"  # IP-Adresse des WLED-Geräts anpassen
WLED_ENABLED = True  # WLED-Steuerung aktivieren/deaktivieren

# Farb-Mapping für Mülltypen (RGB)
TRASH_TYPE_COLORS = {
    'Restmuell': (255, 0, 0),  # Rot
    'Gelber Sack/Gelbe Tonne': (255, 255, 0),  # Gelb
    'Biomuell': (0, 128, 0),  # Grün
    'Papier': (0, 0, 255)  # Blau
}

# Logger-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trash_check.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import WLED-Klasse
try:
    from wled_api import WLED
except ImportError:
    logger.warning("WLED-API nicht importierbar. WLED-Steuerung deaktiviert.")
    WLED_ENABLED = False

# Dictionary zum Speichern von laufenden Ausschalt-Timern
active_turnoff_timers = {}


def turn_off_wled_delayed(delay_hours=26):
    """Schaltet das WLED-Gerät nach der angegebenen Zeit aus."""
    def turn_off():
        try:
            if WLED_ENABLED:
                wled = WLED(WLED_IP)
                wled.off()
                logger.info(f"WLED-Gerät nach {delay_hours} Stunden ausgeschaltet")
                if "wled_turnoff" in active_turnoff_timers:
                    del active_turnoff_timers["wled_turnoff"]
        except Exception as e:
            logger.error(f"Fehler beim Ausschalten des WLED-Geräts: {e}")
    
    # Existierenden Timer canceln wenn vorhanden
    if "wled_turnoff" in active_turnoff_timers:
        active_turnoff_timers["wled_turnoff"].cancel()
    
    # Neuen Timer erstellen (delay_hours * 3600 Sekunden)
    timer = Timer(delay_hours * 3600, turn_off)
    timer.daemon = True
    timer.start()
    active_turnoff_timers["wled_turnoff"] = timer
    logger.info(f"WLED-Ausschalt-Timer für {delay_hours} Stunden gestartet")


def activate_wled_for_trash(trash_types):
    """Aktiviert WLED mit der passenden Farbe basierend auf Mülltyp."""
    if not WLED_ENABLED:
        return
    
    try:
        wled = WLED(WLED_IP)
        
        # Finde die "wichtigste" Müllart (erste in der Liste)
        primary_trash_type = trash_types[0] if trash_types else None
        
        if primary_trash_type and primary_trash_type in TRASH_TYPE_COLORS:
            r, g, b = TRASH_TYPE_COLORS[primary_trash_type]
            # WLED einschalten mit Farbe und Effekt 2
            wled.set(on=True, brightness=200, color=(r, g, b), effect=2, speed=30)
            logger.info(f"WLED-Gerät aktiviert für {primary_trash_type} (RGB: {r}, {g}, {b}, Effect: 2)")
            
            # Timer für Ausschalten nach 26 Stunden starten
            turn_off_wled_delayed(26)
        else:
            logger.warning(f"Unbekannter Mülltyp: {primary_trash_type}")
    except Exception as e:
        logger.error(f"Fehler beim Steuern des WLED-Geräts: {e}")


def load_trash_schedule(csv_file):
    """Lädt den Müllabholplan aus der CSV-Datei."""
    schedule_dict = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            # Header lesen
            headers = next(reader)
            trash_types = headers[1:]  # Erste Spalte ist Restmüll 4-Wo, Rest sind die Mülltypen
            
            # Daten lesen
            for row in reader:
                if not row[0]:  # Leere erste Spalte überspringen
                    continue
                    
                try:
                    # Datum im Format DD.MM.YYYY
                    date = datetime.strptime(row[0].strip(), '%d.%m.%Y').date()
                    schedule_dict[date] = {
                        'Restmüll 4-Wo': row[0].strip() if row[0] else None,
                        'Gelber Sack/Gelbe Tonne': row[1].strip() if len(row) > 1 and row[1] else None,
                        'Biomüll': row[2].strip() if len(row) > 2 and row[2] else None,
                        'Papier': row[3].strip() if len(row) > 3 and row[3] else None
                    }
                except ValueError:
                    continue
    except FileNotFoundError:
        logger.error(f"CSV-Datei nicht gefunden: {csv_file}")
        return {}
    
    return schedule_dict


def check_trash_tomorrow():
    """Prüft, ob morgen Müll abgeholt wird."""
    csv_file = os.path.join(os.path.dirname(__file__), 'amhagenberglotte.csv')
    
    # Schedule laden
    schedule_dict = {}
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            headers = next(reader)
            
            for row in reader:
                if not any(row):  # Leere Zeilen überspringen
                    continue
                
                # Durchsuche alle Spalten nach Daten
                for col_idx, value in enumerate(row):
                    if value and value.strip():
                        try:
                            date = datetime.strptime(value.strip(), '%d.%m.%Y').date()
                            trash_type = headers[col_idx] if col_idx < len(headers) else "Unbekannt"
                            if date not in schedule_dict:
                                schedule_dict[date] = []
                            if trash_type not in schedule_dict[date]:
                                schedule_dict[date].append(trash_type)
                        except ValueError:
                            pass
    except FileNotFoundError:
        logger.error(f"CSV-Datei nicht gefunden: {csv_file}")
        return
    
    # Morgen's Datum berechnen
    tomorrow = datetime.now().date() + timedelta(days=1)
    
    # Prüfen, ob morgen Müll abgeholt wird
    if tomorrow in schedule_dict:
        trash_types = schedule_dict[tomorrow]
        for trash_type in trash_types:
            logger.info(f"Müllabholung morgen ({tomorrow.strftime('%d.%m.%Y')}): {trash_type}")
        
        # WLED aktivieren für die Müllabholung
        activate_wled_for_trash(trash_types)
    else:
        logger.debug(f"Keine Müllabholung morgen ({tomorrow.strftime('%d.%m.%Y')})")


def schedule_trash_check():
    """Startet den Scheduler, der täglich um 6 Uhr die Prüfung durchführt."""
    schedule.every().day.at("06:00").do(check_trash_tomorrow)
    
    logger.info("Trash-Scheduler gestartet. Prüfung täglich um 06:00 Uhr.")
    
    # Scheduler läuft in einer Endlosschleife
    while True:
        schedule.run_pending()
        time.sleep(60)  # Jede Minute prüfen, ob eine Aufgabe fällig ist


if __name__ == "__main__":
    # Einmalige Prüfung beim Start (optional)
    logger.info("Führe initiale Müllabholung-Prüfung durch...")
    check_trash_tomorrow()
    
    # Scheduler starten
    schedule_trash_check()
