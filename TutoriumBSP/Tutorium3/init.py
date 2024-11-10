import os
import psycopg2

# Verbindung zur Datenbank (Singleton)
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"]
    )
    return conn

# Funktion zum Erstellen der Datenbanken, falls diese nicht existieren
def create_databases():
    conn = get_db_connection()
    cur = conn.cursor()

    # SQL-Befehl, um die 'studis'-Datenbank zu erstellen, wenn sie noch nicht existiert
    create_studis_table = """
    CREATE TABLE IF NOT EXISTS public.studis (
        email VARCHAR(255) PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        password VARCHAR(100),
        matrikelnummer INTEGER UNIQUE,
        seminar VARCHAR(20),
        studiengang VARCHAR(50),
        abschluss VARCHAR(10)
    );
    """
    # SQL-Befehl, um die 'dozenten'-Datenbank zu erstellen, wenn sie noch nicht existiert
    create_dozenten_table = """
    CREATE TABLE IF NOT EXISTS public.dozenten (
        dozent_id SERIAL PRIMARY KEY,
        titel VARCHAR(50),
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        email VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(100)
    );
    """

    # SQL-Befehl, um die 'personen'-Datenbank zu erstellen, wenn sie noch nicht existiert
    create_personen_table = """
    CREATE TABLE IF NOT EXISTS public.personen (
        email VARCHAR(255) PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        password VARCHAR(100),
        role VARCHAR(20)  -- z.B. 'studi' oder 'dozent'
    );
    """

    create_seminare_table = """
    CREATE TABLE IF NOT EXISTS seminare (
        seminarid SERIAL PRIMARY KEY,
        titel VARCHAR(100),
        dozent_id INTEGER REFERENCES dozenten(dozent_id) ON DELETE SET NULL,
        oberbegriff VARCHAR(100),
        beschreibung VARCHAR(255),
        anhang BYTEA DEFAULT NULL,
        zugewiesener_student INTEGER REFERENCES studis(matrikelnummer) ON DELETE SET NULL,
        semester INT,
        status VARCHAR(13) DEFAULT 'frei'
            );
        """

    # Tabellen erstellen
    cur.execute(create_studis_table)
    cur.execute(create_dozenten_table)
    cur.execute(create_personen_table)
    cur.execute(create_seminare_table)

    # Dozenten-Accounts hinzufügen, falls diese noch nicht existieren
    dozenten_data = [
        ("Prof.", "Dr. Klaus-Dieter", "Altho", "altho@uni-hildesheim.de", "Passwort!123"),
        ("Dr.", "Pascal", "Reuss", "reusspa@uni-hildesheim.de", "Passwort!123"),
        ("", "Jakob Michael", "Schonborn", "schoenb@uni-hildesheim.de", "Passwort!123")
    ]

    for titel, first_name, last_name, email, password in dozenten_data:
        # Überprüfen, ob der Dozent bereits existiert, bevor er eingefügt wird
        cur.execute("SELECT 1 FROM public.dozenten WHERE email = %s", (email,))
        if cur.fetchone() is None:
            cur.execute("""
            INSERT INTO public.dozenten (titel, first_name, last_name, email, password)
            VALUES (%s, %s, %s, %s, %s)
            """, (titel, first_name, last_name, email, password))

    seminare_data = [
        ("Einführung in die Informatik", 1, "Grundlagen", "Einführung in die Konzepte der Informatik", None, None, 1,
         "frei"),
        ("Datenbanksysteme", 2, "Datenbanken", "Grundlagen relationaler Datenbanksysteme", None, None, 1, "frei"),
        ("Programmierung in Python", 3, "Programmierung", "Programmieren lernen mit Python", None, None, 2, "frei")
    ]

    for titel, dozent_id, oberbegriff, beschreibung, anhang, zugewiesener_student, semester, status in seminare_data:
        # Überprüfen, ob das Seminar bereits existiert, bevor es eingefügt wird
        cur.execute("SELECT 1 FROM seminare WHERE titel = %s AND semester = %s", (titel, semester))
        if cur.fetchone() is None:
            cur.execute("""
            INSERT INTO seminare (titel, dozent_id, oberbegriff, beschreibung, anhang, zugewiesener_student, semester, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (titel, dozent_id, oberbegriff, beschreibung, anhang, zugewiesener_student, semester, status))



    # Änderungen speichern und Verbindung schließen
    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    create_databases()
    print("Datenbanken wurden überprüft und erstellt (falls erforderlich). Dozenten-Accounts wurden hinzugefügt.")
