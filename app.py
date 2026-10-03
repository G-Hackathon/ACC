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
    flash,
    session,
    send_from_directory,
    abort,
)


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-secret-change-this"
)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

DATABASE = os.path.join(
    DATA_DIR,
    "acc.db"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)


os.makedirs(
    DATA_DIR,
    exist_ok=True
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ============================================================
# PASSWORDS
# ============================================================

CHAIR_PASSWORD = os.environ.get(
    "CHAIR_PASSWORD",
    "welovekishorsir"
)


PRESS_PASSWORDS = {
    "Yukta": "aljazeeraarticles",
    "Nandika": "aarushismybf",
}


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

    "Manisha": {
        "delegation": "Class Teacher",
        "password": "ClassTeach094",
    },
}


# ============================================================
# DATABASE
# ============================================================

def get_db():

    conn = sqlite3.connect(
        DATABASE
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS crises (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            description TEXT NOT NULL,

            filename TEXT,

            created_at TEXT NOT NULL

        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            author TEXT NOT NULL,

            delegation TEXT,

            title TEXT NOT NULL,

            body TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT NOT NULL,

            title TEXT NOT NULL,

            content TEXT NOT NULL,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL

        )
    """)

    conn.commit()

    conn.close()


# ============================================================
# FILE VALIDATION
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

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


# ============================================================
# CURRENT USER
# ============================================================

def current_user():

    username = session.get(
        "username"
    )

    if not username:
        return None

    # CHAIR

    if username == "__chair__":

        return {
            "username": "Chair",
            "role": "chair",
        }

    # PRESS

    if username in PRESS_PASSWORDS:

        return {
            "username": username,
            "role": "press",
        }

    # DELEGATE

    if username in DELEGATES:

        return {
            "username": username,
            "role": "delegate",
            "delegation":
                DELEGATES[username]["delegation"],
        }

    return None


# ============================================================
# MAKE USER AVAILABLE TO ALL TEMPLATES
# ============================================================

@app.context_processor
def inject_user():

    return {
        "user": current_user()
    }


# ============================================================
# LOGIN REQUIRED
# ============================================================

def login_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        user = current_user()

        if user is None:

            flash(
                "Please log in first."
            )

            return redirect(
                url_for("login")
            )

        return view(
            *args,
            **kwargs
        )

    return wrapped


# ============================================================
# ROLE REQUIRED
# ============================================================

def role_required(*roles):

    def decorator(view):

        @wraps(view)
        def wrapped(*args, **kwargs):

            user = current_user()

            if user is None:

                flash(
                    "Please log in first."
                )

                return redirect(
                    url_for("login")
                )

            if user["role"] not in roles:

                flash(
                    "You do not have permission to access that."
                )

                return redirect(
                    url_for("home")
                )

            return view(
                *args,
                **kwargs
            )

        return wrapped

    return decorator


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    conn = get_db()

    latest_crisis = conn.execute("""
        SELECT *
        FROM crises
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    latest_articles = conn.execute("""
        SELECT *
        FROM articles
        ORDER BY id DESC
        LIMIT 3
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        latest_crisis=latest_crisis,
        latest_articles=latest_articles,
    )


# ============================================================
# COMBINED LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

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
        # CHAIR LOGIN
        # ----------------------------------------------------

        if username.lower() == "chair":

            if password == CHAIR_PASSWORD:

                session.clear()

                session["username"] = "__chair__"

                flash(
                    "Chair access granted."
                )

                return redirect(
                    url_for("home")
                )

            flash(
                "Incorrect chair password."
            )

            return render_template(
                "login.html"
            )

        # ----------------------------------------------------
        # DELEGATE LOGIN
        # ----------------------------------------------------

        if username in DELEGATES:

            if (
                password ==
                DELEGATES[username]["password"]
            ):

                session.clear()

                session["username"] = username

                flash(
                    f"Welcome, {username}."
                )

                return redirect(
                    url_for("profile")
                )

            flash(
                "Incorrect password."
            )

            return render_template(
                "login.html"
            )

        # ----------------------------------------------------
        # PRESS LOGIN
        # ----------------------------------------------------

        if username in PRESS_PASSWORDS:

            if (
                password ==
                PRESS_PASSWORDS[username]
            ):

                session.clear()

                session["username"] = username

                flash(
                    "Press access granted."
                )

                return redirect(
                    url_for("articles")
                )

            flash(
                "Incorrect password."
            )

            return render_template(
                "login.html"
            )

        flash(
            "Account not found."
        )

    return render_template(
        "login.html"
    )


# ============================================================
# PRESS LOGIN
# ============================================================

@app.route(
    "/press-login",
    methods=["GET", "POST"]
)
def press_login():

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
            and
            password == PRESS_PASSWORDS[username]
        ):

            session.clear()

            session["username"] = username

            flash(
                "Press access granted."
            )

            return redirect(
                url_for("articles")
            )

        flash(
            "Invalid press credentials."
        )

    return render_template(
        "press_login.html"
    )


# ============================================================
# CHAIR LOGIN
# ============================================================

@app.route(
    "/chair-login",
    methods=["GET", "POST"]
)
def chair_login():

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        if password == CHAIR_PASSWORD:

            session.clear()

            session["username"] = "__chair__"

            flash(
                "Chair access granted."
            )

            return redirect(
                url_for("crises")
            )

        flash(
            "Incorrect chair password."
        )

    return render_template(
        "chair_login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out."
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

    return render_template(
        "profile.html",
        profile=user
    )


# ============================================================
# NOTES
# ============================================================

@app.route("/notes")
@role_required("delegate")
def notes():

    user = current_user()

    conn = get_db()

    notes_list = conn.execute("""
        SELECT *
        FROM notes
        WHERE username = ?
        ORDER BY updated_at DESC
    """, (
        user["username"],
    )).fetchall()

    conn.close()

    return render_template(
        "notes.html",
        notes=notes_list
    )


# ============================================================
# NEW NOTE
# ============================================================

@app.route(
    "/notes/new",
    methods=["GET", "POST"]
)
@role_required("delegate")
def new_note():

    if request.method == "POST":

        user = current_user()

        title = request.form.get(
            "title",
            ""
        ).strip()

        content = request.form.get(
            "content",
            ""
        )

        if not title:

            flash(
                "Please enter a title."
            )

            return render_template(
                "note_editor.html",
                note=None
            )

        now = datetime.now().isoformat(
            timespec="seconds"
        )

        conn = get_db()

        conn.execute("""
            INSERT INTO notes (
                username,
                title,
                content,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            user["username"],
            title,
            content,
            now,
            now,
        ))

        conn.commit()

        conn.close()

        flash(
            "Note created."
        )

        return redirect(
            url_for("notes")
        )

    return render_template(
        "note_editor.html",
        note=None
    )


# ============================================================
# UPDATE NOTE
# ============================================================

@app.route(
    "/notes/<int:note_id>/update",
    methods=["GET", "POST"]
)
@role_required("delegate")
def update_note(note_id):

    user = current_user()

    conn = get_db()

    note = conn.execute("""
        SELECT *
        FROM notes
        WHERE id = ?
        AND username = ?
    """, (
        note_id,
        user["username"],
    )).fetchone()

    if note is None:

        conn.close()

        abort(404)

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        content = request.form.get(
            "content",
            ""
        )

        if not title:

            flash(
                "Please enter a title."
            )

            conn.close()

            return render_template(
                "note_editor.html",
                note=note
            )

        now = datetime.now().isoformat(
            timespec="seconds"
        )

        conn.execute("""
            UPDATE notes
            SET title = ?,
                content = ?,
                updated_at = ?
            WHERE id = ?
            AND username = ?
        """, (
            title,
            content,
            now,
            note_id,
            user["username"],
        ))

        conn.commit()

        conn.close()

        flash(
            "Note updated."
        )

        return redirect(
            url_for("notes")
        )

    conn.close()

    return render_template(
        "note_editor.html",
        note=note
    )


# ============================================================
# DELETE NOTE
# ============================================================

@app.route(
    "/notes/<int:note_id>/delete",
    methods=["POST"]
)
@role_required("delegate")
def delete_note(note_id):

    user = current_user()

    conn = get_db()

    conn.execute("""
        DELETE FROM notes
        WHERE id = ?
        AND username = ?
    """, (
        note_id,
        user["username"],
    ))

    conn.commit()

    conn.close()

    flash(
        "Note deleted."
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

    user = current_user()

    if request.method == "POST":

        if (
            user is None
            or
            user["role"] != "press"
        ):

            flash(
                "Only the press desk can publish articles."
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

            flash(
                "Title and article body are required."
            )

            return redirect(
                url_for("articles")
            )

        conn = get_db()

        conn.execute("""
            INSERT INTO articles (
                author,
                delegation,
                title,
                body,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            user["username"],
            user.get("delegation"),
            title,
            body,
            datetime.now().isoformat(
                timespec="seconds"
            ),
        ))

        conn.commit()

        conn.close()

        flash(
            "Article published."
        )

        return redirect(
            url_for("articles")
        )

    conn = get_db()

    articles_list = conn.execute("""
        SELECT *
        FROM articles
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "articles.html",
        articles=articles_list
    )


# ============================================================
# FULL ARTICLE
# ============================================================

@app.route(
    "/articles/<int:article_id>"
)
def article(article_id):

    conn = get_db()

    article_data = conn.execute("""
        SELECT *
        FROM articles
        WHERE id = ?
    """, (
        article_id,
    )).fetchone()

    conn.close()

    if article_data is None:

        abort(404)

    return render_template(
        "article.html",
        article=article_data
    )


# ============================================================
# PRESS UPLOAD
# ============================================================

@app.route(
    "/press-upload",
    methods=["GET", "POST"]
)
@role_required("press")
def press_upload():

    if request.method == "POST":

        user = current_user()

        title = request.form.get(
            "title",
            ""
        ).strip()

        body = request.form.get(
            "body",
            ""
        ).strip()

        if not title or not body:

            flash(
                "Title and article body are required."
            )

            return redirect(
                url_for("press_upload")
            )

        conn = get_db()

        conn.execute("""
            INSERT INTO articles (
                author,
                delegation,
                title,
                body,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            user["username"],
            user.get("delegation"),
            title,
            body,
            datetime.now().isoformat(
                timespec="seconds"
            ),
        ))

        conn.commit()

        conn.close()

        flash(
            "Article published."
        )

        return redirect(
            url_for("articles")
        )

    return render_template(
        "press_upload.html"
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

    conn = get_db()

    conn.execute("""
        DELETE FROM articles
        WHERE id = ?
    """, (
        article_id,
    ))

    conn.commit()

    conn.close()

    flash(
        "Article deleted."
    )

    return redirect(
        url_for("articles")
    )


# ============================================================
# CRISES — VIEW
# ============================================================

@app.route(
    "/crises",
    methods=["GET"]
)
def crises():

    conn = get_db()

    crises_list = conn.execute("""
        SELECT *
        FROM crises
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "crises.html",
        crises=crises_list
    )


# ============================================================
# CRISES — PUBLISH
#
# IMPORTANT:
# This is a separate POST handler.
# The @role_required("chair") decorator runs BEFORE
# any crisis can be created.
# ============================================================

@app.route(
    "/crises",
    methods=["POST"]
)
@role_required("chair")
def publish_crisis():

    title = request.form.get(
        "title",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    file = request.files.get(
        "file"
    )

    if not title or not description:

        flash(
            "Crisis title and description are required."
        )

        return redirect(
            url_for("crises")
        )

    filename = None

    if file and file.filename:

        if not allowed_file(
            file.filename
        ):

            flash(
                "That file type is not allowed."
            )

            return redirect(
                url_for("crises")
            )

        safe_filename = (
            file.filename
            .replace("/", "_")
            .replace("\\", "_")
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )

        filename = (
            f"{timestamp}_{safe_filename}"
        )

        file.save(
            os.path.join(
                UPLOAD_FOLDER,
                filename
            )
        )

    conn = get_db()

    conn.execute("""
        INSERT INTO crises (
            title,
            description,
            filename,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        title,
        description,
        filename,
        datetime.now().isoformat(
            timespec="seconds"
        ),
    ))

    conn.commit()

    conn.close()

    flash(
        "Crisis published."
    )

    return redirect(
        url_for("crises")
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

    conn = get_db()

    crisis = conn.execute("""
        SELECT *
        FROM crises
        WHERE id = ?
    """, (
        crisis_id,
    )).fetchone()

    if crisis is not None:

        if crisis["filename"]:

            file_path = os.path.join(
                UPLOAD_FOLDER,
                crisis["filename"]
            )

            if os.path.exists(
                file_path
            ):

                try:
                    os.remove(
                        file_path
                    )

                except OSError:
                    pass

        conn.execute("""
            DELETE FROM crises
            WHERE id = ?
        """, (
            crisis_id,
        ))

        conn.commit()

    conn.close()

    flash(
        "Crisis deleted."
    )

    return redirect(
        url_for("crises")
    )


# ============================================================
# UPLOADS
# ============================================================

@app.route(
    "/uploads/<path:filename>"
)
def uploaded_file(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# ============================================================
# FILE TOO LARGE
# ============================================================

@app.errorhandler(413)
def file_too_large(error):

    flash(
        "The uploaded file is too large. Maximum size is 10 MB."
    )

    return redirect(
        url_for("crises")
    )


# ============================================================
# INITIALIZE DATABASE
# ============================================================

init_db()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
