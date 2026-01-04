import requests

class WLED:
    def __init__(self, ip):
        """
        Erstellt ein WLED-Objekt.
        :param ip: IP-Adresse des WLED-Geräts, z.B. '192.168.1.50'
        """
        self.ip = ip
        self.base_url = f"http://{ip}/json/state"

    def _send(self, payload):
        try:
            response = requests.post(self.base_url, json=payload, timeout=2)
            return response.json()
        except requests.RequestException as e:
            print(f"Fehler bei Verbindung zu WLED: {e}")
            return None

    def on(self):
        """Schaltet das WLED ein"""
        return self._send({"on": True})

    def off(self):
        """Schaltet das WLED aus"""
        return self._send({"on": False})

    def set_brightness(self, brightness):
        """
        Setzt die Helligkeit
        :param brightness: 0-255
        """
        brightness = max(0, min(255, brightness))
        return self._send({"bri": brightness})

    def set_color(self, r, g, b):
        """
        Setzt die Farbe (RGB)
        :param r: 0-255
        :param g: 0-255
        :param b: 0-255
        """
        return self._send({"seg": [{"col": [[r, g, b]]}]})

    def set_effect(self, effect_id):
        """
        Setzt den Effekt
        :param effect_id: Effektnummer aus der WLED-App
        """
        return self._send({"fx": effect_id})

    def set_speed(self, speed):
        """
        Setzt die Geschwindigkeit des Effekts
        :param speed: 0-255
        """
        return self._send({"sx": speed})

    def set(self, on=None, brightness=None, color=None, effect=None, speed=None):
        """
        Flexible Methode: alles auf einmal setzen
        """
        payload = {}
        if on is not None:
            payload["on"] = bool(on)
        if brightness is not None:
            payload["bri"] = max(0, min(255, brightness))
        if color is not None and effect is not None:
            r, g, b = color
            payload["seg"] = [{"col": [[r, g, b]],"fx":effect}]
        if speed is not None:
            payload["sx"] = max(0, min(255, speed))

        return self._send(payload)
