from openprocurement.auth.provider_app import oauth_provider, oauth
from openprocurement.auth.models import User, Client, current_user
from flask import request, session, redirect, jsonify, render_template
from werkzeug.security import gen_salt


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
        kwargs['client'] = Client.get_from_db(client_id=kwargs.get('client_id', ''))
        kwargs['user'] = user
        kwargs['redirect_uri'] = request.args['redirect_uri']
        return render_template('authorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'


@oauth_provider.route('/api/me')
@oauth.require_oauth()
def allow_bid():
    user = request.oauth.user
    return jsonify(bidder_id=user)
