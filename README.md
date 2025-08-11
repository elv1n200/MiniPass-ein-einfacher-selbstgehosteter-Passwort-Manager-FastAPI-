# MiniPass-ein-einfacher-selbstgehosteter-Passwort-Manager-FastAPI-
Webapp, die Passwörter verschlüsselt in einer SQLite-DB speichert, mit Login und Suche.

## Features

- Sitzungsbasierter Login mit Passwort-Hashing über `bcrypt`
- AES-Verschlüsselung der gespeicherten Passwörter (Fernet)
- Speicherung in einer lokalen SQLite-Datenbank
- Suchfunktion über vorhandene Einträge
- Dockerfile für einfachen Container-Betrieb

## Konfiguration

Vor dem Start muss der geheime Schlüssel für die Verschlüsselung gesetzt werden:

```bash
export MINIPASS_SECRET_KEY="$(openssl rand -base64 32)"
```

## Entwicklung

### Abhängigkeiten installieren

```bash
python -m pip install -r requirements.txt
```

### Tests ausführen

```bash
pytest
```

### Anwendung starten

```bash
uvicorn app.main:app --reload
```

### Mit Docker

```bash
docker build -t minipass .
docker run -e MINIPASS_SECRET_KEY="$(openssl rand -base64 32)" -p 8000:8000 minipass
```
