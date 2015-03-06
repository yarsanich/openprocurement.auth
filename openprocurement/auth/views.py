from openprocurement.auth.provider_app import oauth_provider, oauth
from openprocurement.auth.models import Client, current_user
from flask import request, redirect, jsonify, render_template


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
    if request.method == 'GET' and 'auto_allow' not in request.args:
        kwargs['client'] = Client.get_from_db(client_id=kwargs.get('client_id', ''))
        kwargs['user'] = user
        kwargs['redirect_uri'] = request.args['redirect_uri']
        return render_template('authorize.html', **kwargs)
    elif 'auto_allow' in request.args:
        return True

    if 'confirm' in request.form:
        return True

    return False


@oauth_provider.route('/api/me')
@oauth.require_oauth()
def allow_bid():
    return jsonify(
        bidder_id=request.oauth.user,
        expires=request.oauth.access_token._expires
    )
