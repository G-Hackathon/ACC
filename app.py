from flask import Flask, render_template, request, redirect, session
import json
import os
from datetime import datetime
import time

app = Flask(__name__)

app.secret_key = "acc-chair-secret-key-change-this-later"


# ============================================================
# ACC ACCOUNTS
# ============================================================

PRESS_DELEGATES = {
    "yukta": {
        "password": "aljazeeraarticles",
        "name": "Yukta",
        "publication": "Al Jazeera"
    },

    "nandika": {
        "password": "aarushismybf",
        "name": "Nandika",
        "publication": "Reuters"
    }
}

CHAIR_PASSWORD = "welovekishorsir"


# ============================================================
# ARTICLE STORAGE
# ============================================================

ARTICLES_FILE = "articles.json"


def load_articles():

    if not os.path.exists(ARTICLES_FILE):
        return []

    try:

        with open(ARTICLES_FILE, "r", encoding="utf-8") as file:
            articles = json.load(file)

        if not isinstance(articles, list):
            return []

        changed = False

        # ----------------------------------------------------
        # Give older articles an ID if they don't have one.
        # ----------------------------------------------------

        for article in articles:

            if not article.get("id"):

                article["id"] = int(time.time() * 1000000)

                time.sleep(0.001)

                changed = True

        # Save the repaired article list.
        if changed:
            save_articles(articles)

        return articles

    except (json.JSONDecodeError, OSError):

        return []


def save_articles(articles):

    with open(ARTICLES_FILE, "w", encoding="utf-8") as file:

        json.dump(
            articles,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template("index.html")


# ============================================================
# ARTICLES
# ============================================================

@app.route("/articles")
def articles():

    all_articles = load_articles()

    return render_template(
        "articles.html",
        articles=all_articles
    )


# ============================================================
# FULL ARTICLE
# ============================================================

@app.route("/article/<article_id>")
def full_article(article_id):

    all_articles = load_articles()

    selected_article = None

    for article in all_articles:

        stored_id = str(article.get("id", "")).strip()

        if stored_id == str(article_id).strip():

            selected_article = article
            break

    # If the article genuinely doesn't exist,
    # return to the archive.
    if selected_article is None:

        return redirect("/articles")

    return render_template(
        "article.html",
        article=selected_article
    )


# ============================================================
# PRESS LOGIN
# ============================================================

@app.route("/press-login", methods=["GET", "POST"])
def press_login():

    if request.method == "POST":

        delegate = request.form.get(
            "delegate",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        user = PRESS_DELEGATES.get(delegate)

        if user and password == user["password"]:

            # Make sure the browser isn't also in chair mode.
            session.pop("chair_authenticated", None)

            session["press_authenticated"] = True
            session["press_name"] = user["name"]
            session["press_publication"] = user["publication"]

            return redirect("/articles")

        return render_template(
            "press_login.html",
            error="Incorrect delegate or password."
        )

    return render_template("press_login.html")


# ============================================================
# PRESS UPLOAD
# ============================================================

@app.route("/press-upload", methods=["GET", "POST"])
def press_upload():

    if not session.get("press_authenticated"):

        return redirect("/press-login")

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        content = request.form.get(
            "content",
            ""
        ).strip()

        if not title or not content:

            return render_template(
                "press_upload.html",
                name=session.get("press_name"),
                publication=session.get("press_publication"),
                error="Please complete both the title and article."
            )

        all_articles = load_articles()

        # Make an extremely unlikely-to-collide ID.
        new_id = int(time.time() * 1000000)

        new_article = {

            "id": new_id,

            "title": title,

            "content": content,

            "author": session.get(
                "press_name"
            ),

            "publication": session.get(
                "press_publication"
            ),

            "date": datetime.now().strftime(
                "%d %B %Y"
            ),

            "time": datetime.now().strftime(
                "%H:%M"
            )
        }

        all_articles.insert(
            0,
            new_article
        )

        save_articles(
            all_articles
        )

        # IMPORTANT:
        # Go directly to the full article.
        return redirect(
            f"/article/{new_id}"
        )

    return render_template(
        "press_upload.html",
        name=session.get("press_name"),
        publication=session.get("press_publication")
    )


# ============================================================
# CHAIR LOGIN
# ============================================================

@app.route("/chair-login", methods=["GET", "POST"])
def chair_login():

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        if password == CHAIR_PASSWORD:

            # Completely clear press access.
            session.pop(
                "press_authenticated",
                None
            )

            session.pop(
                "press_name",
                None
            )

            session.pop(
                "press_publication",
                None
            )

            session["chair_authenticated"] = True

            return redirect("/articles")

        return render_template(
            "chair_login.html",
            error="Incorrect chair password."
        )

    return render_template(
        "chair_login.html"
    )


# ============================================================
# DELETE ARTICLE
# ============================================================

@app.route(
    "/delete-article/<article_id>",
    methods=["POST"]
)
def delete_article(article_id):

    if not session.get("chair_authenticated"):

        return redirect("/chair-login")

    all_articles = load_articles()

    updated_articles = []

    for article in all_articles:

        if str(article.get("id", "")) != str(article_id):

            updated_articles.append(article)

    save_articles(
        updated_articles
    )

    return redirect("/articles")


# ============================================================
# LOGOUT
# ============================================================

@app.route("/press-logout")
def press_logout():

    session.pop(
        "press_authenticated",
        None
    )

    session.pop(
        "press_name",
        None
    )

    session.pop(
        "press_publication",
        None
    )

    return redirect("/articles")


@app.route("/chair-logout")
def chair_logout():

    session.pop(
        "chair_authenticated",
        None
    )

    return redirect("/articles")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
