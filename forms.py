from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, FileField, SelectField
from wtforms.validators import DataRequired

from consts.grades import GRADES


class LoginForm(FlaskForm):
    login = EmailField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    login = EmailField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    repeat_password = PasswordField('Повторите пароль', validators=[DataRequired()])

    name = StringField("Имя", validators=[DataRequired()])
    surname = StringField("Фамилия", validators=[DataRequired()])
    patronymic = StringField("Отчество")
    grade = SelectField("Класс", choices=GRADES)

    submit = SubmitField("Зарегистрироваться")


class UploadProjectForm(FlaskForm):
    title = StringField("Название проекта", validators=[DataRequired()])
    idea = StringField("Идея проекта", validators=[DataRequired()])
    presentation = StringField("Ссылка на презентацию проекта", validators=[DataRequired()])
    submit = SubmitField("Загрузить")


class EditProjectForm(FlaskForm):
    title = StringField("Название проекта", validators=[DataRequired()])
    idea = StringField("Идея проекта", validators=[DataRequired()])
    presentation = StringField("Ссылка на презентацию проекта", validators=[DataRequired()])
    submit = SubmitField("Сохранить")