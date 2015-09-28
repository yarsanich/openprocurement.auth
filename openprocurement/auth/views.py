from openprocurement.auth.provider_app import oauth_provider, oauth
from openprocurement.auth.models import current_user
from flask import request, redirect, jsonify, render_template, make_response


@oauth_provider.route('/oauth/token', methods=['GET', 'POST'])
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
        kwargs['client'] = oauth_provider.auction_client
        kwargs['user'] = user
        kwargs['redirect_uri'] = request.args['redirect_uri']
        response = make_response(render_template('authorize.html', **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
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
