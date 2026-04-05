"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file contains the routes for your application.
"""

import os
from uuid import uuid4

from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from flask import flash, redirect, render_template, request, session, url_for
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash

from app import app, db, mail
from app.forms import LoginForm, PropertyForm, SignUpForm
from app.models import Property, UserProfile


###
# Routing for your application.
###


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('manage_properties'))

    form = LoginForm()

    if form.validate_on_submit():
        user = UserProfile.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('manage_properties'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('manage_properties'))

    form = SignUpForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()

        if UserProfile.query.filter_by(username=username).first():
            form.username.errors.append('That username is already in use.')

        if UserProfile.query.filter_by(email=email).first():
            form.email.errors.append('That email address is already registered.')

        if not form.errors:
            user = UserProfile(
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                username=username,
                email=email,
                password=form.password.data,
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Account created successfully.', 'success')
            return redirect(url_for('manage_properties'))

    if request.method == 'POST' and form.errors:
        flash_errors(form)

    return render_template('signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

def get_managed_property_ids():
    return session.get('managed_property_ids', [])


def add_managed_property_id(property_id):
    managed_ids = get_managed_property_ids()
    if property_id not in managed_ids:
        managed_ids.append(property_id)
        session['managed_property_ids'] = managed_ids


def get_managed_properties():
    managed_ids = get_managed_property_ids()
    if not managed_ids:
        return []
    return (
        Property.query
        .filter(Property.id.in_(managed_ids))
        .order_by(Property.id.desc())
        .all()
    )


def save_property_photo(photo):
    filename = secure_filename(photo.filename)
    _, extension = os.path.splitext(filename)
    stored_filename = f'{uuid4().hex}{extension.lower()}'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    photo.save(os.path.join(app.config['UPLOAD_FOLDER'], stored_filename))
    return stored_filename


def remove_property_photo(filename):
    if not filename:
        return

    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(upload_path):
        os.remove(upload_path)


def get_manageable_property(propertyid):
    property = Property.query.get_or_404(propertyid)
    if property.id not in get_managed_property_ids():
        return None
    return property


def property_image_url(filename):
    upload_path = os.path.join(app.static_folder, 'uploads', filename)
    if os.path.exists(upload_path):
        return url_for('static', filename=f'uploads/{filename}')

    image_path = os.path.join(app.static_folder, 'image', filename)
    if os.path.exists(image_path):
        return url_for('static', filename=f'image/{filename}')

    return url_for('static', filename=f'uploads/{filename}')


@app.context_processor
def inject_property_helpers():
    return {'property_image_url': property_image_url}


@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/properties/create', methods=['GET', 'POST'])
@login_required
def create_property():
    form = PropertyForm(require_photo=True)

    if form.validate_on_submit():
        filename = save_property_photo(form.photo.data)

        new_property = Property(
            title=form.title.data,
            description=form.description.data,
            no_of_rooms=form.no_of_rooms.data,
            no_of_bathrooms=form.no_of_bathrooms.data,
            price=form.price.data,
            property_type=form.property_type.data,
            location=form.location.data,
            photo=filename
        )

        db.session.add(new_property)
        db.session.commit()
        add_managed_property_id(new_property.id)
        flash('Property successfully added!', 'success')
        return redirect(url_for('properties'))

    if form.errors:
        flash_errors(form)

    return render_template(
        'create_property.html',
        form=form,
        form_title='Add New Property',
        submit_label='Add Property',
        current_photo=None,
    )


@app.route('/properties')
def properties():
    search_query = request.args.get('q', '').strip()
    properties_query = Property.query

    if search_query:
        search_term = f'%{search_query}%'
        properties_query = properties_query.filter(
            or_(
                Property.title.ilike(search_term),
                Property.location.ilike(search_term),
                Property.property_type.ilike(search_term),
                Property.description.ilike(search_term),
            )
        )

    properties = properties_query.order_by(Property.id.desc()).all()
    return render_template('properties.html', properties=properties, search_query=search_query)


@app.route('/properties/<int:propertyid>')
def property_detail(propertyid):
    property = Property.query.get_or_404(propertyid)
    return render_template('property_detail.html', property=property)


@app.route('/properties/<int:propertyid>/checkout', methods=['GET', 'POST'])
def checkout_property(propertyid):
    property = Property.query.get_or_404(propertyid)

    if request.method == 'POST':
        flash(f'Checkout started for {property.title}.', 'success')
        return redirect(url_for('properties'))

    return render_template('checkout.html', property=property)


@app.route('/manage-properties')
@login_required
def manage_properties():
    properties = get_managed_properties()
    return render_template('MangeProperties.html', properties=properties)


@app.route('/manage-properties/<int:propertyid>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(propertyid):
    property = get_manageable_property(propertyid)
    if property is None:
        flash('You can only edit properties created in this browser session.', 'warning')
        return redirect(url_for('manage_properties'))

    form = PropertyForm(obj=property, require_photo=False)

    if form.validate_on_submit():
        property.title = form.title.data
        property.description = form.description.data
        property.no_of_rooms = form.no_of_rooms.data
        property.no_of_bathrooms = form.no_of_bathrooms.data
        property.price = form.price.data
        property.property_type = form.property_type.data
        property.location = form.location.data

        uploaded_photo = form.photo.data
        if uploaded_photo and getattr(uploaded_photo, 'filename', ''):
            remove_property_photo(property.photo)
            property.photo = save_property_photo(uploaded_photo)

        db.session.commit()
        flash('Property updated successfully.', 'success')
        return redirect(url_for('manage_properties'))

    if form.errors:
        flash_errors(form)

    return render_template(
        'create_property.html',
        form=form,
        form_title='Edit Property',
        submit_label='Save Changes',
        current_photo=property.photo,
    )


@app.route('/properties/<int:propertyid>/email', methods=['POST'])
def email_realtor(propertyid):
    property = Property.query.get_or_404(propertyid)
    recipient = app.config.get('MAIL_RECIPIENT')

    if not recipient:
        flash('Email is not configured. Set MAIL_RECIPIENT or MAIL_DEFAULT_SENDER.', 'danger')
        return redirect(url_for('property_detail', propertyid=propertyid))

    message = Message(
        subject=f'Property inquiry: {property.title}',
        recipients=[recipient],
    )
    message.body = (
        'A visitor requested more information about a property.\n\n'
        f'Title: {property.title}\n'
        f'Location: {property.location}\n'
        f'Price: {property.price}\n'
        f'Property Type: {property.property_type}\n'
        f'Bedrooms: {property.no_of_rooms}\n'
        f'Bathrooms: {property.no_of_bathrooms}\n'
    )

    try:
        mail.send(message)
    except Exception:
        app.logger.exception('Failed to send property inquiry email.')
        flash('The inquiry email could not be sent. Check your mail configuration.', 'danger')
    else:
        flash('Inquiry email sent successfully.', 'success')

    return redirect(url_for('property_detail', propertyid=propertyid))


###
# The functions below should be applicable to all Flask apps.
###


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
