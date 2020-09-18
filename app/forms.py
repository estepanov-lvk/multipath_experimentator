from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FieldList, FormField, Form
from wtforms import SelectField, SelectMultipleField, IntegerField
from wtforms import widgets
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, IPAddress
from app.models import User, Server, VM, Topo
from config import Config

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
 
class VMAddForm(FlaskForm):
    vmname = StringField('Имя виртуальной машины', validators=[DataRequired()])
    vm_ip = StringField('IP адрес виртуальной машины', validators=[DataRequired(), IPAddress()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    servername = NonValidatingSelectField('Имя сервера', validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def validate_vmname(self, vmname):
        vm = VM.query.filter_by(vmname=vmname.data).first()
        if vm is not None: 
            raise ValidationError('Виртуальная машина с таким именем уже существует.')

    def validate_vm_ip(self, vm_ip):
        vm = VM.query.filter_by(vm_ip=vm_ip.data).first()
        if vm is not None:
            raise ValidationError('Виртуальная машина с таким IP адресом уже существует.')


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
 
class VMDeleteForm(FlaskForm):
    vmname = StringField('Имя виртуальной машины', validators=[DataRequired()])
    submit = SubmitField('Удалить')

    def validate_vmname(self, vmname):
        vm = VM.query.filter_by(vmname=vmname.data).first()
        if vm is None:
            raise ValidationError('Не существует виртуальной машины с таким именем')


class VMEditForm(FlaskForm):
    vmname = StringField('Имя виртуальной машины', validators=[DataRequired()])
    vm_ip = StringField('IP адрес виртуальной машины', validators=[DataRequired(), IPAddress()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    servername = NonValidatingSelectField('Имя сервера', validators=[DataRequired()])
    submit = SubmitField('Обновить')

    def __init__(self, original_vmname, original_ip, *args, **kwargs):
        super(VMEditForm, self).__init__(*args, **kwargs)
        self.original_vmname = original_vmname
        self.original_ip = original_ip

    def validate_vmname(self, vmname):
        if self.original_vmname != vmname.data:
            vm = VM.query.filter_by(vmname=vmname.data).first()
            if vm is not None:
                raise ValidationError('Виртуальная машина с таким именем уже существует.')

    def validate_vm_ip(self, vm_ip):
        if self.original_ip != vm_ip.data:
            vm = VM.query.filter_by(vm_ip=vm_ip.data).first()
            if vm is not None:
                raise ValidationError('Виртуальная машина с таким IP адресом уже существует.')
 
 
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
 
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


def generate_topos_choices():
    topos = Topo.query.all()
    topos_params = [(x.name, x.nodes, x.edges) for x in topos]
    topos_params = sorted(topos_params, key=lambda x: x[1])
    return [(x[0], x[0] + " (" + str(x[1]) + ", " + str(x[2]) + ")") for x in topos_params]

class ExperimentAddForm(FlaskForm):
    mode_choices_list = Config.MODE_CHOICES
    mode_choices = [(x, x) for x in mode_choices_list]
    mode = MultiCheckboxField("Режим", choices=mode_choices)

    model_choices_list = Config.MODEL_CHOICES
    model_choices = [(x, x) for x in model_choices_list]
    model = MultiCheckboxField("Маршрутизация", choices=model_choices)

    subflow = StringField('Максимальное количество подпотоков (пример: 1, 2, 4):', validators=[DataRequired()])

    cc_choices_list = Config.CC_CHOICES
    cc_choices = [(x, x) for x in cc_choices_list]
    cc = MultiCheckboxField("Алгоритм управления перегрузкой", choices = cc_choices)

    distribution_choices_list = Config.DISTRIBUTION_CHOICES
    distribution_choices = [(x, x) for x in distribution_choices_list]
    distribution = MultiCheckboxField("Распределение времени старта потоков", choices = distribution_choices)

    protocol_choices_list = Config.PROTOCOL_CHOICES
    protocol_choices = [(x, x) for x in protocol_choices_list]
    protocol = MultiCheckboxField("Протокол", choices = protocol_choices)

    topos_choices = generate_topos_choices()
    topos = MultiCheckboxField("Топологии", choices = topos_choices)

    time = StringField('Время проведения одного эксперимента в секундах (пример: 60, 360):', validators=[DataRequired()])

    flows = StringField('Количество потоков в эксперименте (пример: 1000, 100):', validators=[DataRequired()])

    poles = StringField('Количество полюсов в процентном соотношении с количеством узлов в топологии (пример: 30, 70):', validators=[DataRequired()])

    probe = IntegerField('Количество повторов одного эксперимента (пример: 10):', validators=[DataRequired()])

    poles_seed = StringField('Инициализатор генератора случайного распределения полюсов (пример: 0, 1):', validators=[DataRequired()])
    routes_seed = StringField('Инициализатор генератора случайного распределения маршрутов потоков (пример: 0, 1):', validators=[DataRequired()])

    submit = SubmitField('Добавить')

    def validate_mode(self, mode):
        if not mode.data:
            raise ValidationError("Хотя бы один параметр должен быть выбран")

    def validate_model(self, model):
        if not model.data:
            raise ValidationError("Хотя бы один параметр должен быть выбран")

    def validate_cc(self, cc):
        if not cc.data:
            raise ValidationError("Хотя бы один параметр должен быть выбран")

    def validate_protocol(self, protocol):
        if not protocol.data:
            raise ValidationError("Хотя бы один параметр должен быть выбран")

    def validate_distribution(self, distribution):
        if not distribution.data:
            raise ValidationError("Хотя бы один параметр должен быть выбран")

    def validate_topos(self, topos):
        if not topos.data:
            raise ValidationError("Хотя бы один параметр должен быть выбран")

