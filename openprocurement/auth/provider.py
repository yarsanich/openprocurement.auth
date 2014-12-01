# coding: utf-8
from openprocurement.auth.provider_app import oauth_provider, db

import openprocurement.auth.models
import openprocurement.auth.views


def make_oath_provider_app(
        global_conf,
        sqlite='sqlite:///db.sqlite',
        secret='abcdfg',
        timezone='Europe/Kiev'):
    oauth_provider.config.update({
        'SQLALCHEMY_DATABASE_URI': sqlite,
    })
    oauth_provider.secret_key = secret
    db.create_all()
    return oauth_provider

if __name__ == '__main__':
    db.create_all()

    oauth_provider.config.update({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
    })
    # oauth_provider.debug = True
    # oauth_provider.use_reloader = False

    oauth_provider.run()
