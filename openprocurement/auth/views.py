from openprocurement.auth.provider_app import oauth_provider, db, oauth
from openprocurement.auth.models import User, Client, current_user
from flask import request, session, redirect, jsonify, render_template
from werkzeug.security import gen_salt


@oauth_provider.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        username = request.form.get('bidder_id')
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        session['bidder_id'] = user.id
        return redirect('/')
    user = current_user()
    return render_template('home.html', user=user)

## CREATE CLIENT API ########################################################


@oauth_provider.route('/client')
def client():
    item = Client(
        client_id=gen_salt(40),
        client_secret=gen_salt(50),
        _redirect_uris=' '.join([
            'http://localhost:8000/authorized',
            'http://127.0.0.1:8000/authorized',
            'http://127.0.1:8000/authorized',
            'http://127.1:8000/authorized',
        ]),
        _default_scopes='email',
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(
        client_id=item.client_id,
        client_secret=item.client_secret,
    )

################################################################################


@oauth_provider.route('/oauth/token')
@oauth.token_handler
def access_token():
    return None


@oauth_provider.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
def authorize(*args, **kwargs):
    user = current_user()
    if not user:
        return redirect('/')
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = Client.query.filter_by(client_id=client_id).first()
        kwargs['client'] = client
        kwargs['user'] = user
        return render_template('authorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'


@oauth_provider.route('/api/allow_bid')
@oauth.require_oauth()
def allow_bid():
    user = request.oauth.user
    return jsonify(username=user.username)
