from flask import Flask, render_template, request, session, redirect, url_for
from database import (
    db_getAllStudis, db_check_existing_email_matrikelnummer,
    db_getUserByEmail, db_addStudi,
    transfer_data_to_personen, db_getStudiByEmail, db_getAllSeminare
)
from init import create_databases
import os
import re

# Flask-App initialisieren
app = Flask(__name__)
app.secret_key = "Tutorium3"

create_databases()

# Regulärer Ausdruck für das Passwortmuster
password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

# Regulärer Ausdruck für Vorname und Nachname
name_pattern = re.compile(r'^[A-Z][a-z]+$')

# Regulärer Ausdruck für die E-Mail-Adresse
email_pattern = re.compile(r'^[a-z0-9.-_]+@[a-z0-9.-]+\.[a-z]{2,}$')

# Regulärer Ausdruck für die Matrikelnummer (6 bis 8 Ziffern)
matrikel_pattern = re.compile(r'^\d{6,8}$')

# Startseite
@app.route('/', methods=["GET"])
def start():
    transfer_data_to_personen()
    session.pop("email", None)
    session.pop("role", None)
    return render_template("index.html")


# Login
@app.route('/profil', methods=["POST", "GET"])
def profil():
    if session.get("email"):  # Überprüfe, ob der Benutzer bereits eingeloggt ist
        if session["role"] == "dozent":
            allstudis = db_getAllStudis()
            return render_template("alle_studis.html", allstudis=allstudis)
        else:
            studi_data = db_getStudiByEmail(session)
            return render_template("profil.html", studi_data=studi_data)

    if request.method == "POST":
        data = request.form
        email = data.get("email")
        pw = data.get("password")
        userdata = db_getUserByEmail(email)
        if userdata and pw == userdata[0][3]:
            session["email"] = email
            session["role"] = userdata[0][4]  # Setze die Rolle in der Session
            if session["role"] == "dozent":
                allstudis = db_getAllStudis()
                return render_template("alle_studis.html", allstudis=allstudis)
            else:
                studi_data = db_getStudiByEmail(session)
                return render_template("profil.html", studi_data=studi_data)
        else:
            return render_template("login.html", emsg="Email oder Passwort falsch!")

    return render_template("login.html")


# Benutzer hinzufügen
@app.route('/add', methods=["POST", "GET"])
def add():
    # Standardmäßig leere Werte für das Formular
    form_data = {
        'email': '',
        'first_name': '',
        'last_name': '',
        'password': '',
        'matrikelnummer': '',
        'seminar': '',
        'studiengang': '',
        'abschluss': ''
    }

    if request.method == "POST":
        data = request.form
        email = data.get("email")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        password = data.get("password")
        matrikelnummer = data.get("matrikelnummer")
        seminar = data.get("seminar")
        studiengang = data.get("studiengang")
        abschluss = data.get("abschluss")

        # Setze die Werte zurück, die der Benutzer eingegeben hat
        form_data.update({
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'matrikelnummer': matrikelnummer,
            'seminar': seminar,
            'studiengang': studiengang,
            'abschluss': abschluss
        })

        # Validierung der Eingabefelder
        if email and first_name and last_name and password and seminar and studiengang and matrikelnummer:
            # Vorname und Nachname validieren
            if not name_pattern.match(first_name):
                return render_template("add.html", form_data=form_data, emsg="Der Vorname muss mit einem Großbuchstaben beginnen und nur Kleinbuchstaben enthalten.")
            if not name_pattern.match(last_name):
                return render_template("add.html", form_data=form_data, emsg="Der Nachname muss mit einem Großbuchstaben beginnen und nur Kleinbuchstaben enthalten.")

            # E-Mail-Adresse validieren
            if not email_pattern.match(email):
                return render_template("add.html", form_data=form_data, emsg="Die E-Mail-Adresse ist ungültig.")

            # Matrikelnummer validieren
            if not matrikel_pattern.match(matrikelnummer):
                return render_template("add.html", form_data=form_data, emsg="Die Matrikelnummer muss zwischen 6 und 8 Zahlen enthalten.")

            # Überprüfen, ob E-Mail oder Matrikelnummer bereits existieren
            email_exists, matrikelnummer_exists = db_check_existing_email_matrikelnummer(email, matrikelnummer)

            if email_exists:
                return render_template("add.html", form_data=form_data, emsg="Diese E-Mail-Adresse wird bereits verwendet. Bitte eine andere wählen.")
            elif matrikelnummer_exists:
                return render_template("add.html", form_data=form_data, emsg="Diese Matrikelnummer wird bereits verwendet. Bitte eine andere wählen.")

            # Passwort validieren
            if not password_pattern.match(password):
                return render_template("add.html", form_data=form_data, emsg="Das Passwort entspricht nicht den Anforderungen.")

            # Benutzer in die Datenbank einfügen
            db_addStudi([email, first_name, last_name, password, matrikelnummer, seminar, studiengang, abschluss])
            transfer_data_to_personen()
            return render_template("profil.html", smsg="Benutzer erfolgreich hinzugefügt!")
        else:
            return render_template("add.html", form_data=form_data, emsg="Bitte füllen Sie alle erforderlichen Felder aus.")

    return render_template("add.html", form_data=form_data)

@app.route('/seminare')
def seminare():
    seminare=db_getAllSeminare()
    return render_template("seminare.html", seminare=seminare)

# Logout
@app.route('/logout', methods=["POST", "GET"])
def logout():
    session.pop("email", None)
    session.pop("role", None)
    return render_template("login.html", smsg="Sie haben sich erfolgreich ausgeloggt!")


if __name__ == '__main__':
    app.run()
