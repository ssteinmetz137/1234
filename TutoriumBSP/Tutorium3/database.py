import os
import psycopg2

def doSQL(sql, args=None):
    host = "localhost"
    database = "postgres"
    user = os.environ["DB_USERNAME"]
    password = os.environ["DB_PASSWORD"]

    conn = psycopg2.connect(host=host, database=database, user=user, password=password)
    cur = conn.cursor()

    if args:
        cur.execute(sql, args)
    else:
        cur.execute(sql)
    conn.commit()

    try:
        output = cur.fetchall()
    except:
        output = None

    cur.close()
    conn.close()
    return output

# Datenbankfunktionen
def db_getAllStudis():
    return doSQL("SELECT * FROM public.studis;")

def db_getAllDozenten():
    return doSQL('SELECT * FROM public.dozenten;')

def db_getUserByEmail(email):
    return doSQL("SELECT * FROM public.personen WHERE email = %s;", (email,))

def db_addStudi(data):
    return doSQL("INSERT INTO public.studis (email, first_name, last_name, password, matrikelnummer, seminar, studiengang, abschluss) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", data)

def db_getAllSeminare():
    sql_query = """
    SELECT seminare.seminarid, seminare.titel, dozenten.titel, dozenten.first_name, dozenten.last_name, 
           seminare.oberbegriff, seminare.beschreibung, seminare.semester, seminare.status
    FROM public.seminare
    LEFT JOIN public.dozenten ON seminare.dozent_id = dozenten.dozent_id;
    """
    return doSQL(sql_query)

def db_getStudiByEmail(session):
    email = session.get("email")
    sql_query = """
    SELECT s.*
    FROM public.studis s
    JOIN public.personen p ON s.email = p.email
    WHERE p.email = %s;
    """
    return doSQL(sql_query, (email,))

def db_check_existing_email_matrikelnummer(email, matrikelnummer):
    email_exists = doSQL("SELECT COUNT(*) FROM public.studis WHERE email = %s;", (email,))[0][0] > 0
    matrikelnummer_exists = doSQL("SELECT COUNT(*) FROM public.studis WHERE matrikelnummer = %s;", (matrikelnummer,))[0][0] > 0
    return email_exists, matrikelnummer_exists

def transfer_data_to_personen():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"]
    )
    cur = conn.cursor()

    # Übertrage Dozenten
    cur.execute("SELECT * FROM public.dozenten")
    dozenten = cur.fetchall()
    for dozent in dozenten:
        email = dozent[4]
        cur.execute("SELECT COUNT(*) FROM public.personen WHERE email = %s", (email,))
        count = cur.fetchone()[0]
        if count == 0:
            # Die E-Mail-Adresse ist eindeutig, daher können wir sie einfügen
            cur.execute(
                "INSERT INTO public.personen (email, first_name, last_name, password, role) VALUES (%s, %s, %s, %s, %s)",
                (dozent[4], dozent[2], dozent[3], dozent[5], "dozent"))

    # Übertrage Studenten
    cur.execute("SELECT * FROM public.studis")
    studis = cur.fetchall()
    for studi in studis:
        email = studi[3]
        # Überprüfen, ob die E-Mail-Adresse bereits vorhanden ist
        cur.execute("SELECT COUNT(*) FROM public.personen WHERE email = %s", (email,))
        count = cur.fetchone()[0]
        if count == 0:
            # Die E-Mail-Adresse ist eindeutig, daher können wir sie einfügen
            cur.execute(
                "INSERT INTO public.personen (email, first_name, last_name, password, role) VALUES (%s, %s, %s, %s, %s)",
                (studi[3], studi[1], studi[2], studi[4], "studi"))

    conn.commit()
    cur.close()
    conn.close()

