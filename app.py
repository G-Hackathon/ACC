import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_from_directory,
)
from werkzeug.utils import secure_filename


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "acc-development-secret-key-change-this"
)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

DATA_DIR = BASE_DIR

DATABASE = os.path.join(
    DATA_DIR,
    "acc.db"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ============================================================
# PASSWORDS
# ============================================================

CHAIR_PASSWORD = os.environ.get(
    "CHAIR_PASSWORD",
    "welovekishorsir"
)


PRESS_PASSWORDS = {
    "Yukta": os.environ.get(
        "PRESS_YUKTA_PASSWORD",
        "aljazeeraarticles"
    ),

    "Nandika": os.environ.get(
        "PRESS_NANDIKA_PASSWORD",
        "aarushismybf"
    ),
}


# ============================================================
# DELEGATE ACCOUNTS
# ============================================================

DELEGATES = {
    "Siddhiksha": {
        "delegation": "National Liberation Council",
        "password": "NLC#Liberation2026!Sec",
    },

    "Shlok": {
        "delegation": "Southern Arkanian Republic",
        "password": "SAR#SouthArkania!948",
    },

    "Aarush": {
        "delegation": "Transitional Council of Arkania",
        "password": "TCA#Transition!7392",
    },

    "Nirav": {
        "delegation": "Republic of Selvar",
        "password": "RoS#SelvarPass!401",
    },

    "Vihaan": {
        "delegation": "Erdan Province",
        "password": "EP#ErdanSecure!827",
    },

    "Anika": {
        "delegation": "United Civilian Authority",
        "password": "UCA#CivilianAuth!315",
    },

    "Shrishti": {
        "delegation": "Western Arkanian Republic",
        "password": "WAR#WestArkania!682",
    },

    "Ryana": {
        "delegation": "Novera",
        "password": "NOV#NoveraAccess!594",
    },

    "Ridhu": {
        "delegation": "Republic of Darsen",
        "password": "RoD#DarsenState!173",
    },

    "Siya": {
        "delegation": "Tavria",
        "password": "TAV#TavriaSecure!846",
    },

    "Shruti": {
        "delegation": "Kavren State",
        "password": "KVR#KavrenPass!209",
    },

    "Sailesh": {
        "delegation": "Arkanian People's Front",
        "password": "APF#PeoplesFront!518",
    },

    "Naman": {
        "delegation": "Federal Government of Arkania",
        "password": "FGA#FedGovArkania!902",
    },

    "Ayushman": {
        "delegation": "Arkanian Military Command",
        "password": "AMC#MilitaryCmd!741",
    },

    "Rizwan": {
        "delegation": "Arkanian Intelligence Directorate",
        "password": "AID#IntelDir2026!613",
    },

    "Saanvi": {
        "delegation": "Foreign Affairs Office",
        "password": "FAO#ForeignAffairs!384",
    },

    "Reyansh": {
        "delegation": "Arkanian General Staff",
        "password": "AGS#GeneralStaff!825",
    },

    "Adele": {
        "delegation": "Arkanian Border Authority",
        "password": "ABA#BorderAuth!491",
    },

    "Jazlyn": {
        "delegation": "Lorian Autonomous Territory",
        "password": "LAT#LorianTerritory!637",
    },

    "Shivani": {
        "delegation": "Arkanian Humanitarian Authority",
        "password": "AHA#Humanitarian!158",
    },

    "Arshita": {
        "delegation": "Highlands of Ordan",
        "password": "HoO#OrdanHighlands!962",
    },

    "Guna": {
        "delegation": "Free State of Veyra",
        "password": "FSV#VeyraFreeState!407",
    },

    "Vidhi": {
        "delegation": "Zarev Republic",
        "password": "ZR#ZarevRepublic!831",
    },

    "Ashima": {
        "delegation": "Maren Coast",
        "password": "MC#MarenCoast!274",
    },
}


# ============================================================
# ALLOWED UPLOAD FILE TYPES
# ============================================================

ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "webp",
    "doc",
    "docx",
    "txt",
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# DATABASE
# ============================================================

def get_db():

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_db():

    connection = get_db()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS crises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            filename TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            delegation TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    connection.commit()

    connection.close()


# ============================================================
# TIME
# ============================================================

def now_string():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ============================================================
# USER SYSTEM
# ============================================================

def current_user():

    username = session.get(
        "username"
    )

    if not username:
        return None

    # --------------------------------------------------------
    # CHAIR
    # --------------------------------------------------------

    if username == "__chair__":

        return {
            "username": "Chair",
            "role": "chair",
            "delegation": "Arkanian Crisis Committee",
        }

    # --------------------------------------------------------
    # PRESS
    # --------------------------------------------------------

    if username in PRESS_PASSWORDS:

        return {
            "username": username,
            "role": "press",
            "delegation": "Press Corps",
        }

    # --------------------------------------------------------
    # DELEGATE
    # --------------------------------------------------------

    if username in DELEGATES:

        return {
            "username": username,
            "role": "delegate",
            "delegation": DELEGATES[
                username
            ]["delegation"],
        }

    # --------------------------------------------------------
    # INVALID SESSION
    # --------------------------------------------------------

    session.clear()

    return None


# ============================================================
# LOGIN REQUIRED
# ============================================================

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if current_user() is None:

            flash(
                "Please log in to access that page.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        return function(
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# ROLE REQUIRED
# ============================================================

def role_required(*roles):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            user = current_user()

            if user is None:

                flash(
                    "Please log in first.",
                    "error"
                )

                return redirect(
                    url_for("login")
                )

            if user["role"] not in roles:

                flash(
                    "You do not have permission to access that.",
                    "error"
                )

                return redirect(
                    url_for("home")
                )

            return function(
                *args,
                **kwargs
            )

        return wrapper

    return decorator


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    db = get_db()

    latest_crisis = db.execute(
        """
        SELECT *
        FROM crises
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()

    latest_articles = db.execute(
        """
        SELECT *
        FROM articles
        ORDER BY id DESC
        LIMIT 3
        """
    ).fetchall()

    db.close()

    return render_template(
        "index.html",
        user=current_user(),
        latest_crisis=latest_crisis,
        latest_articles=latest_articles,
    )


# ============================================================
# DELEGATE LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    error = None

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        # ----------------------------------------------------
        # CHAIR
        # ----------------------------------------------------

        if (
            username.lower() == "chair"
            and password == CHAIR_PASSWORD
        ):

            session.clear()

            session["username"] = "__chair__"

            flash(
                "Chair mode activated.",
                "success"
            )

            return redirect(
                url_for("home")
            )

        # ----------------------------------------------------
        # PRESS
        # ----------------------------------------------------

        if (
            username in PRESS_PASSWORDS
            and password == PRESS_PASSWORDS[
                username
            ]
        ):

            session.clear()

            session["username"] = username

            flash(
                f"Welcome, {username}.",
                "success"
            )

            return redirect(
                url_for("home")
            )

        # ----------------------------------------------------
        # DELEGATE
        # ----------------------------------------------------

        if username in DELEGATES:

            if (
                password
                == DELEGATES[
                    username
                ]["password"]
            ):

                session.clear()

                session["username"] = username

                flash(
                    f"Welcome back, {username}.",
                    "success"
                )

                return redirect(
                    url_for("home")
                )

        error = (
            "Incorrect username or password."
        )

        flash(
            error,
            "error"
        )

    return render_template(
        "delegate_login.html",
        user=current_user(),
        error=error,
    )


# ============================================================
# PRESS LOGIN
# ============================================================

@app.route(
    "/press-login",
    methods=["GET", "POST"]
)
def press_login():

    error = None

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if (
            username in PRESS_PASSWORDS
            and password == PRESS_PASSWORDS[
                username
            ]
        ):

            session.clear()

            session["username"] = username

            flash(
                f"Welcome, {username}. Press access granted.",
                "success"
            )

            return redirect(
                url_for("profile")
            )

        error = (
            "Invalid Press Corps credentials."
        )

    return render_template(
        "press_login.html",
        user=current_user(),
        error=error,
    )


# ============================================================
# CHAIR LOGIN
# ============================================================

@app.route(
    "/chair-login",
    methods=["GET", "POST"]
)
def chair_login():

    error = None

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if (
            username.lower() == "chair"
            and password == CHAIR_PASSWORD
        ):

            session.clear()

            session["username"] = "__chair__"

            flash(
                "Chair mode activated.",
                "success"
            )

            return redirect(
                url_for("profile")
            )

        error = (
            "Invalid Chair credentials."
        )

    return render_template(
        "chair_login.html",
        user=current_user(),
        error=error,
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("home")
    )


# ============================================================
# PROFILE
# ============================================================

@app.route("/profile")
@login_required
def profile():

    user = current_user()

    connection = get_db()

    note_count = 0

    article_count = 0

    crisis_count = 0

    # --------------------------------------------------------
    # DELEGATE NOTES
    # --------------------------------------------------------

    if user["role"] == "delegate":

        note_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM notes
            WHERE username = ?
            """,
            (
                user["username"],
            )
        ).fetchone()[0]

    # --------------------------------------------------------
    # PRESS ARTICLES
    # --------------------------------------------------------

    if user["role"] == "press":

        article_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM articles
            WHERE author = ?
            """,
            (
                user["username"],
            )
        ).fetchone()[0]

    # --------------------------------------------------------
    # CHAIR CRISES
    # --------------------------------------------------------

    if user["role"] == "chair":

        crisis_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM crises
            """
        ).fetchone()[0]

        article_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM articles
            """
        ).fetchone()[0]

    connection.close()

    return render_template(
        "profile.html",
        user=user,
        note_count=note_count,
        article_count=article_count,
        crisis_count=crisis_count,
    )


# ============================================================
# NOTES — DELEGATE ONLY
# ============================================================

@app.route("/notes")
@login_required
def notes():

    user = current_user()

    if user["role"] != "delegate":

        flash(
            "Notes are available to delegates.",
            "error"
        )

        return redirect(
            url_for("profile")
        )

    connection = get_db()

    all_notes = connection.execute(
        """
        SELECT *
        FROM notes
        WHERE username = ?
        ORDER BY updated_at DESC
        """,
        (
            user["username"],
        )
    ).fetchall()

    selected_note_id = request.args.get(
        "note",
        type=int
    )

    selected_note = None

    if selected_note_id:

        selected_note = connection.execute(
            """
            SELECT *
            FROM notes
            WHERE id = ?
            AND username = ?
            """,
            (
                selected_note_id,
                user["username"],
            )
        ).fetchone()

    if selected_note is None and all_notes:

        selected_note = all_notes[0]

    connection.close()

    return render_template(
        "notes.html",
        notes=all_notes,
        selected_note=selected_note,
        user=user,
    )


# ============================================================
# CREATE NOTE
# ============================================================

@app.route(
    "/notes/new",
    methods=["POST"]
)
@login_required
def new_note():

    user = current_user()

    if user["role"] != "delegate":

        flash(
            "Only delegates can create notes.",
            "error"
        )

        return redirect(
            url_for("profile")
        )

    title = request.form.get(
        "title",
        ""
    ).strip()

    content = request.form.get(
        "content",
        ""
    )

    if not title:

        title = "Untitled"

    current_time = now_string()

    connection = get_db()

    cursor = connection.execute(
        """
        INSERT INTO notes
        (
            username,
            title,
            content,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user["username"],
            title,
            content,
            current_time,
            current_time,
        )
    )

    connection.commit()

    note_id = cursor.lastrowid

    connection.close()

    return redirect(
        url_for(
            "notes",
            note=note_id
        )
    )


# ============================================================
# UPDATE NOTE
# ============================================================

@app.route(
    "/notes/<int:note_id>/update",
    methods=["POST"]
)
@login_required
def update_note(note_id):

    user = current_user()

    if user["role"] != "delegate":

        return redirect(
            url_for("profile")
        )

    title = request.form.get(
        "title",
        ""
    ).strip()

    content = request.form.get(
        "content",
        ""
    )

    if not title:

        title = "Untitled"

    connection = get_db()

    note = connection.execute(
        """
        SELECT *
        FROM notes
        WHERE id = ?
        AND username = ?
        """,
        (
            note_id,
            user["username"],
        )
    ).fetchone()

    if note is None:

        connection.close()

        flash(
            "That note could not be found.",
            "error"
        )

        return redirect(
            url_for("notes")
        )

    connection.execute(
        """
        UPDATE notes
        SET title = ?,
            content = ?,
            updated_at = ?
        WHERE id = ?
        AND username = ?
        """,
        (
            title,
            content,
            now_string(),
            note_id,
            user["username"],
        )
    )

    connection.commit()

    connection.close()

    flash(
        "Note saved.",
        "success"
    )

    return redirect(
        url_for(
            "notes",
            note=note_id
        )
    )


# ============================================================
# DELETE NOTE — DELEGATE ONLY
# ============================================================

@app.route(
    "/notes/<int:note_id>/delete",
    methods=["POST"]
)
@login_required
def delete_note(note_id):

    user = current_user()

    # --------------------------------------------------------
    # ONLY DELEGATES CAN DELETE NOTES
    # --------------------------------------------------------

    if user["role"] != "delegate":

        flash(
            "Only delegates can delete notes.",
            "error"
        )

        return redirect(
            url_for("profile")
        )

    connection = get_db()

    # --------------------------------------------------------
    # MAKE SURE THE NOTE EXISTS AND BELONGS TO THIS USER
    # --------------------------------------------------------

    note = connection.execute(
        """
        SELECT id
        FROM notes
        WHERE id = ?
        AND username = ?
        """,
        (
            note_id,
            user["username"],
        )
    ).fetchone()

    if note is None:

        connection.close()

        flash(
            "That note could not be found.",
            "error"
        )

        return redirect(
            url_for("notes")
        )

    # --------------------------------------------------------
    # DELETE NOTE
    # --------------------------------------------------------

    connection.execute(
        """
        DELETE FROM notes
        WHERE id = ?
        AND username = ?
        """,
        (
            note_id,
            user["username"],
        )
    )

    connection.commit()

    connection.close()

    flash(
        "Note deleted successfully.",
        "success"
    )

    return redirect(
        url_for("notes")
    )

# ============================================================
# ARTICLES
# ============================================================


@app.route(
    "/articles",
    methods=["GET", "POST"]
)
def articles():

    connection = get_db()

    user = current_user()

    # --------------------------------------------------------
    # ARTICLE POST
    # --------------------------------------------------------

    if request.method == "POST":

        if user is None:

            connection.close()

            flash(
                "You must be logged in to publish an article.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        if user["role"] != "press":

            connection.close()

            flash(
                "Only Press delegates can publish articles.",
                "error"
            )

            return redirect(
                url_for("articles")
            )

        title = request.form.get(
            "title",
            ""
        ).strip()

        body = request.form.get(
            "body",
            ""
        ).strip()

        if not title or not body:

            connection.close()

            flash(
                "Please provide both a headline and article.",
                "error"
            )

            return redirect(
                url_for("articles")
            )

        connection.execute(
            """
            INSERT INTO articles
            (
                author,
                delegation,
                title,
                body,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user["username"],
                user["delegation"],
                title,
                body,
                now_string(),
            )
        )

        connection.commit()

        connection.close()

        flash(
            "Article published.",
            "success"
        )

        return redirect(
            url_for("articles")
        )

    # --------------------------------------------------------
    # GET ARTICLES
    # --------------------------------------------------------

    all_articles = connection.execute(
        """
        SELECT *
        FROM articles
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "articles.html",
        articles=all_articles,
        user=user,
    )


# ============================================================
# FULL ARTICLE
# ============================================================

@app.route(
    "/articles/<int:article_id>"
)
def full_article(article_id):

    connection = get_db()

    article = connection.execute(
        """
        SELECT *
        FROM articles
        WHERE id = ?
        """,
        (
            article_id,
        )
    ).fetchone()

    connection.close()

    if article is None:

        flash(
            "Article not found.",
            "error"
        )

        return redirect(
            url_for("articles")
        )

    return render_template(
        "article.html",
        article=article,
        user=current_user(),
    )


# ============================================================
# PRESS PUBLISHING DESK
# ============================================================

@app.route(
    "/press-upload",
    methods=["GET", "POST"]
)
@role_required("press")
def press_upload():

    user = current_user()

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        body = request.form.get(
            "body",
            ""
        ).strip()

        if not title or not body:

            return render_template(
                "press_upload.html",
                user=user,
                error="Please provide both a headline and article.",
                title=title,
                content=body,
            )

        connection = get_db()

        connection.execute(
            """
            INSERT INTO articles
            (
                author,
                delegation,
                title,
                body,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user["username"],
                user["delegation"],
                title,
                body,
                now_string(),
            )
        )

        connection.commit()

        connection.close()

        flash(
            "Article published successfully.",
            "success"
        )

        return redirect(
            url_for("articles")
        )

    return render_template(
        "press_upload.html",
        user=user,
        error=None,
        title="",
        content="",
    )


# ============================================================
# DELETE ARTICLE — CHAIR ONLY
# ============================================================

@app.route(
    "/articles/<int:article_id>/delete",
    methods=["POST"]
)
@role_required("chair")
def delete_article(article_id):

    connection = get_db()

    connection.execute(
        """
        DELETE FROM articles
        WHERE id = ?
        """,
        (
            article_id,
        )
    )

    connection.commit()

    connection.close()

    flash(
        "Article deleted.",
        "success"
    )

    return redirect(
        url_for("articles")
    )


# ============================================================
# CRISIS COMMAND CENTER
# ============================================================

@app.route(
    "/crises",
    methods=["GET", "POST"]
)
def crises():

    connection = get_db()

    user = current_user()

    # --------------------------------------------------------
    # PUBLISH CRISIS
    # --------------------------------------------------------

    if request.method == "POST":

        if (
            user is None
            or user["role"] != "chair"
        ):

            connection.close()

            flash(
                "Only the Chair can publish crises.",
                "error"
            )

            return redirect(
                url_for("crises")
            )

        title = request.form.get(
            "title",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        uploaded = request.files.get(
            "file"
        )

        if not title or not description:

            connection.close()

            flash(
                "A crisis needs a title and description.",
                "error"
            )

            return redirect(
                url_for("crises")
            )

        filename = None

        # ----------------------------------------------------
        # FILE UPLOAD
        # ----------------------------------------------------

        if (
            uploaded
            and uploaded.filename
        ):

            if not allowed_file(
                uploaded.filename
            ):

                connection.close()

                flash(
                    "That file type is not allowed.",
                    "error"
                )

                return redirect(
                    url_for("crises")
                )

            safe_name = secure_filename(
                uploaded.filename
            )

            timestamp = datetime.now().strftime(
                "%Y%m%d%H%M%S"
            )

            filename = (
                timestamp
                + "_"
                + safe_name
            )

            uploaded.save(
                os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )
            )

        connection.execute(
            """
            INSERT INTO crises
            (
                title,
                description,
                filename,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                title,
                description,
                filename,
                now_string(),
            )
        )

        connection.commit()

        connection.close()

        flash(
            "Crisis published.",
            "success"
        )

        return redirect(
            url_for("crises")
        )

    # --------------------------------------------------------
    # GET CRISES
    # --------------------------------------------------------

    all_crises = connection.execute(
        """
        SELECT *
        FROM crises
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "crises.html",
        crises=all_crises,
        user=user,
    )


# ============================================================
# DELETE CRISIS — CHAIR ONLY
# ============================================================

@app.route(
    "/crises/<int:crisis_id>/delete",
    methods=["POST"]
)
@role_required("chair")
def delete_crisis(crisis_id):

    connection = get_db()

    crisis = connection.execute(
        """
        SELECT filename
        FROM crises
        WHERE id = ?
        """,
        (
            crisis_id,
        )
    ).fetchone()

    # --------------------------------------------------------
    # DELETE ASSOCIATED FILE
    # --------------------------------------------------------

    if (
        crisis
        and crisis["filename"]
    ):

        path = os.path.join(
            UPLOAD_FOLDER,
            crisis["filename"]
        )

        if os.path.exists(path):

            os.remove(path)

    # --------------------------------------------------------
    # DELETE DATABASE ENTRY
    # --------------------------------------------------------

    connection.execute(
        """
        DELETE FROM crises
        WHERE id = ?
        """,
        (
            crisis_id,
        )
    )

    connection.commit()

    connection.close()

    flash(
        "Crisis deleted.",
        "success"
    )

    return redirect(
        url_for("crises")
    )


# ============================================================
# SERVE CRISIS FILES
# ============================================================

@app.route(
    "/uploads/<filename>"
)
def uploaded_file(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# ============================================================
# ERROR HANDLING
# ============================================================

@app.errorhandler(413)
def file_too_large(error):

    flash(
        "The uploaded file is too large. Maximum size is 10 MB.",
        "error"
    )

    return redirect(
        url_for("crises")
    )


# ============================================================
# STARTUP
# ============================================================

os.makedirs(
    DATA_DIR,
    exist_ok=True
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

init_db()


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
