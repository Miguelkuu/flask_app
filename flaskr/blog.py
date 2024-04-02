from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required
from flaskr.db import get_db

# UPLOAD_FOLDER = 'C:\Users\migue\OneDrive\Desktop\csvjson\learn\flask-tutorial\temp_files'
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

bp = Blueprint('blog', __name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username, color"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        color = request.form["color"]
        error = None

        if not title:
            error = "Title is required."

        # try:
        #     file = request.form.get('file')
        #     UPLOAD_FOLDER = 'C:/Users/migue/OneDrive/Desktop/csvjson/learn/flask-tutorial/temp_files'
        #     file.save(secure_filename(file.filename))
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'],\
        #              filename))


        # except error:
        #     error = "Failed uploading file"

        if error is not None:
            flash(error)
        
        else:
            # print(file)
            # j = open(file, "r+b")
            # with j:
            #     filename = j.load()
            # data = readData(file)

            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, color, author_id, filename) VALUES (?, ?, ?, ?)",
                (title, body, color, g.user["id"]),
            )
            db.commit()
            # if file:
            #     with open(file, 'rb') as myfile:
            #         binaryData = myfile.read()
            #     db.execute(
            #         "INSERT INTO post (filename) VALUES (?)",
            #         (binaryData))
            # db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


# def readData(file):
#     fl = open(file, 'rb')
#     with fl:
#         data = fl.read()
#     return data



@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        color = request.form["color"]
        photo = request.form["photo"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, color, id, photo)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))


# def allowed_file(filename):
#     return '.' in filename and \
#         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# def convert_to_binary(filename):
#     with open(filename, 'rb') as file:
#         blobData = file.read()
#     return blobData


# def insert_into_post(id, myFile):
#     get_post(id)
#     db = get_db()
#     db.execute("UPDATE post SET filename = ?, WHERE id = ?", (myFile, id))
#     db.commit()