# coding: utf-8
from openprocurement.auth.provider_app import oauth_provider, db

import openprocurement.auth.models
import openprocurement.auth.views


def make_oath_provider_app(
        global_conf,
        sqlite='sqlite:///db.sqlite',
        secret='abcdfg',
        timezone='Europe/Kiev',
        hash_secret_key='',
        auction_client_id='',
        auction_client_secret=''):
    oauth_provider.config.update({
        'SQLALCHEMY_DATABASE_URI': sqlite,
    })
    oauth_provider.debug = True
    oauth_provider.secret_key = secret
    oauth_provider.hash_secret_key = hash_secret_key
    db.create_all()
    if not openprocurement.auth.models.Client.query.get(auction_client_id):
        item = openprocurement.auth.models.Client(
            client_id=auction_client_id,
            client_secret=auction_client_secret,
            _redirect_uris=' '.join([
                'http://localhost:',
                'http://cygnet.office.quintagroup.com',
                'http://auction-sandbox.openprocurement.org',
            ]),
            _default_scopes='email',
        )
        db.session.add(item)
        db.session.commit()
    return oauth_provider

if __name__ == '__main__':
    db.create_all()

    oauth_provider.config.update({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
    })
    # oauth_provider.debug = True
    # oauth_provider.use_reloader = False

    oauth_provider.run()
