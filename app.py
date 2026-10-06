# ============================================================
# ARKANIAN CRISIS COMMITTEE
# COMPLETE FLASK APPLICATION
# ============================================================

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
    abort,
)

import sqlite3
import os
import json


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "acc-development-secret-key-change-in-production"
)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

ARTICLES_FILE = os.path.join(
    BASE_DIR,
    "articles.json"
)

CRISES_FILE = os.path.join(
    BASE_DIR,
    "crises.json"
)

DB_PATH = os.path.join(
    DATA_DIR,
    "acc.db"
)

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


# ============================================================
# MAIN CHAIR PASSWORD
# ============================================================

CHAIR_PASSWORD = "welovekishorsir"


# ============================================================
# PRESS ACCOUNTS
# ============================================================

PRESS_PASSWORDS = {
    "Yukta": "aljazeeraarticles",
    "Nandika": "aarushismybf",
    "Press Head": "susu",
}


# ============================================================
# DELEGATE ACCOUNTS
# ============================================================

DELEGATES = {

    # --------------------------------------------------------
    # SPECIAL CHAIR ACCOUNTS
    # --------------------------------------------------------

    "Crisis Director": {
        "delegation": "Crisis Director",
        "password": "tungtungtungcrisis",
        "role": "chair",
    },

    "fam": {
        "delegation": "fam",
        "password": "VCHG",
        "role": "chair",
    },

    # --------------------------------------------------------
    # NORMAL DELEGATES
    # --------------------------------------------------------

    "Siddhiksha": {
        "delegation": "National Liberation Council",
        "password": "NLC#Liberation2026!Sec",
        "role": "delegate",
    },

    "Shlok": {
        "delegation": "Southern Arkanian Republic",
        "password": "SAR#SouthArkania!948",
        "role": "delegate",
    },

    "Aarush": {
        "delegation": "Transitional Council of Arkania",
        "password": "TCA#Transition!7392",
        "role": "delegate",
    },

    "Nirav": {
        "delegation": "Republic of Selvar",
        "password": "RoS#SelvarPass!401",
        "role": "delegate",
    },

    "Vihaan": {
        "delegation": "Erdan Province",
        "password": "EP#ErdanSecure!827",
        "role": "delegate",
    },

    "Anika": {
        "delegation": "United Civilian Authority",
        "password": "UCA#CivilianAuth!315",
        "role": "delegate",
    },

    "Shrishti": {
        "delegation": "Western Arkanian Republic",
        "password": "WAR#WestArkania!682",
        "role": "delegate",
    },

    "Ryana": {
        "delegation": "Novera",
        "password": "NOV#NoveraAccess!594",
        "role": "delegate",
    },

    "Ridhu": {
        "delegation": "Republic of Darsen",
        "password": "RoD#DarsenState!173",
        "role": "delegate",
    },

    "Siya": {
        "delegation": "Tavria",
        "password": "chaddilicker",
        "role": "delegate",
    },

    "Shruti": {
        "delegation": "Kavren State",
        "password": "KVR#KavrenPass!209",
        "role": "delegate",
    },

    "Sailesh": {
        "delegation": "Arkanian People's Front",
        "password": "APF#PeoplesFront!518",
        "role": "delegate",
    },

    "Naman": {
        "delegation": "Federal Government of Arkania",
        "password": "FGA#FedGovArkania!902",
        "role": "delegate",
    },

    "Ayushman": {
        "delegation": "Arkanian Military Command",
        "password": "AMC#MilitaryCmd!741",
        "role": "delegate",
    },

    "Rizwan": {
        "delegation": "Arkanian Intelligence Directorate",
        "password": "AID#IntelDir2026!613",
        "role": "delegate",
    },

    "Saanvi": {
        "delegation": "Foreign Affairs Office",
        "password": "FAO#ForeignAffairs!384",
        "role": "delegate",
    },

    "Reyansh": {
        "delegation": "Arkanian General Staff",
        "password": "AGS#GeneralStaff!825",
        "role": "delegate",
    },

    "Adele": {
        "delegation": "Arkanian Border Authority",
        "password": "ABA#BorderAuth!491",
        "role": "delegate",
    },

    "Jazlyn": {
        "delegation": "Lorian Autonomous Territory",
        "password": "LAT#LorianTerritory!637",
        "role": "delegate",
    },

    "Shivani": {
        "delegation": "Arkanian Humanitarian Authority",
        "password": "AHA#Humanitarian!158",
        "role": "delegate",
    },

    "Arshita": {
        "delegation": "Highlands of Ordan",
        "password": "HoO#OrdanHighlands!962",
        "role": "delegate",
    },

    "Guna": {
        "delegation": "Free State of Veyra",
        "password": "FSV#VeyraFreeState!407",
        "role": "delegate",
    },

    "Vidhi": {
        "delegation": "Zarev Republic",
        "password": "ZR#ZarevRepublic!831",
        "role": "delegate",
    },

    "Ashima": {
        "delegation": "Maren Coast",
        "password": "MC#MarenCoast!274",
        "role": "delegate",
    },

    "Manisha": {
        "delegation": "Class Teacher",
        "password": "ClassTeach094",
        "role": "delegate",
    },
}


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    conn.execute(
        "PRAGMA busy_timeout = 30000"
    )

    conn.execute(
        "PRAGMA synchronous = NORMAL"
    )

    return conn


def init_db():
    conn = get_db()

    try:

        # WAL can fail on some existing database states.
        try:
            conn.execute(
                "PRAGMA journal_mode = WAL"
            )
        except sqlite3.OperationalError:
            pass

        # ----------------------------------------------------
        # NOTES
        # ----------------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT 'Untitled',
                content TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # DELEGATE STATUS
        # ----------------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS delegate_status (
                username TEXT PRIMARY KEY,
                attendance TEXT NOT NULL DEFAULT 'ABSENT',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # ANNOUNCEMENTS
        # ----------------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL DEFAULT 'GENERAL',
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # DIRECTIVES
        # ----------------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS directives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                delegation TEXT NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'UNDER REVIEW',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # CRISIS RESPONSES
        # ----------------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS crisis_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crisis_index INTEGER NOT NULL,
                username TEXT NOT NULL,
                delegation TEXT NOT NULL,
                response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # VOTES
        # ----------------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                motion TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'OPEN',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # VOTE RECORDS
        # ----------------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS vote_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vote_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                choice TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(vote_id, username)
            )
        """)

        # ----------------------------------------------------
        # MESSAGES
        # ----------------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_read INTEGER NOT NULL DEFAULT 0
            )
        """)

        # ----------------------------------------------------
        # MESSAGE INDEXES
        # ----------------------------------------------------

        conn.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_messages_recipient
            ON messages(recipient)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_messages_unread
            ON messages(recipient, is_read)
        """)

        # ----------------------------------------------------
        # INITIALIZE NORMAL DELEGATES
        # ----------------------------------------------------

        for username, account in DELEGATES.items():

            if account.get(
                "role",
                "delegate"
            ) != "delegate":
                continue

            conn.execute("""
                INSERT OR IGNORE INTO delegate_status
                (
                    username,
                    attendance
                )
                VALUES (?, 'ABSENT')
            """, (
                username,
            ))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ============================================================
# USER SYSTEM
# ============================================================

def current_user():

    username = session.get("username")

    if not username:
        return None

    # --------------------------------------------------------
    # MAIN CHAIR
    # --------------------------------------------------------

    if username == "__chair__":

        return {
            "username": "Chair",
            "display_name": "Chair",
            "delegation": "Chair",
            "role": "chair",
        }

    # --------------------------------------------------------
    # PRESS
    # --------------------------------------------------------

    if username.startswith("__press__:"):

        press_name = username.replace(
            "__press__:",
            "",
            1
        )

        return {
            "username": press_name,
            "display_name": press_name,
            "delegation": "Press",
            "role": "press",
        }

    # --------------------------------------------------------
    # DELEGATES / SPECIAL CHAIRS
    # --------------------------------------------------------

    if username in DELEGATES:

        account = DELEGATES[username]

        return {
            "username": username,
            "display_name": username,
            "delegation": account.get(
                "delegation",
                ""
            ),
            "role": account.get(
                "role",
                "delegate"
            ),
        }

    return None


# ============================================================
# AUTH DECORATORS
# ============================================================

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if current_user() is None:

            flash(
                "Please log in first."
            )

            return redirect(
                url_for("login")
            )

        return function(
            *args,
            **kwargs
        )

    return wrapper


def role_required(required_role):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            user = current_user()

            if user is None:

                flash(
                    "Please log in first."
                )

                return redirect(
                    url_for("login")
                )

            if user.get("role") != required_role:

                flash(
                    "You do not have permission to access that page.",
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
# GLOBAL TEMPLATE CONTEXT
# ============================================================

@app.context_processor
def inject_user():

    user = current_user()

    unread_count = 0

    if user:

        conn = None

        try:

            conn = get_db()

            unread_count = conn.execute("""
                SELECT COUNT(*)
                FROM messages
                WHERE recipient = ?
                AND is_read = 0
            """, (
                user["username"],
            )).fetchone()[0]

        except sqlite3.Error:

            unread_count = 0

        finally:

            if conn:
                conn.close()

    return {
        "user": user,
        "unread_count": unread_count
    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        user=current_user()
    )


# ============================================================
# GENERAL LOGIN
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
        # MAIN CHAIR
        # ----------------------------------------------------

        if (
            username.lower() == "chair"
            and password == CHAIR_PASSWORD
        ):

            session.clear()
            session["username"] = "__chair__"

            flash(
                "Chair access granted."
            )

            return redirect(
                url_for("home")
            )

        # ----------------------------------------------------
        # DELEGATE / SPECIAL CHAIR
        # ----------------------------------------------------

        if username in DELEGATES:

            account = DELEGATES[username]

            if account.get("password") == password:

                session.clear()
                session["username"] = username

                flash(
                    f"Welcome, {username}."
                )

                return redirect(
                    url_for("home")
                )

        flash(
            "Invalid username or password."
        )

    return render_template(
        "login.html",
        user=current_user()
    )


# ============================================================
# DELEGATE LOGIN
# ============================================================

@app.route(
    "/delegate-login",
    methods=["GET", "POST"]
)
def delegate_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if username in DELEGATES:

            account = DELEGATES[username]

            if (
                account.get(
                    "role",
                    "delegate"
                ) == "delegate"
                and account.get(
                    "password"
                ) == password
            ):

                session.clear()
                session["username"] = username

                flash(
                    f"Welcome, {username}."
                )

                return redirect(
                    url_for("home")
                )

        flash(
            "Invalid delegate credentials."
        )

    return render_template(
        "delegate_login.html",
        user=current_user()
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

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        # ----------------------------------------------------
        # MAIN CHAIR
        # ----------------------------------------------------

        if (
            username.lower() == "chair"
            and password == CHAIR_PASSWORD
        ):

            session.clear()
            session["username"] = "__chair__"

            flash(
                "Chair access granted."
            )

            return redirect(
                url_for("home")
            )

        # ----------------------------------------------------
        # SPECIAL CHAIR ACCOUNTS
        # ----------------------------------------------------

        if username in DELEGATES:

            account = DELEGATES[username]

            if (
                account.get("role") == "chair"
                and account.get("password") == password
            ):

                session.clear()
                session["username"] = username

                flash(
                    f"Chair access granted for {username}."
                )

                return redirect(
                    url_for("home")
                )

        flash(
            "Invalid chair credentials."
        )

    return render_template(
        "chair_login.html",
        user=current_user()
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
            and PRESS_PASSWORDS[username] == password
        ):

            session.clear()

            session["username"] = (
                "__press__:" + username
            )

            flash(
                f"Welcome, {username}."
            )

            return redirect(
                url_for("home")
            )

        flash(
            "Invalid press credentials."
        )

    return render_template(
        "press_login.html",
        user=current_user()
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
    attendance = None

    if user["role"] == "delegate":

        conn = get_db()

        try:

            row = conn.execute("""
                SELECT attendance
                FROM delegate_status
                WHERE username = ?
            """, (
                user["username"],
            )).fetchone()

        finally:
            conn.close()

        if row:
            attendance = row["attendance"]

    return render_template(
        "profile.html",
        user=user,
        attendance=attendance
    )


# ============================================================
# INBOX
# ============================================================

@app.route("/inbox")
@login_required
def inbox():

    user = current_user()

    conn = get_db()

    try:

        messages = conn.execute("""
            SELECT
                id,
                sender,
                recipient,
                subject,
                body,
                created_at,
                is_read
            FROM messages
            WHERE recipient = ?
            ORDER BY
                is_read ASC,
                created_at DESC,
                id DESC
        """, (
            user["username"],
        )).fetchall()

        unread_count = conn.execute("""
            SELECT COUNT(*)
            FROM messages
            WHERE recipient = ?
            AND is_read = 0
        """, (
            user["username"],
        )).fetchone()[0]

        return render_template(
            "inbox.html",
            messages=messages,
            unread_count=unread_count,
            user=user
        )

    except sqlite3.Error:

        flash(
            "Could not load your inbox.",
            "error"
        )

        return redirect(
            url_for("home")
        )

    finally:
        conn.close()


# ============================================================
# READ MESSAGE
# ============================================================

@app.route(
    "/inbox/<int:message_id>",
    methods=["GET"]
)
@login_required
def read_message(message_id):

    user = current_user()

    conn = get_db()

    try:

        message = conn.execute("""
            SELECT
                id,
                sender,
                recipient,
                subject,
                body,
                created_at,
                is_read
            FROM messages
            WHERE id = ?
            AND recipient = ?
        """, (
            message_id,
            user["username"]
        )).fetchone()

        if message is None:

            flash(
                "Message not found.",
                "error"
            )

            return redirect(
                url_for("inbox")
            )

        if not message["is_read"]:

            conn.execute("""
                UPDATE messages
                SET is_read = 1
                WHERE id = ?
                AND recipient = ?
            """, (
                message_id,
                user["username"]
            ))

            conn.commit()

            message = conn.execute("""
                SELECT
                    id,
                    sender,
                    recipient,
                    subject,
                    body,
                    created_at,
                    is_read
                FROM messages
                WHERE id = ?
                AND recipient = ?
            """, (
                message_id,
                user["username"]
            )).fetchone()

        return render_template(
            "message.html",
            message=message,
            user=user
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not open message.",
            "error"
        )

        return redirect(
            url_for("inbox")
        )

    finally:
        conn.close()


# ============================================================
# DELETE MESSAGE
# ============================================================

@app.route(
    "/inbox/<int:message_id>/delete",
    methods=["POST"]
)
@login_required
def delete_message(message_id):

    user = current_user()

    conn = get_db()

    try:

        message = conn.execute("""
            SELECT id
            FROM messages
            WHERE id = ?
            AND recipient = ?
        """, (
            message_id,
            user["username"]
        )).fetchone()

        if message is None:

            flash(
                "Message not found.",
                "error"
            )

            return redirect(
                url_for("inbox")
            )

        conn.execute("""
            DELETE FROM messages
            WHERE id = ?
            AND recipient = ?
        """, (
            message_id,
            user["username"]
        ))

        conn.commit()

        flash(
            "Message deleted.",
            "success"
        )

        return redirect(
            url_for("inbox")
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not delete message.",
            "error"
        )

        return redirect(
            url_for("inbox")
        )

    finally:
        conn.close()


# ============================================================
# CHAIR — COMPOSE MESSAGE
# ============================================================

@app.route(
    "/chair-inbox/compose",
    methods=["GET", "POST"]
)
@role_required("chair")
def compose_message():

    conn = get_db()

    try:

        if request.method == "POST":

            recipient = request.form.get(
                "recipient",
                ""
            ).strip()

            subject = request.form.get(
                "subject",
                ""
            ).strip()

            body = request.form.get(
                "body",
                ""
            ).strip()

            if not body:

                body = request.form.get(
                    "description",
                    ""
                ).strip()

            if not recipient or not subject or not body:

                flash(
                    "Recipient, subject, and message are required.",
                    "error"
                )

                return redirect(
                    url_for("compose_message")
                )

            sender = current_user()["display_name"]

            now = datetime.now().isoformat(
                timespec="seconds"
            )

            # ------------------------------------------------
            # SEND TO ALL NORMAL DELEGATES
            # ------------------------------------------------

            if recipient == "__ALL_DELEGATES__":

                recipients = [
                    username
                    for username, account in DELEGATES.items()
                    if account.get(
                        "role",
                        "delegate"
                    ) == "delegate"
                ]

                for username in recipients:

                    conn.execute("""
                        INSERT INTO messages
                        (
                            sender,
                            recipient,
                            subject,
                            body,
                            created_at,
                            is_read
                        )
                        VALUES (?, ?, ?, ?, ?, 0)
                    """, (
                        sender,
                        username,
                        subject,
                        body,
                        now
                    ))

                conn.commit()

                flash(
                    "Message sent to all delegates.",
                    "success"
                )

                return redirect(
                    url_for("compose_message")
                )

            # ------------------------------------------------
            # SEND TO ONE DELEGATE
            # ------------------------------------------------

            if recipient not in DELEGATES:

                flash(
                    "Invalid recipient.",
                    "error"
                )

                return redirect(
                    url_for("compose_message")
                )

            if DELEGATES[recipient].get(
                "role",
                "delegate"
            ) != "delegate":

                flash(
                    "That account cannot receive delegate messages.",
                    "error"
                )

                return redirect(
                    url_for("compose_message")
                )

            conn.execute("""
                INSERT INTO messages
                (
                    sender,
                    recipient,
                    subject,
                    body,
                    created_at,
                    is_read
                )
                VALUES (?, ?, ?, ?, ?, 0)
            """, (
                sender,
                recipient,
                subject,
                body,
                now
            ))

            conn.commit()

            flash(
                "Message sent.",
                "success"
            )

            return redirect(
                url_for("compose_message")
            )

        delegates = [
            {
                "username": username,
                "delegation": account.get(
                    "delegation",
                    username
                )
            }
            for username, account in DELEGATES.items()
            if account.get(
                "role",
                "delegate"
            ) == "delegate"
        ]

        return render_template(
            "compose_message.html",
            delegates=delegates,
            user=current_user()
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not send message.",
            "error"
        )

        return redirect(
            url_for("compose_message")
        )

    finally:
        conn.close()


# ============================================================
# NOTES
# ============================================================

@app.route("/notes")
@login_required
@role_required("delegate")
def notes():

    user = current_user()

    conn = get_db()

    try:

        rows = conn.execute("""
            SELECT
                id,
                username,
                title,
                content,
                created_at,
                updated_at
            FROM notes
            WHERE username = ?
            ORDER BY updated_at DESC, id DESC
        """, (
            user["username"],
        )).fetchall()

        selected_note = None

        note_id = request.args.get(
            "note",
            type=int
        )

        if note_id:

            selected_note = conn.execute("""
                SELECT
                    id,
                    username,
                    title,
                    content,
                    created_at,
                    updated_at
                FROM notes
                WHERE id = ?
                AND username = ?
            """, (
                note_id,
                user["username"]
            )).fetchone()

        if selected_note is None and rows:
            selected_note = rows[0]

        return render_template(
            "notes.html",
            notes=rows,
            selected_note=selected_note,
            user=user
        )

    finally:
        conn.close()


# ============================================================
# CREATE NOTE
# ============================================================

@app.route(
    "/notes/new",
    methods=["GET", "POST"]
)
@login_required
@role_required("delegate")
def new_note():

    user = current_user()

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
            title = "Untitled"

        now = datetime.now().isoformat(
            timespec="seconds"
        )

        conn = get_db()

        try:

            cursor = conn.execute("""
                INSERT INTO notes
                (
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
                now
            ))

            conn.commit()

            note_id = cursor.lastrowid

        except sqlite3.Error:

            conn.rollback()

            flash(
                "Could not create note.",
                "error"
            )

            return redirect(
                url_for("notes")
            )

        finally:
            conn.close()

        flash(
            "Note created.",
            "success"
        )

        return redirect(
            url_for(
                "notes",
                note=note_id
            )
        )

    return redirect(
        url_for("notes")
    )


# ============================================================
# EDIT NOTE
# ============================================================

@app.route(
    "/notes/<int:note_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@role_required("delegate")
def edit_note(note_id):

    user = current_user()

    conn = get_db()

    try:

        note = conn.execute("""
            SELECT
                id,
                username,
                title,
                content,
                created_at,
                updated_at
            FROM notes
            WHERE id = ?
            AND username = ?
        """, (
            note_id,
            user["username"]
        )).fetchone()

        if note is None:

            flash(
                "Note not found.",
                "error"
            )

            return redirect(
                url_for("notes")
            )

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
                title = "Untitled"

            now = datetime.now().isoformat(
                timespec="seconds"
            )

            conn.execute("""
                UPDATE notes
                SET
                    title = ?,
                    content = ?,
                    updated_at = ?
                WHERE id = ?
                AND username = ?
            """, (
                title,
                content,
                now,
                note_id,
                user["username"]
            ))

            conn.commit()

            flash(
                "Note updated.",
                "success"
            )

            return redirect(
                url_for(
                    "notes",
                    note=note_id
                )
            )

        rows = conn.execute("""
            SELECT
                id,
                username,
                title,
                content,
                created_at,
                updated_at
            FROM notes
            WHERE username = ?
            ORDER BY updated_at DESC, id DESC
        """, (
            user["username"],
        )).fetchall()

        return render_template(
            "notes.html",
            notes=rows,
            selected_note=note,
            user=user
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not edit note.",
            "error"
        )

        return redirect(
            url_for("notes")
        )

    finally:
        conn.close()


# ============================================================
# UPDATE NOTE
# ============================================================

@app.route(
    "/notes/<int:note_id>/update",
    methods=["POST"]
)
@login_required
@role_required("delegate")
def update_note(note_id):

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
        title = "Untitled"

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    conn = get_db()

    try:

        note = conn.execute("""
            SELECT id
            FROM notes
            WHERE id = ?
            AND username = ?
        """, (
            note_id,
            user["username"]
        )).fetchone()

        if note is None:

            flash(
                "You do not have permission to edit this note.",
                "error"
            )

            return redirect(
                url_for("notes")
            )

        conn.execute("""
            UPDATE notes
            SET
                title = ?,
                content = ?,
                updated_at = ?
            WHERE id = ?
            AND username = ?
        """, (
            title,
            content,
            now,
            note_id,
            user["username"]
        ))

        conn.commit()

        flash(
            "Note updated.",
            "success"
        )

        return redirect(
            url_for(
                "notes",
                note=note_id
            )
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not update note.",
            "error"
        )

        return redirect(
            url_for("notes")
        )

    finally:
        conn.close()


# ============================================================
# DELETE NOTE
# ============================================================

@app.route(
    "/notes/<int:note_id>/delete",
    methods=["POST"]
)
@login_required
@role_required("delegate")
def delete_note(note_id):

    user = current_user()

    conn = get_db()

    try:

        note = conn.execute("""
            SELECT id
            FROM notes
            WHERE id = ?
            AND username = ?
        """, (
            note_id,
            user["username"]
        )).fetchone()

        if note is None:

            flash(
                "You do not have permission to delete this note.",
                "error"
            )

            return redirect(
                url_for("notes")
            )

        conn.execute("""
            DELETE FROM notes
            WHERE id = ?
            AND username = ?
        """, (
            note_id,
            user["username"]
        ))

        conn.commit()

        flash(
            "Note deleted.",
            "success"
        )

        return redirect(
            url_for("notes")
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not delete note.",
            "error"
        )

        return redirect(
            url_for("notes")
        )

    finally:
        conn.close()


# ============================================================
# ARTICLES
# ============================================================

def load_articles():

    if not os.path.exists(ARTICLES_FILE):
        return []

    try:

        with open(
            ARTICLES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


def save_articles(articles):

    temp_file = ARTICLES_FILE + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            articles,
            file,
            indent=2,
            ensure_ascii=False
        )

    os.replace(
        temp_file,
        ARTICLES_FILE
    )


@app.route("/articles")
def articles():

    return render_template(
        "articles.html",
        articles=load_articles(),
        user=current_user()
    )


@app.route(
    "/articles/<int:index>"
)
def article_view(index):

    articles_data = load_articles()

    if (
        index < 0
        or index >= len(articles_data)
    ):
        abort(404)

    return render_template(
        "article.html",
        article=articles_data[index],
        index=index,
        user=current_user()
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

        title = request.form.get(
            "title",
            ""
        ).strip()

        author = request.form.get(
            "author",
            ""
        ).strip()

        content = request.form.get(
            "content",
            ""
        ).strip()

        image = request.files.get(
            "image"
        )

        if not title or not content:

            flash(
                "Title and article content are required.",
                "error"
            )

            return redirect(
                url_for("press_upload")
            )

        image_filename = ""

        if image and image.filename:

            filename = os.path.basename(
                image.filename
            )

            if filename:

                image_filename = filename

                image.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        filename
                    )
                )

        articles_data = load_articles()

        articles_data.append({
            "title": title,
            "author": (
                author
                or current_user()["username"]
            ),
            "content": content,
            "image": image_filename,
            "created_at": datetime.now().isoformat(
                timespec="seconds"
            )
        })

        save_articles(
            articles_data
        )

        flash(
            "Article uploaded.",
            "success"
        )

        return redirect(
            url_for("articles")
        )

    return render_template(
        "press_upload.html",
        user=current_user()
    )


# ============================================================
# DELETE ARTICLE
# ============================================================

@app.route(
    "/articles/<int:index>/delete",
    methods=["POST"]
)
@role_required("chair")
def delete_article(index):

    articles_data = load_articles()

    if (
        index < 0
        or index >= len(articles_data)
    ):
        abort(404)

    article = articles_data[index]

    image_filename = article.get(
        "image",
        ""
    )

    articles_data.pop(index)

    save_articles(
        articles_data
    )

    if image_filename:

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            os.path.basename(image_filename)
        )

        try:

            if os.path.exists(file_path):
                os.remove(file_path)

        except OSError:
            pass

    flash(
        "Article deleted.",
        "success"
    )

    return redirect(
        url_for("articles")
    )


# ============================================================
# CRISES
# ============================================================

def load_crises():

    if not os.path.exists(CRISES_FILE):
        return []

    try:

        with open(
            CRISES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if not isinstance(data, list):
                return []

            changed = False

            # ------------------------------------------------
            # NORMALIZE OLD CRISIS DATA
            # ------------------------------------------------

            for crisis in data:

                if not isinstance(crisis, dict):
                    continue

                if "title" not in crisis:

                    crisis["title"] = (
                        "Untitled Crisis"
                    )

                    changed = True

                if "body" not in crisis:

                    crisis["body"] = crisis.get(
                        "description",
                        ""
                    )

                    changed = True

                if "description" not in crisis:

                    crisis["description"] = crisis.get(
                        "body",
                        ""
                    )

                    changed = True

                if "filename" not in crisis:

                    crisis["filename"] = ""

                    changed = True

                if "created_at" not in crisis:

                    crisis["created_at"] = ""

                    changed = True

            if changed:

                try:
                    save_crises(data)
                except OSError:
                    pass

            return data

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


def save_crises(crises):

    temp_file = CRISES_FILE + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            crises,
            file,
            indent=2,
            ensure_ascii=False
        )

    os.replace(
        temp_file,
        CRISES_FILE
    )


# ============================================================
# CRISIS PAGE / PUBLISH CRISIS
# ============================================================

@app.route(
    "/crises",
    methods=["GET", "POST"]
)
@role_required("chair")
def crises():

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

            flash(
                "Crisis title and body are required.",
                "error"
            )

            return redirect(
                url_for("crises")
            )

        # ----------------------------------------------------
        # OPTIONAL FILE
        # ----------------------------------------------------

        uploaded_file = request.files.get(
            "file"
        )

        filename = ""

        if (
            uploaded_file
            and uploaded_file.filename
        ):

            original_filename = os.path.basename(
                uploaded_file.filename
            )

            if original_filename:

                filename = original_filename

                uploaded_file.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        filename
                    )
                )

        crises_data = load_crises()

        now = datetime.now().isoformat(
            timespec="seconds"
        )

        crisis = {
            "title": title,
            "body": body,
            "description": body,
            "filename": filename,
            "created_at": now
        }

        crises_data.append(
            crisis
        )

        save_crises(
            crises_data
        )

        flash(
            "Crisis published.",
            "success"
        )

        return redirect(
            url_for("crises")
        )

    return render_template(
        "crises.html",
        crises=load_crises(),
        user=current_user()
    )


# ============================================================
# DELETE CRISIS
# ============================================================

@app.route(
    "/crises/<int:index>/delete",
    methods=["POST"]
)
@role_required("chair")
def delete_crisis(index):

    crises_data = load_crises()

    if (
        index < 0
        or index >= len(crises_data)
    ):

        flash(
            "Crisis not found.",
            "error"
        )

        return redirect(
            url_for("crises")
        )

    crisis = crises_data[index]

    crisis_title = crisis.get(
        "title",
        "Untitled Crisis"
    )

    filename = crisis.get(
        "filename",
        ""
    )

    crises_data.pop(index)

    save_crises(
        crises_data
    )

    if filename:

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            os.path.basename(filename)
        )

        try:

            if os.path.exists(file_path):
                os.remove(file_path)

        except OSError:
            pass

    flash(
        f'Crisis "{crisis_title}" deleted.',
        "success"
    )

    return redirect(
        url_for("crises")
    )


# ============================================================
# CHAIR CONTROL
# ============================================================

@app.route("/chair-control")
@role_required("chair")
def chair_control():

    conn = get_db()

    try:

        statuses = conn.execute("""
            SELECT *
            FROM delegate_status
            ORDER BY username COLLATE NOCASE
        """).fetchall()

        return render_template(
            "chair_control.html",
            statuses=statuses,
            user=current_user()
        )

    finally:
        conn.close()


# ============================================================
# CHAIR TIMER
# ============================================================

@app.route("/chair-timer")
@role_required("chair")
def chair_timer():

    return render_template(
        "chair_timer.html",
        user=current_user()
    )


# ============================================================
# COMMITTEE
# ============================================================

@app.route("/committee")
@login_required
def committee():

    conn = get_db()

    try:

        statuses = conn.execute("""
            SELECT *
            FROM delegate_status
            ORDER BY username COLLATE NOCASE
        """).fetchall()

        return render_template(
            "committee.html",
            statuses=statuses,
            user=current_user()
        )

    finally:
        conn.close()


# ============================================================
# DELEGATES API
# ============================================================

@app.route("/api/delegates")
@login_required
def api_delegates():

    conn = get_db()

    try:

        rows = conn.execute("""
            SELECT *
            FROM delegate_status
            ORDER BY username COLLATE NOCASE
        """).fetchall()

        return {
            "delegates": [
                dict(row)
                for row in rows
            ]
        }

    finally:
        conn.close()


# ============================================================
# LIVE STATE API
# ============================================================

@app.route("/api/live-state")
@login_required
def api_live_state():

    conn = get_db()

    try:

        statuses = conn.execute("""
            SELECT *
            FROM delegate_status
            ORDER BY username COLLATE NOCASE
        """).fetchall()

        announcements = conn.execute("""
            SELECT *
            FROM announcements
            ORDER BY id DESC
            LIMIT 20
        """).fetchall()

        directives = conn.execute("""
            SELECT *
            FROM directives
            ORDER BY updated_at DESC, id DESC
            LIMIT 20
        """).fetchall()

        return {
            "delegates": [
                dict(row)
                for row in statuses
            ],
            "announcements": [
                dict(row)
                for row in announcements
            ],
            "directives": [
                dict(row)
                for row in directives
            ]
        }

    finally:
        conn.close()


# ============================================================
# ANNOUNCEMENTS API
# ============================================================

@app.route("/api/announcements")
@login_required
def api_announcements():

    conn = get_db()

    try:

        rows = conn.execute("""
            SELECT *
            FROM announcements
            ORDER BY id DESC
            LIMIT 50
        """).fetchall()

        return {
            "announcements": [
                dict(row)
                for row in rows
            ]
        }

    finally:
        conn.close()


# ============================================================
# CHAIR ATTENDANCE
# ============================================================

@app.route(
    "/chair-attendance",
    methods=["GET", "POST"]
)
@role_required("chair")
def chair_attendance():

    conn = get_db()

    try:

        # ----------------------------------------------------
        # POST
        # ----------------------------------------------------

        if request.method == "POST":

            updated = 0

            for username, account in DELEGATES.items():

                if account.get(
                    "role",
                    "delegate"
                ) != "delegate":
                    continue

                field_name = (
                    f"attendance_{username}"
                )

                attendance = request.form.get(
                    field_name
                )

                if attendance is None:
                    continue

                attendance = (
                    attendance
                    .strip()
                    .upper()
                )

                valid_attendance = {
                    "ABSENT",
                    "PRESENT",
                    "PRESENT & VOTING"
                }

                if attendance not in valid_attendance:

                    flash(
                        "Invalid attendance status.",
                        "error"
                    )

                    return redirect(
                        url_for("chair_control")
                    )

                conn.execute(
                    """
                    INSERT INTO delegate_status
                    (
                        username,
                        attendance,
                        updated_at
                    )
                    VALUES
                    (
                        ?,
                        ?,
                        CURRENT_TIMESTAMP
                    )
                    ON CONFLICT(username)
                    DO UPDATE SET
                        attendance =
                            excluded.attendance,
                        updated_at =
                            CURRENT_TIMESTAMP
                    """,
                    (
                        username,
                        attendance
                    )
                )

                updated += 1

            if updated == 0:

                flash(
                    "No attendance changes were submitted.",
                    "error"
                )

                return redirect(
                    url_for("chair_control")
                )

            conn.commit()

            flash(
                f"Attendance saved for {updated} delegates.",
                "success"
            )

            return redirect(
                url_for("chair_control")
            )

        # ----------------------------------------------------
        # GET
        # ----------------------------------------------------

        rows = conn.execute("""
            SELECT *
            FROM delegate_status
            ORDER BY username COLLATE NOCASE
        """).fetchall()

        return render_template(
            "chair_control.html",
            statuses=rows,
            user=current_user()
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not save attendance.",
            "error"
        )

        return redirect(
            url_for("chair_control")
        )

    finally:
        conn.close()


# ============================================================
# CHAIR ANNOUNCEMENTS
# ============================================================

@app.route(
    "/chair-announcements",
    methods=["GET", "POST"]
)
@role_required("chair")
def chair_announcements():

    conn = get_db()

    try:

        if request.method == "POST":

            kind = request.form.get(
                "kind",
                "GENERAL"
            ).strip().upper()

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
                    "Announcement title and body are required.",
                    "error"
                )

                return redirect(
                    url_for("chair_announcements")
                )

            conn.execute("""
                INSERT INTO announcements
                (
                    kind,
                    title,
                    body
                )
                VALUES (?, ?, ?)
            """, (
                kind,
                title,
                body
            ))

            conn.commit()

            flash(
                "Announcement published.",
                "success"
            )

            return redirect(
                url_for("chair_announcements")
            )

        rows = conn.execute("""
            SELECT *
            FROM announcements
            ORDER BY id DESC
        """).fetchall()

        return render_template(
            "chair_announcements.html",
            announcements=rows,
            user=current_user()
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not publish announcement.",
            "error"
        )

        return redirect(
            url_for("chair_announcements")
        )

    finally:
        conn.close()


# ============================================================
# DIRECTIVES
# ============================================================

@app.route(
    "/directives",
    methods=["GET", "POST"]
)
@login_required
def directives():

    user = current_user()

    if user["role"] not in (
        "delegate",
        "chair"
    ):

        flash(
            "You do not have permission to access directives.",
            "error"
        )

        return redirect(
            url_for("home")
        )

    conn = get_db()

    try:

        if request.method == "POST":

            if user["role"] != "delegate":

                flash(
                    "Chairs cannot submit directives.",
                    "error"
                )

                return redirect(
                    url_for("directives")
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
                    "Directive title and body are required.",
                    "error"
                )

                return redirect(
                    url_for("directives")
                )

            attendance_row = conn.execute("""
                SELECT attendance
                FROM delegate_status
                WHERE username = ?
            """, (
                user["username"],
            )).fetchone()

            attendance = (
                attendance_row["attendance"]
                if attendance_row
                else "ABSENT"
            )

            if attendance == "ABSENT":

                flash(
                    "You must be marked present before submitting a directive.",
                    "error"
                )

                return redirect(
                    url_for("directives")
                )

            now = datetime.now().isoformat(
                timespec="seconds"
            )

            conn.execute("""
                INSERT INTO directives
                (
                    username,
                    delegation,
                    title,
                    body,
                    status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, 'UNDER REVIEW', ?, ?)
            """, (
                user["username"],
                user["delegation"],
                title,
                body,
                now,
                now
            ))

            conn.commit()

            flash(
                "Directive submitted.",
                "success"
            )

            return redirect(
                url_for("directives")
            )

        # ----------------------------------------------------
        # LOAD DIRECTIVES
        # ----------------------------------------------------

        if user["role"] == "chair":

            rows = conn.execute("""
                SELECT *
                FROM directives
                ORDER BY updated_at DESC, id DESC
            """).fetchall()

        else:

            rows = conn.execute("""
                SELECT *
                FROM directives
                WHERE username = ?
                ORDER BY updated_at DESC, id DESC
            """, (
                user["username"],
            )).fetchall()

        attendance = None

        if user["role"] == "delegate":

            attendance_row = conn.execute("""
                SELECT attendance
                FROM delegate_status
                WHERE username = ?
            """, (
                user["username"],
            )).fetchone()

            if attendance_row:
                attendance = attendance_row["attendance"]

        template_user = {
            **user,
            "attendance": attendance
        }

        return render_template(
            "directives.html",
            directives=rows,
            user=template_user
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not load directives.",
            "error"
        )

        return redirect(
            url_for("home")
        )

    finally:
        conn.close()


# ============================================================
# CHAIR DIRECTIVES
# ============================================================

@app.route(
    "/chair-directives",
    methods=["GET", "POST"]
)
@role_required("chair")
def chair_directives():

    conn = get_db()

    try:

        if request.method == "POST":

            directive_id = request.form.get(
                "directive_id",
                type=int
            )

            status = request.form.get(
                "status",
                ""
            ).strip().upper()

            valid_statuses = {
                "UNDER REVIEW",
                "APPROVED",
                "REJECTED",
                "EXECUTED"
            }

            if directive_id is None:

                flash(
                    "Invalid directive update.",
                    "error"
                )

                return redirect(
                    url_for("chair_directives")
                )

            if status not in valid_statuses:

                flash(
                    "Invalid directive status.",
                    "error"
                )

                return redirect(
                    url_for("chair_directives")
                )

            directive = conn.execute("""
                SELECT id
                FROM directives
                WHERE id = ?
            """, (
                directive_id,
            )).fetchone()

            if directive is None:

                flash(
                    "Directive not found.",
                    "error"
                )

                return redirect(
                    url_for("chair_directives")
                )

            conn.execute("""
                UPDATE directives
                SET
                    status = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                status,
                datetime.now().isoformat(
                    timespec="seconds"
                ),
                directive_id
            ))

            conn.commit()

            flash(
                "Directive status updated.",
                "success"
            )

            return redirect(
                url_for("chair_directives")
            )

        rows = conn.execute("""
            SELECT
                id,
                username,
                delegation,
                title,
                body,
                status,
                created_at,
                updated_at
            FROM directives
            ORDER BY
                updated_at DESC,
                id DESC
        """).fetchall()

        total = len(rows)

        under_review = sum(
            1
            for row in rows
            if row["status"] == "UNDER REVIEW"
        )

        approved = sum(
            1
            for row in rows
            if row["status"] == "APPROVED"
        )

        rejected = sum(
            1
            for row in rows
            if row["status"] == "REJECTED"
        )

        executed = sum(
            1
            for row in rows
            if row["status"] == "EXECUTED"
        )

        return render_template(
            "chair_directives.html",
            directives=rows,
            user=current_user(),
            total=total,
            under_review=under_review,
            approved=approved,
            rejected=rejected,
            executed=executed
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not load directives.",
            "error"
        )

        return redirect(
            url_for("home")
        )

    finally:
        conn.close()


# ============================================================
# DELETE DIRECTIVE
# ============================================================

@app.route(
    "/chair-directives/<int:directive_id>/delete",
    methods=["POST"]
)
@role_required("chair")
def delete_directive(directive_id):

    conn = get_db()

    try:

        directive = conn.execute("""
            SELECT
                id,
                title
            FROM directives
            WHERE id = ?
        """, (
            directive_id,
        )).fetchone()

        if directive is None:

            flash(
                "Directive not found.",
                "error"
            )

            return redirect(
                url_for("chair_directives")
            )

        conn.execute("""
            DELETE FROM directives
            WHERE id = ?
        """, (
            directive_id,
        ))

        conn.commit()

        flash(
            "Directive deleted successfully.",
            "success"
        )

        return redirect(
            url_for("chair_directives")
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not delete directive.",
            "error"
        )

        return redirect(
            url_for("chair_directives")
        )

    finally:
        conn.close()


# ============================================================
# CRISIS RESPONSE
# ============================================================

@app.route(
    "/crises/<int:index>/respond",
    methods=["GET", "POST"]
)
@login_required
@role_required("delegate")
def crisis_response(index):

    user = current_user()

    crises_data = load_crises()

    if (
        index < 0
        or index >= len(crises_data)
    ):
        abort(404)

    crisis = crises_data[index]

    conn = get_db()

    try:

        if request.method == "POST":

            response = request.form.get(
                "response",
                ""
            ).strip()

            if not response:

                flash(
                    "Response cannot be empty.",
                    "error"
                )

                return redirect(
                    url_for(
                        "crisis_response",
                        index=index
                    )
                )

            conn.execute("""
                INSERT INTO crisis_responses
                (
                    crisis_index,
                    username,
                    delegation,
                    response
                )
                VALUES (?, ?, ?, ?)
            """, (
                index,
                user["username"],
                user["delegation"],
                response
            ))

            conn.commit()

            flash(
                "Crisis response submitted.",
                "success"
            )

        responses = conn.execute("""
            SELECT *
            FROM crisis_responses
            WHERE crisis_index = ?
            ORDER BY id DESC
        """, (
            index,
        )).fetchall()

        attendance_row = conn.execute("""
            SELECT attendance
            FROM delegate_status
            WHERE username = ?
        """, (
            user["username"],
        )).fetchone()

        current_attendance = (
            attendance_row["attendance"]
            if attendance_row
            else "ABSENT"
        )

        return render_template(
            "crisis_response.html",
            crisis=crisis,
            responses=responses,
            user={
                **user,
                "attendance": current_attendance
            }
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not submit crisis response.",
            "error"
        )

        return redirect(
            url_for(
                "crisis_response",
                index=index
            )
        )

    finally:
        conn.close()


# ============================================================
# VOTING
# ============================================================

@app.route(
    "/votes",
    methods=["GET", "POST"]
)
@login_required
def votes():

    user = current_user()

    conn = get_db()

    try:

        if request.method == "POST":

            vote_id = request.form.get(
                "vote_id",
                type=int
            )

            choice = request.form.get(
                "choice",
                ""
            ).strip().upper()

            if user["role"] != "delegate":

                flash(
                    "Only delegates can cast votes.",
                    "error"
                )

                return redirect(
                    url_for("votes")
                )

            attendance = conn.execute("""
                SELECT attendance
                FROM delegate_status
                WHERE username = ?
            """, (
                user["username"],
            )).fetchone()

            if (
                not attendance
                or attendance["attendance"]
                != "PRESENT & VOTING"
            ):

                flash(
                    "Only delegates marked PRESENT & VOTING may vote.",
                    "error"
                )

                return redirect(
                    url_for("votes")
                )

            if choice not in {
                "FOR",
                "AGAINST",
                "ABSTAIN"
            }:

                flash(
                    "Invalid vote.",
                    "error"
                )

                return redirect(
                    url_for("votes")
                )

            vote = conn.execute("""
                SELECT *
                FROM votes
                WHERE id = ?
                AND status = 'OPEN'
            """, (
                vote_id,
            )).fetchone()

            if vote is None:

                flash(
                    "That vote is no longer open.",
                    "error"
                )

                return redirect(
                    url_for("votes")
                )

            try:

                conn.execute("""
                    INSERT INTO vote_records
                    (
                        vote_id,
                        username,
                        choice
                    )
                    VALUES (?, ?, ?)
                """, (
                    vote_id,
                    user["username"],
                    choice
                ))

                conn.commit()

                flash(
                    "Vote recorded.",
                    "success"
                )

            except sqlite3.IntegrityError:

                conn.rollback()

                flash(
                    "You have already voted on this motion.",
                    "error"
                )

            return redirect(
                url_for("votes")
            )

        rows = conn.execute("""
            SELECT *
            FROM votes
            ORDER BY id DESC
        """).fetchall()

        return render_template(
            "votes.html",
            votes=rows,
            user=user
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not process vote.",
            "error"
        )

        return redirect(
            url_for("votes")
        )

    finally:
        conn.close()


# ============================================================
# CHAIR VOTE CONTROL
# ============================================================

@app.route(
    "/chair-votes",
    methods=["GET", "POST"]
)
@role_required("chair")
def chair_votes():

    conn = get_db()

    try:

        if request.method == "POST":

            vote_id = request.form.get(
                "vote_id",
                type=int
            )

            action = request.form.get(
                "action",
                ""
            ).strip().lower()

            # ------------------------------------------------
            # CREATE VOTE
            # ------------------------------------------------

            if action == "create":

                title = request.form.get(
                    "title",
                    ""
                ).strip()

                motion = request.form.get(
                    "motion",
                    ""
                ).strip()

                if not title or not motion:

                    flash(
                        "Vote title and motion are required.",
                        "error"
                    )

                    return redirect(
                        url_for("chair_votes")
                    )

                # Close previous open votes.

                conn.execute("""
                    UPDATE votes
                    SET
                        status = 'CLOSED',
                        closed_at = CURRENT_TIMESTAMP
                    WHERE status = 'OPEN'
                """)

                conn.execute("""
                    INSERT INTO votes
                    (
                        title,
                        motion,
                        status,
                        created_at
                    )
                    VALUES (
                        ?,
                        ?,
                        'OPEN',
                        CURRENT_TIMESTAMP
                    )
                """, (
                    title,
                    motion
                ))

                conn.commit()

                flash(
                    "New vote opened live.",
                    "success"
                )

                return redirect(
                    url_for("chair_votes")
                )

            # ------------------------------------------------
            # CLOSE VOTE
            # ------------------------------------------------

            if action == "close":

                if not vote_id:

                    flash(
                        "Invalid vote.",
                        "error"
                    )

                    return redirect(
                        url_for("chair_votes")
                    )

                vote = conn.execute("""
                    SELECT id
                    FROM votes
                    WHERE id = ?
                    AND status = 'OPEN'
                """, (
                    vote_id,
                )).fetchone()

                if vote is None:

                    flash(
                        "That vote is already closed or does not exist.",
                        "error"
                    )

                    return redirect(
                        url_for("chair_votes")
                    )

                conn.execute("""
                    UPDATE votes
                    SET
                        status = 'CLOSED',
                        closed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    vote_id,
                ))

                conn.commit()

                flash(
                    "Vote closed.",
                    "success"
                )

                return redirect(
                    url_for("chair_votes")
                )

        # ----------------------------------------------------
        # LOAD ALL VOTES
        # ----------------------------------------------------

        rows = conn.execute("""
            SELECT *
            FROM votes
            ORDER BY id DESC
        """).fetchall()

        vote_data = []

        for vote in rows:

            results = {}

            for choice in (
                "FOR",
                "AGAINST",
                "ABSTAIN"
            ):

                results[choice] = conn.execute("""
                    SELECT COUNT(*)
                    FROM vote_records
                    WHERE vote_id = ?
                    AND choice = ?
                """, (
                    vote["id"],
                    choice
                )).fetchone()[0]

            total_votes = sum(
                results.values()
            )

            vote_data.append({
                "vote": vote,
                "results": results,
                "total_votes": total_votes
            })

        # ----------------------------------------------------
        # CURRENT OPEN VOTE
        # ----------------------------------------------------

        open_vote = conn.execute("""
            SELECT *
            FROM votes
            WHERE status = 'OPEN'
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()

        open_results = {
            "FOR": 0,
            "AGAINST": 0,
            "ABSTAIN": 0
        }

        open_total = 0

        if open_vote:

            for choice in (
                "FOR",
                "AGAINST",
                "ABSTAIN"
            ):

                open_results[choice] = conn.execute("""
                    SELECT COUNT(*)
                    FROM vote_records
                    WHERE vote_id = ?
                    AND choice = ?
                """, (
                    open_vote["id"],
                    choice
                )).fetchone()[0]

            open_total = sum(
                open_results.values()
            )

        return render_template(
            "chair_votes.html",
            votes=rows,
            vote_data=vote_data,
            open_vote=open_vote,
            open_results=open_results,
            open_total=open_total,
            user=current_user()
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not load voting control.",
            "error"
        )

        return redirect(
            url_for("home")
        )

    finally:
        conn.close()


# ============================================================
# DELETE VOTE
# ============================================================

@app.route(
    "/chair-votes/<int:vote_id>/delete",
    methods=["POST"]
)
@role_required("chair")
def delete_vote(vote_id):

    conn = get_db()

    try:

        vote = conn.execute("""
            SELECT
                id,
                title
            FROM votes
            WHERE id = ?
        """, (
            vote_id,
        )).fetchone()

        if vote is None:

            flash(
                "Vote not found.",
                "error"
            )

            return redirect(
                url_for("chair_votes")
            )

        # ----------------------------------------------------
        # DELETE BALLOTS FIRST
        # ----------------------------------------------------

        conn.execute("""
            DELETE FROM vote_records
            WHERE vote_id = ?
        """, (
            vote_id,
        ))

        # ----------------------------------------------------
        # DELETE VOTE
        # ----------------------------------------------------

        conn.execute("""
            DELETE FROM votes
            WHERE id = ?
        """, (
            vote_id,
        ))

        conn.commit()

        flash(
            f"Vote '{vote['title']}' deleted.",
            "success"
        )

        return redirect(
            url_for("chair_votes")
        )

    except sqlite3.Error:

        conn.rollback()

        flash(
            "Could not delete the vote.",
            "error"
        )

        return redirect(
            url_for("chair_votes")
        )

    finally:
        conn.close()


# ============================================================
# VOTE RESULTS
# ============================================================

@app.route(
    "/votes/<int:vote_id>/results"
)
@login_required
def vote_results(vote_id):

    conn = get_db()

    try:

        vote = conn.execute("""
            SELECT *
            FROM votes
            WHERE id = ?
        """, (
            vote_id,
        )).fetchone()

        if vote is None:
            abort(404)

        results = {}

        for choice in (
            "FOR",
            "AGAINST",
            "ABSTAIN"
        ):

            results[choice] = conn.execute("""
                SELECT COUNT(*)
                FROM vote_records
                WHERE vote_id = ?
                AND choice = ?
            """, (
                vote_id,
                choice
            )).fetchone()[0]

        total_votes = sum(
            results.values()
        )

        return render_template(
            "vote_results.html",
            vote=vote,
            results=results,
            total_votes=total_votes,
            user=current_user()
        )

    finally:
        conn.close()


# ============================================================
# VOTE RESULTS API
# ============================================================

@app.route(
    "/api/votes/<int:vote_id>"
)
@login_required
def api_vote_results(vote_id):

    conn = get_db()

    try:

        vote = conn.execute("""
            SELECT *
            FROM votes
            WHERE id = ?
        """, (
            vote_id,
        )).fetchone()

        if vote is None:

            return {
                "error": "Vote not found"
            }, 404

        results = {}

        for choice in (
            "FOR",
            "AGAINST",
            "ABSTAIN"
        ):

            results[choice] = conn.execute("""
                SELECT COUNT(*)
                FROM vote_records
                WHERE vote_id = ?
                AND choice = ?
            """, (
                vote_id,
                choice
            )).fetchone()[0]

        return {
            "vote": dict(vote),
            "results": results,
            "total_votes": sum(
                results.values()
            )
        }

    finally:
        conn.close()


# ============================================================
# UPLOADS
# ============================================================

@app.route(
    "/uploads/<path:filename>"
)
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# ============================================================
# FILE SIZE ERROR
# ============================================================

@app.errorhandler(413)
def too_large(error):

    flash(
        "The uploaded file is too large."
    )

    return redirect(
        url_for("home")
    )


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

# IMPORTANT:
# This MUST be at top level.
# It must NOT be inside a route/function.

init_db()


# ============================================================
# RUN LOCAL SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )
