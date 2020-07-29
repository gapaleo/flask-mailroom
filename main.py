import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import pbkdf2_sha256

from model import Donation, Donor, User

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY').encode()


@app.route('/')
def home():
    return redirect(url_for('all'))


@app.route('/donations')
def all():
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        donor_name = request.form['donor-name']

        try:
            donor = Donor.get(Donor.name == donor_name)
        except Donor.DoesNotExist:
            donor = Donor.create(name=donor_name)

        Donation.create(value=request.form['donation-amount'], donor=donor)
        return redirect(url_for('all'))

    return render_template('create.jinja2')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = User.get(User.name == request.form['name'])
        except User.DoesNotExist:
            return render_template('login.jinja2', error='Incorrect username or password.')
        if pbkdf2_sha256.verify(request.form['password'], user.password):
            session['username'] = request.form['name']
            return redirect(url_for('create'))
        return render_template('login.jinja2', error='Incorrect username or password.')
    return render_template('login.jinja2')


@app.route('/donors')
def donors():
    donor_name = request.args.get('donor-name', None)
    if donor_name is None:
        return render_template('donors.jinja2')

    try:
        donor = Donor.get(Donor.name == donor_name)
    except Donor.DoesNotExist:
        return render_template('donors.jinja2', error="Donor does not exist.")

    donations = donor.donations
    return render_template('donors.jinja2', donations=donations)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)
