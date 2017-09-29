from datetime import datetime, timedelta
from .provider_app import oauth, oauth_provider
from flask import request, abort
from flask import current_app
from hashlib import sha1
import re
from retrying import retry
from base64 import b64decode
from libnacl.sign import Signer, Verifier
from urllib import unquote

GRANT_EXPIRES = 86400

def get_database(master=True):
    if hasattr(oauth_provider, 'sentinal'):
        if master:
            return oauth_provider.sentinal.master_for(oauth_provider.sentinel_cluster_name)
        else:
            return oauth_provider.sentinal.slave_for(oauth_provider.sentinel_cluster_name)
    else:
        return oauth_provider.db


class MetaModel(object):
    format_key_string = "{0['id']}"

    def __init__(self, **entries):
        self.__dict__.update(entries)

    @classmethod
    @retry(stop_max_attempt_number=3)
    def format_key(cls, kw):
        return cls.__name__.lower() + cls.format_key_string.format(kw)

    @classmethod
    @retry(stop_max_attempt_number=3)
    def set_expire(cls, model, timeout=GRANT_EXPIRES):
        db = get_database()
        db.expire(cls.format_key(model.__dict__), timeout)

    @classmethod
    @retry(stop_max_attempt_number=3)
    def get_from_db(cls, **kw):
        db = get_database()
        document = db.hgetall(cls.format_key(kw))
        if document:
            client = cls(**document)
            client.__dict__.update(kw)
            return client

    @classmethod
    @retry(stop_max_attempt_number=3)
    def save_to_db(cls, model):
        db = get_database()
        return db.hmset(
            cls.format_key(model.__dict__),
            model.__dict__
        )


class User(MetaModel):
    format_key_string = "_{0[bidder_id]}"


class Client(MetaModel):
    format_key_string = "_{0[client_id]}"

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    def validate_redirect_uri(self, redirect_uri):
        return any([True for url in self.redirect_uris if re.match(url, redirect_uri)])

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []


class Grant(MetaModel):
    format_key_string = "_{0[client_id]}_{0[code]}"

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

    @property
    def expires(self):
        return datetime.strptime(self._expires, "%Y-%m-%dT%H:%M:%S.%f")

    def delete(self):
        db = get_database()
        return db.delete(self.format_key(self.__dict__))

    def validate_redirect_uri(self, redirect_uri):
        return True


class Token(MetaModel):
    format_key_string = "_{0[access_token]}"

    @property
    def expires(self):
        return datetime.strptime(self._expires, "%Y-%m-%dT%H:%M:%S.%f")

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


def current_user():
    if 'bidder_id' in request.args and 'hash' in request.args:
        digest = sha1(current_app.hash_secret_key)
        digest.update(request.args['bidder_id'])
        if digest.hexdigest() == request.args['hash']:
            bidder_id = request.args['bidder_id']
            user = User.get_from_db(bidder_id=bidder_id)
            if not user:
                user = User(**{'bidder_id': bidder_id})
                User.save_to_db(user)
                User.set_expire(user)
            return user
    elif 'bidder_id' in request.form:
        user = User.get_from_db(bidder_id=request.form['bidder_id'])
        if user:
            return user
    return abort(405)



def current_user_sig():
    if 'bidder_id' in request.args and 'signature' in request.args:
        signature = b64decode(unquote(request.args['signature']))
        bidder_id = request.args['bidder_id']
        signer = Signer(current_app.signature_key.decode('hex'))
        verifier = Verifier(signer.hex_vk())
        if verifier.verify(signature+str(bidder_id)):
            user = User(**{'bidder_id': bidder_id})
            User.save_to_db(user)
            User.set_expire(user)
            return user
    elif 'bidder_id' in request.form:
        user = User.get_from_db(bidder_id=request.form['bidder_id'])
        if user:
            return user
    return abort(405)


@oauth.clientgetter
def load_client(client_id):
    if oauth_provider.auction_client.client_id == client_id:
        return oauth_provider.auction_client


@oauth.grantgetter
def load_grant(client_id, code):
    return Grant.get_from_db(client_id=client_id, code=code)


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    expires = datetime.utcnow() + timedelta(seconds=GRANT_EXPIRES)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=current_user().bidder_id,
        _expires=expires.isoformat()
    )

    Grant.save_to_db(grant)
    Grant.set_expire(grant, GRANT_EXPIRES)
    return grant


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return Token.get_from_db(access_token=access_token)


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    expires = datetime.utcnow() + timedelta(seconds=GRANT_EXPIRES)
    tok = Token(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        _expires=expires.isoformat(),
        client_id=request.client.client_id,
        user=request.user
    )

    Token.save_to_db(tok)
    Token.set_expire(tok, GRANT_EXPIRES)
    return tok
