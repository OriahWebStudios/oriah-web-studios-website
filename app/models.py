from app import db
from app import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash


class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50), nullable=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.id

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class MeetingTable(db.Model):
    __tablename__ = 'meeting_table'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(20), nullable=False)
    meeting_url = db.Column(db.String(300), nullable=True)
    datetime = db.Column(db.String(50), nullable=False, default='Date & Time Not Available')
    setting = db.Column(db.String(50), nullable=False, default='Virtual')

class ProjectTable(db.Model):
    __tablename__ = 'project_table'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    cell_number = db.Column(db.String(20), nullable=False)
    province = db.Column(db.String(20), nullable=False)
    project_name = db.Column(db.String(50), nullable=False)
    project_description = db.Column(db.Text, nullable=False)
    is_maintenance = db.Column(db.Boolean, nullable=False, default=False)
    additional_information = db.Column(db.Text, nullable=False)
    package_type = db.Column(db.String(20), nullable=False)
    client_status = db.Column(db.String(20), nullable=False, default='Pending')
    project_status = db.Column(db.String(20), nullable=False, default='Pending')
    project_approval = db.Column(db.String, nullable=False, default='Pending')
    contract = db.Column(db.String(100), nullable=False, default='Pending')
    meeting_url = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"ProjectTable('{self.first_name}', '{self.last_name}', '{self.email}', '{self.cell_number}', '{self.project_name}', '{self.project_description}')"

class ActivityLog(db.Model):
    __tablename__ = 'activity_log' 
    id = db.Column(db.Integer, primary_key=True) 
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False) 
    actions = db.Column(db.String(50), nullable=False, default='Not Available') 
    details = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    admin = db.relationship('Admin', backref='activity_log')

    def __repr__(self):
        return f"ActivityLog('{self.admin_id}', '{self.actions}', '{self.details}', '{self.timestamp}')"

class ExpensesTable(db.Model):
    __tablename__ = 'expenses_table'

    id = db.Column(db.Integer, primary_key=True)
    expense_type = db.Column(db.String(50), nullable=False)
    expense_amount = db.Column(db.Float, nullable=False)
    is_deductible = db.Column(db.Boolean, nullable=False)
    description = db.Column(db.Text, nullable=False)
    proof_of_transcation = db.Column(db.String, nullable=False, default='Not Available')
    expense_date_time = db.Column(db.String, nullable=False)

class IncomeTable(db.Model):
    __tablename__ = 'income_table'

    id = db.Column(db.Integer, primary_key=True)
    income_type = db.Column(db.String(50), nullable=False)
    income_description = db.Column(db.Text, nullable=False)
    income_amount = db.Column(db.Float, nullable=False)
    income_date_time = db.Column(db.String, nullable=False)
    proof_of_transcation = db.Column(db.String, nullable=False, default='Not Available')

class ContactTable(db.Model):
    __tablename__ = 'contact_table'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)


