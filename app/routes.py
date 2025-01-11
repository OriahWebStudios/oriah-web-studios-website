from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, session, jsonify, current_app, make_response, send_from_directory, send_file
from app.models import db, ProjectTable, Admin, ActivityLog, ExpensesTable, IncomeTable, MeetingTable, ContactTable
from app.forms import ProjectForm, EditClientForm, StatusUpdateForm, ProjectApprovalForm, LoginForm, ExpenseForm, IncomeForm, ReminderForm, ContactPageForm
from app.utils import generate_meeting_link
from app.utils import send_email, allowed_file
from flask_mail import Message
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from app import login_manager
from werkzeug.utils import secure_filename
from flask_session import Session
import csv
import os
import shutil
from datetime import datetime
from io import StringIO


main = Blueprint('main', __name__)

meeting_started = False
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx'}



# Admin Login 
login_manager.login_view = 'main.login'
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password_hash.data):
            session['admin'] = True
            login_user(admin)
            return redirect(url_for('main.admin_panel'))
        else:
            flash('Invalid username or password', 'error-login')
    return render_template('admin/login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logged out successfully', 'success-logout')
    return redirect(url_for('main.login'))

# Homepage
@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

# Contact Page 
@main.route('/contact_page', methods=['GET', 'POST'])
def contact_page():
    form = ContactPageForm()
    contact_data = ContactTable()

    if form.validate_on_submit():
        contact_data.full_name=form.full_name.data
        contact_data.email=form.email.data
        contact_data.message=form.message.data
        db.session.add(contact_data)
        db.session.commit()
        flash('Your message has been successfully sent! Thank you for contacting us.. We will get  back to you as soons as possible.', 'success_contact_page')
        return redirect(url_for('main.success_page'))
    return render_template('contactForm.html', form=form, contact_data=contact_data)

# Begin Project Form
@main.route('/start_project/<package_type>', methods=['GET', 'POST'])
def start_project(package_type):
    form = ProjectForm()
    form.package_type.data = package_type
    return render_template('projectPlanForm.html', form=form)

# Submissions
@main.route('/submit_project', methods=['POST'])
def submit_project():
    form = ProjectForm()

    if form.validate_on_submit():
        province = form.province.data
        is_in_person = province == 'Gauteng'

        meeting_url = generate_meeting_link()

        host_link = f'{meeting_url}&role=host' if meeting_url else None
        participant_link = f'{meeting_url}&role=participant' if meeting_url else None
        print(host_link, participant_link)

        project = ProjectTable(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            cell_number=form.cell_number.data,
            province=province,

            project_name=form.project_name.data,
            project_description=form.project_description.data,
            
            is_maintenance=form.is_maintenance.data,

            additional_information=form.additional_information.data,

            package_type=form.package_type.data,
            meeting_url=participant_link,
        )
        db.session.add(project)
        db.session.commit()

        meeting = MeetingTable(
            full_name = form.first_name.data + ' ' + form.last_name.data,
            meeting_url=host_link
        )
        db.session.add(meeting)
        db.session.commit()

        if is_in_person:
            flash('Thank you for submitting your project request. We’re excited to collaborate with you. A member of our team will be in touch soon to schedule the next steps. ', 'submission-project-home-success')
        else:
            flash('Thank you for submitting your project request. We’re excited to collaborate with you. A member of our team will be in touch soon to schedule the next steps.', 'submission-project-other-success')
        return redirect(url_for('main.success_page'))
    return render_template('projectPlanForm.html', form=form)

# Success Page
@main.route('/success-page')
def success_page():
    return render_template('success_page.html')

# Video Confrence
@main.route('/video-conference')
def video_confrence():
    role = request.args.get('role', 'participant')
    meeting_id = request.args.get('meeting_id')

    if not meeting_id:
        print('Meeting URL not found')
        return redirect(url_for('main.index'))

    is_host = role == 'host'
    return render_template('videoConference.html', meeting_id=meeting_id, is_host=is_host)

@main.route('/start-video-conference', methods=['POST'])
def start_video_conference():
    global meeting_started
    meeting_started = True
    return jsonify({'message': 'Video conference started'})

@main.route('/check-conference-status', methods=['GET'])
def check_conference_status():
    return jsonify({'started': meeting_started})

# Admin Panel
@main.route('/admin_panel', methods=['GET', 'POST'])
@login_required
def admin_panel():
    form = IncomeForm()
    form2 = ExpenseForm()
    reminderForm = ReminderForm()

    if not session.get('admin'):
        return redirect(url_for('main.login'))
    
    response = make_response(redirect(url_for('main.admin_panel')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    recent_logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(5).all()
    clients = ProjectTable.query.all()
    meetings = MeetingTable.query.all()
    income_data = IncomeTable.query.all()
    expense_data = ExpensesTable.query.all()
    proj_client = ProjectTable.query.all()
    total_clients = ProjectTable.query.filter_by(client_status='Active').count()
    total_active_work = ProjectTable.query.filter_by(project_status='In Progress').count()
    host_link = request.args.get('host_link')
    participant_link = request.args.get('participant_link')

    # Financials
    total_revenue = sum([income.income_amount for income in IncomeTable.query.all()])
    total_expenses = sum([expense.expense_amount for expense in ExpensesTable.query.all()])
    taxable_income = total_revenue - total_expenses if total_revenue > total_expenses else 0
    tax_rate = 0.28
    tax_amount = taxable_income * tax_rate if taxable_income > 0 else 0
    net_income = taxable_income - tax_amount    
    provisional_tax = taxable_income * tax_rate if taxable_income > 0 else 0

    return render_template('admin/admin_panel.html', reminderForm=reminderForm ,meetings=meetings, proj_client=proj_client, clients=clients, total_clients=total_clients, total_active_work=total_active_work, recent_logs=recent_logs, income_data=income_data, expense_data=expense_data, form=form, form2=form2, total_revenue=total_revenue, total_expenses=total_expenses, net_income=net_income, tax_amount=tax_amount, taxable_income=taxable_income, provisional_tax=provisional_tax, host_link=host_link, participant_link=participant_link)

@main.route('/check_session')
def check_session():
    return jsonify({'admin': session.get('admin', False)})

@main.route('/clients/view_clients/<int:client_id>', methods=['GET', 'POST'])
@login_required
def view_clients(client_id):
    client = ProjectTable.query.get_or_404(client_id)
    form = EditClientForm()
    form2 = StatusUpdateForm()
    form3 = ProjectApprovalForm()
    return render_template('admin/view_client.html', client=client, form=form, form2=form2, form3=form3)
    

@main.route('/clients/edit/<int:client_id>', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = ProjectTable.query.get_or_404(client_id)
    form = EditClientForm(obj=client)
    if form.validate_on_submit():
        client.first_name = form.first_name.data
        client.last_name = form.last_name.data
        client.email = form.email.data
        client.cell_number = form.cell_number.data
        db.session.commit()

        log = ActivityLog(
            admin_id=None if current_user.is_anonymous else current_user.id,
            actions='Client Details Updated',
            details=f"Details for CID{client.id} have been updated",
            timestamp=datetime.now()
        )
        db.session.add(log)
        db.session.commit()
        flash('Client updated successfully', 'success')
        return redirect(url_for('main.view_clients', client_id=client.id))
    return render_template('admin/view_client.html', form=form, client=client)

@main.route('/clients/status_update/<int:client_id>', methods=['GET', 'POST'])
@login_required
def status_update(client_id):
    client = ProjectTable.query.get_or_404(client_id)
    form2 = StatusUpdateForm(obj=client)
    if form2.validate_on_submit():
        client.project_status = form2.project_status.data
        db.session.commit()
        flash('Status updated successfully', 'success')
        return redirect(url_for('main.view_clients', client_id=client.id))
    return render_template('admin/view_client.html', form2=form2, client=client)

@main.route('/client/project_approval/<int:client_id>', methods=['GET', 'POST'])
@login_required
def project_approval(client_id):
    client = ProjectTable.query.get_or_404(client_id)
    form3 = ProjectApprovalForm(obj=client)
    participant_link = client.meeting_url
    if form3.validate_on_submit():
        client.project_approval = form3.project_approval.data
        db.session.commit()
        if client.project_approval == 'Approved':
           send_email(
                to=client.email,
                subject="Approval of Your Project Proposal",
                template="emails/projects/in_person_confirmation.html", client=client,
                first_name=client.first_name,
                last_name=client.last_name,
                package_type=client.package_type,
                project_name=client.project_name,
            )
        elif client.project_approval == 'Rejected':
            send_email(
                to=client.email,
                subject="Project Rejected",
                template="emails/projects/in_person_confirmation.html", client=client,
                first_name=client.first_name,
                last_name=client.last_name,
                package_type=client.package_type,
                project_name=client.project_name,
            )
        flash('Project approval updated successfully and email sent', 'success')
        return redirect(url_for('main.view_clients', client_id=client.id))
    return render_template('admin/view_client.html', form3=form3, client=client)

@main.route('/clients/contract/<int:client_id>', methods=['GET', 'POST'])
@login_required
def contract(client_id):
    client = ProjectTable.query.get_or_404(client_id)
    return render_template('admin/contracts/contract.html', client=client)

# Generate Contract
@main.route('/clients/send_contract/<int:client_id>', methods=['GET', 'POST'])
@login_required
def send_contract(client_id):
    client = ProjectTable.query.get_or_404(client_id)
    send_email(
        to=client.email,
        subject="Oriah Web Studios - Contract Agreement",
        template="admin/contracts/contract.html", client=client,
        first_name=client.first_name,
        last_name=client.last_name,
        package_type=client.package_type
    )
    return redirect(url_for('main.view_clients', client_id=client.id))

@main.route('/clients/accept_contract/<int:client_id>', methods=['GET', 'POST'])
def accept_contract(client_id):
    client = ProjectTable.query.get_or_404(client_id)
    client.contract = 'Accepted'
    client.client_status = 'Active'
    client.project_status = 'In Progress'
    db.session.commit()
    flash('Contract accepted. You are now part of the Oriah Web Studios family', 'success-contract')
    return redirect(url_for('main.success_page', client_id=client.id))

# Exporting Client Data from Client Table(just in case, might be useful in the future)
@main.route('/export_clients', methods=['GET', 'POST'])
@login_required
def export_clients():
    clients = ProjectTable.query.all()

    csv_data = [['ID', 'First Name', 'Last Name', 'Email', 'Cell Number', 'Province', 'Project Name', 'Package Type']]
    
    for client in clients:
        csv_data.append([client.id, client.first_name, client.last_name, client.email, client.cell_number, client.province, client.project_name, client.package_type])

    output = StringIO()
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL, quotechar='"')
    writer.writerows(csv_data)

    output.seek(0)
    current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=clients_{current_datetime}.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

# Upload Project Content
@main.route('/upload_proj_content/<int:client_id>', methods=['GET', 'POST'])
@login_required
def upload_proj_content(client_id):
    client = ProjectTable.query.get_or_404(client_id)

    
    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = file.filename
            file_extention = os.path.splitext(file.filename)[1]
            filename = f'{client.first_name}_{client.last_name}_{client.project_name}{file_extention}'

            project_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], (client.first_name + ' ' + client.last_name))
            file_path = os.path.join(project_folder, filename)
            os.makedirs(project_folder, exist_ok=True)
            file.save(file_path)
            db.session.commit()

            log = ActivityLog(
                admin_id=None if current_user.is_anonymous else current_user.id,
                actions='Project content uploaded',
                details=f"Content for CID{client.id} have been uploaded",
                timestamp=datetime.now()
            )
            db.session.add(log)
            db.session.commit()
            flash(f'Project content for {client.first_name} {client.last_name} uploaded successfully', 'success')
            return redirect(url_for('main.admin_panel'))
        else:
            flash('Invalid file format', 'error')
    return render_template('admin/admin_panel.html', client=client)

# Download Project Content
@main.route('/download_proj_content/<int:client_id>', methods=['GET', 'POST'])
@login_required
def download_proj_content(client_id):
    client = ProjectTable.query.get_or_404(client_id)

    project_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], (client.first_name + ' ' + client.last_name))
    zip_filename = f'{client.first_name}_{client.last_name}_{client.project_name}.zip'
    zip_filepath = os.path.join(project_folder, zip_filename)

    try:
        shutil.make_archive(zip_filepath[:-4], 'zip', project_folder)
        flash(f'Project content for {client.first_name} {client.last_name} downloaded successfully', 'success')
        return send_file(zip_filepath, as_attachment=True)
    except Exception as e:
        flash(f'Error downloading project content: {str(e)}', 'error')
        return redirect(url_for('main.admin_panel'))
    
    
# Accounting System
@main.route('/add_expenses', methods=['GET', 'POST'])
@login_required
def add_expenses():
    current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    expense_data = ExpensesTable()
    form2 = ExpenseForm()
    form = IncomeForm()
    if form2.validate_on_submit():
        proof_file = form2.expense_pot.data
        if proof_file and allowed_file(proof_file.filename):
            proof_filename = secure_filename(proof_file.filename)
            upload_path = os.path.join(current_app.config['UPLOADED_FILES_DEST'], 'expenses', proof_filename)
            proof_file.save(upload_path)

            expense_data.expense_type=form2.expense_type.data
            expense_data.expense_amount=form2.expense_amount.data
            expense_data.is_deductible=form2.is_deductible.data
            expense_data.description=form2.description.data
            expense_data.expense_date_time=form2.expense_date_time.data
            expense_data.proof_of_transcation=proof_filename
            db.session.add(expense_data)
            db.session.commit()
            flash('Expense and proof of transaction captured successfully', 'success')
            return redirect(url_for('main.admin_panel'))
        else:
            flash('Expense proof file is required', 'error')
    else:
        print(form2.errors)
    return render_template('admin/admin_panel.html', form2=form2, form=form)


@main.route('/add_income', methods=['GET', 'POST'])
@login_required
def add_income():
    income_data = IncomeTable()
    form = IncomeForm()
    form2 = ExpenseForm()
    if form.validate_on_submit():
        proof_file = form.income_pot.data
        if proof_file and allowed_file(proof_file.filename):
            proof_filename = secure_filename(proof_file.filename)
            upload_path = os.path.join(current_app.config['UPLOADED_FILES_DEST'], 'income', proof_filename)
            proof_file.save(upload_path)

            income_data.income_description=form.income_description.data
            income_data.income_amount=form.income_amount.data
            income_data.income_date_time=form.income_date_time.data
            income_data.income_type=form.income_type.data
            income_data.proof_of_transcation=proof_filename
            db.session.add(income_data)
            db.session.commit()
            flash('Income and proof of transaction captured successfully', 'success')
            return redirect(url_for('main.admin_panel'))
        else:
            flash('Income proof file is required', 'error')
            return redirect(url_for('main.admin_panel'))
    else:
        print(form.errors)
    return render_template('admin/admin_panel.html', form=form, form2=form2)

# Meeting Reminder
@main.route('/update_reminder/<int:meeting_id>', methods=['GET', 'POST'])
def update_reminder(meeting_id):
    reminderForm = ReminderForm()
    meeting = MeetingTable.query.get_or_404(meeting_id)
    if reminderForm.validate_on_submit():
        meeting.datetime=reminderForm.datetime.data
        meeting.setting=reminderForm.setting.data
        db.session.commit()
        flash('Meeting reminder updated')
        return redirect(url_for('main.admin_panel'))
    return render_template('admin/admin_panel.html', meeting=meeting)

@main.route('/clients/delete/<int:client_id>', methods=['GET', 'POST'])
@login_required
def web_dev_delete_client(client_id):
    web_dev_client = ProjectTable.query.get_or_404(client_id)
    client = web_dev_client
    if client:
        db.session.delete(client)
        db.session.commit()
        flash('Client deleted successfully', 'success')
    else:
        flash('Client not found', 'error')

    return redirect(url_for('main.admin_panel'))
    




    