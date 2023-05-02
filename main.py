from flask import Flask, render_template, make_response, jsonify, send_file, Response
from flask_login import login_user, current_user, login_required, logout_user, LoginManager
from useful import get_secret_key, make_qr
from data import db_session, users, projects, ratings
from forms import LoginForm, UploadProjectForm, EditProjectForm, RegisterForm, RateProjectForm

from werkzeug.utils import redirect, secure_filename
from werkzeug.exceptions import abort
from werkzeug.wsgi import FileWrapper

from consts.access_levels import ACCESS_LEVELS
from consts.grades import GRADES
from consts.strings import DOMAIN

from io import BytesIO
import qrcode

app = Flask(__name__)

app.config["SECRET_KEY"] = get_secret_key()

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/database.db")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"code": 404, "error": "Not found"}), 404)  # TODO: страница 404


@app.route("/")
def main_page():
    params = {"ACCESS_LEVELS": ACCESS_LEVELS}

    session = db_session.create_session()
    if current_user.is_authenticated:
        if current_user.access_level == ACCESS_LEVELS.user.value:
            params["table_data"] = []
            for project in session.query(projects.Project).filter(projects.Project.user_id == current_user.id):
                params["table_data"].append(project)
    return render_template("home.html", **params)  # TODO: html


@app.route("/login", methods=["GET", "POST"])
def login():
    params = {}
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(users.User).filter(users.User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template("login.html", message="Неверные логин или пароль", form=form,
                               **params)  # TODO: params
    return render_template("login.html", title="Авторизация", form=form, **params)


@app.route("/register", methods=["GET", "POST"])
def register():
    params = {"GRADES": GRADES}
    if current_user.is_authenticated:
        return redirect("/")
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if form.password.data != form.repeat_password.data:
            return render_template("register.html", form=form, message="Пароли не совпадают!")
        if session.query(users.User).filter(users.User.login == form.login.data).first():
            return render_template("register.html", form=form, message="Такой e-mail уже зарегистрирован!")
        user = users.User(
            login=form.login.data,
            name=form.name.data,
            surname=form.surname.data,
            patronymic=form.patronymic.data,
            grade=form.grade.data,
            access_level=ACCESS_LEVELS.user.value
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect("/login")
    return render_template("register.html", form=form, **params)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    params = {}
    form = UploadProjectForm()
    if form.validate_on_submit():
        session = db_session.create_session()

        project = projects.Project(
            title=form.title.data,
            user_id=current_user.id,
            idea=form.idea.data,
            presentation=form.presentation.data
        )
        session.add(project)
        session.commit()
        return redirect("/")
    return render_template("upload.html", title="Загрузка проекта", form=form, **params)  # TODO: html


@app.route("/project_qr/<int:id>", methods=["GET", "POST"])
def project_qr(id):
    try:
        img = qrcode.make(f"{DOMAIN}/project/{id}")

        b = BytesIO()
        img.save(b, "PNG")
        b.seek(0)
        response = Response(b.read(), mimetype="image/png", direct_passthrough=True)
        response.headers.set('Content-Disposition', 'attachment', filename=f"qr-{id}.png")
        return response
    except Exception as e:
        return redirect("/")


@app.route("/project_delete/<int:id>", methods=["GET", "POST"])
@login_required
def project_delete(id):
    session = db_session.create_session()
    project = session.query(projects.Project).filter(projects.Project.id == id).first()
    if project:
        if project.user_id != current_user.id:
            return redirect("/")
        session.delete(project)
        session.commit()
    return redirect("/")


@app.route("/project_edit/<int:id>", methods=["GET", "POST"])
@login_required
def project_edit(id):
    session = db_session.create_session()
    project = session.query(projects.Project).filter(projects.Project.id == id).first()
    if project:
        if project.user_id != current_user.id:
            return redirect("/")
    form = EditProjectForm()
    params = {"project": project}

    if form.validate_on_submit():
        session.query(projects.Project).filter_by(id=id).update({
            projects.Project.title: form.title.data,
            projects.Project.idea: form.idea.data,
            projects.Project.presentation: form.presentation.data
        })
        session.commit()
        return redirect("/")

    if project:
        return render_template("project_edit.html", form=form, **params)
    abort(404)
    return redirect("/")
    # TODO закончить +html


@app.route("/project/<int:id>")
def project_watch(id):
    session = db_session.create_session()
    project = session.query(projects.Project).filter(projects.Project.id == id).first()
    if project is None:
        return render_template("project_not_found.html")
    user = session.query(users.User).filter(users.User.id == project.user_id).first()
    params = {"project": project, "user": user}
    if project:
        return render_template("project.html", **params)


@app.route("/project_rate/<int:id>", methods=["GET", "POST"])
@login_required
def project_rate(id):
    session = db_session.create_session()
    form = RateProjectForm()
    project = session.query(projects.Project).filter(projects.Project.id == id).first()
    if project is None:
        return render_template("project_not_found.html")
    user = session.query(users.User).filter(users.User.id == project.user_id).first()
    params = {"project_id": id, "project": project, "user": user}
    if form.validate_on_submit():
        current_rating = session.query(ratings.Rating).filter(ratings.Rating.project_id == project.id and ratings.Rating.expert_id == current_user.id).first()
        if current_rating is None:
            rating = ratings.Rating(
                project_id=project.id,
                expert_id=current_user.id,
                story=form.story.data,
                depth=form.depth.data,
                total=form.total.data
            )
            session.add(rating)
            session.commit()
        else:
            session.query(ratings.Rating).filter_by(id=current_rating.id).update({
                ratings.Rating.story: form.story.data,
                ratings.Rating.depth: form.depth.data,
                ratings.Rating.total: form.total.data
            })
            session.commit()
        return redirect("/")
    return render_template("project_rate.html", form=form, **params)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(users.User).get(user_id)


if __name__ == "__main__":
    app.run()
