from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateField, DateTimeField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp


class ProjectForm(FlaskForm):
    package_type = HiddenField('package_type')
    first_name = StringField('First Name *', validators=[DataRequired(message='First name is required'), Length(min=2, max=20)])
    last_name = StringField('Last Name *', validators=[DataRequired(message='Last name is required'), Length(min=2, max=20)])
    email = StringField('Email *', validators=[DataRequired(message='Email is required'), Regexp(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', message='Invalid email address')])
    cell_number = StringField('Cell Number *', validators=[DataRequired(message='Cell number is required'), Regexp(r'^\d{10}$', message='Please enter a valid 10-digit cell number')])
    province = SelectField('Province *', choices=[('Gauteng', 'Gauteng'), ('KwaZulu-Natal', 'KwaZulu-Natal'), ('Free State', 'Free State'), ('Limpopo', 'Limpopo'), ('North West', 'North West'), ('Northern Cape', 'Northern Cape'), ('Western Cape', 'Western Cape'), ('Mpumalanga', 'Mpumalanga'), ('Eastern Cape', 'Eastern Cape'), ('Other', 'Other')], validators=[DataRequired(message='Province is required')], default='Gauteng')
    
    project_name = StringField('Project Name *', validators=[DataRequired(message='Project name is required'), Length(min=2, max=50)])
    project_description = TextAreaField('Project Description *', validators=[DataRequired(message='Project description is required'), Length(min=2, max=500)])
    is_maintenance = BooleanField()

    additional_information = TextAreaField('Additional Information (Optional)')

    submit = SubmitField('Submit Project Request')

class EditClientForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(message='First name is required'), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(message='Last name is required'), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(message='Email is required'), Regexp(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', message='Invalid email address')])
    cell_number = StringField('Cell Number', validators=[DataRequired(message='Cell number is required'), Regexp(r'^\d{10}$', message='Please enter a valid 10-digit cell number')])
    submit = SubmitField('Save Changes')

class StatusUpdateForm(FlaskForm):
    project_status = SelectField('Project', choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], validators=[DataRequired(message='Project status is required')])
    submit = SubmitField('Save Changes')

class ProjectApprovalForm(FlaskForm):
    project_approval = SelectField('Project Approval', choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], validators=[DataRequired(message='Project approval status is required')])
    submit = SubmitField('Save Changes')

class LoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(message='Email is required')])
    password_hash = PasswordField('Password', validators=[DataRequired(message='Password is required')])
    submit = SubmitField('Login')

class IncomeForm(FlaskForm):
    income_type = SelectField('Income Type', choices=[('Wep Application Development', 'Wep Application Development'), ('Monthly Maintenance Fees', 'Monthly Maintenance Fees')], validators=[DataRequired(message='Income type is required')])
    income_amount = StringField('Amount', validators=[DataRequired(message='Amount is required')])
    income_date_time = StringField('Date and Time', validators=[DataRequired(message='Date and Time is required')])
    income_pot = FileField('Proof of Transaction', validators=[DataRequired(message='Proof of Transaction is required')])
    income_description = StringField('Description')
    submit = SubmitField('Save Changes')

class ExpenseForm(FlaskForm):
    expense_type = SelectField('Expense Type', choices=[('Internet and Communication', 'Internet and Communication'), ('Hardware and Equipment', 'Hardware and Equipment'), ('Marketing and Advertising', 'Marketing and Advertising'), ('Professional Services', 'Professional Services'), ('Education and Training', 'Education and Training'), ('Miscellaneous', 'Miscellaneous'), ('Other', 'Other')], validators=[DataRequired(message='Expense type is required')])
    expense_amount = StringField('Amount', validators=[DataRequired(message='Amount is required')])
    is_deductible = BooleanField('Is this expense deductible?')
    description = StringField('Description')
    expense_date_time = StringField('Date and Time', validators=[DataRequired(message='Date and Time is required')])
    expense_pot = FileField('Proof of Transaction', validators=[DataRequired(message='Proof of Transaction is required')])
    submit = SubmitField('Save Changes')

class ReminderForm(FlaskForm):
    datetime =  StringField('Date & Time', validators=[])
    setting = StringField('Setting', validators=[])
    submit = SubmitField('Save Changes')

class ContactPageForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(message='Full Name required')])
    email = StringField('Email Address', validators=[DataRequired(message='Email required')])
    message = StringField('Messsage', validators=[DataRequired(message='Message required')])
    submit = SubmitField('Send')








