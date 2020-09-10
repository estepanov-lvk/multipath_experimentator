from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FieldList, FormField, Form
from wtforms import SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, IPAddress
from app.models import User, Server

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators = [DataRequired()])
    password = PasswordField('Пароль', validators = [DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Подтвердить')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators = [DataRequired()])
    email = StringField('Почта', validators = [DataRequired(), Email()])
    password = PasswordField('Пароль', validators = [DataRequired()])
    password2 = PasswordField('Повторите пароль', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрировать')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста используйте другое имя пользователя.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста используйте другой почтовый адрес.')

class EditProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    about_me = TextAreaField('О себе', validators=[Length(min=0, max=140)])
    submit = SubmitField('Отправить')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Пожалуйста используйте другое имя пользователя.')

class InterfaceForm(Form):
    interface_name = StringField('Название интерфейса', validators=[DataRequired()])


class ServerAddForm(FlaskForm):
    servername = StringField('Имя сервера', validators=[DataRequired()])
    server_ip = StringField('IP адрес сервера', validators=[DataRequired(), IPAddress()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    interfaces = FieldList(FormField(InterfaceForm), min_entries=0, max_entries=60)
    submit = SubmitField('Добавить')

    def validate_servername(self, servername):
        server = Server.query.filter_by(servername=servername.data).first()
        if server is not None:
            raise ValidationError('Сервер с таким именем уже существует.')

    def validate_server_ip(self, server_ip):
        server = Server.query.filter_by(server_ip=server_ip.data).first()
        if server is not None:
            raise ValidationError('Сервер с таким IP адресом уже существует.')

    def validate_interfaces(self, interfaces):
        interface_names = set()
        for intf in interfaces.data:
            print(intf['interface_name'])
            if intf['interface_name'] in interface_names:
                raise ValidationError('Не может быть двух одинаковых интерфейсов')
            interface_names.add(intf['interface_name'])

class NonValidatingSelectField(SelectField):
    def pre_validate(self, form):
        return True
 
class ConnectionAddForm(FlaskForm):
    server1 = NonValidatingSelectField('Сервер 1', id='serv1')
    int1 = NonValidatingSelectField('Интерфейс на сервере 1', id='int1')
    int2 = NonValidatingSelectField('Интерфейс на сервере 2', id='int2')
    server2 = NonValidatingSelectField('Сервер 2', id='serv2')
    submit = SubmitField('Добавить')

class ConnectionDeleteForm(FlaskForm):
    server1 = NonValidatingSelectField('Сервер 1', id='serv1')
    int1 = NonValidatingSelectField('Интерфейс на сервере 1', id='int1')
    int2 = NonValidatingSelectField('Интерфейс на сервере 2', id='int2')
    server2 = NonValidatingSelectField('Сервер 2', id='serv2')
    submit = SubmitField('Удалить')

 
class ServerDeleteForm(FlaskForm):
    servername = StringField('Имя сервера', validators=[DataRequired()])
    submit = SubmitField('Удалить')

    def validate_servername(self, servername):
        server = Server.query.filter_by(servername=servername.data).first()
        if server is None:
            raise ValidationError('Не существует сервера с таким именем')


class ServerEditForm(FlaskForm):
    servername = StringField('Имя сервера', validators=[DataRequired()])
    server_ip = StringField('IP адрес сервера', validators=[DataRequired(), IPAddress()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    interfaces = FieldList(FormField(InterfaceForm), min_entries=0, max_entries=60)
    submit = SubmitField('Обновить')

    def __init__(self, original_servername, original_ip, *args, **kwargs):
        super(ServerEditForm, self).__init__(*args, **kwargs)
        self.original_servername = original_servername
        self.original_ip = original_ip

    def validate_servername(self, servername):
        if self.original_servername != servername.data:
            server = Server.query.filter_by(servername=servername.data).first()
            if server is not None:
                raise ValidationError('Сервер с таким именем уже существует.')

    def validate_server_ip(self, server_ip):
        if self.original_ip != server_ip.data:
            server = Server.query.filter_by(server_ip=server_ip.data).first()
            if server is not None:
                raise ValidationError('Сервер с таким IP адресом уже существует.')

    def validate_interfaces(self, interfaces):
        pass
 
