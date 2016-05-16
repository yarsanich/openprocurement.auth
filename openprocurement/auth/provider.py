# coding: utf-8
from openprocurement.auth.provider_app import oauth_provider
from json import loads
from redis import Redis
from redis.sentinel import Sentinel

import openprocurement.auth.models
import openprocurement.auth.views


def make_oath_provider_app(
        global_conf,
        redis='redis://localhost:9002/1',
        redis_password='',
        redis_database='',
        sentinel_cluster_name='',
        sentinels='',
        secret='abcdfg',
        timezone='Europe/Kiev',
        hash_secret_key='',
        auction_client_id='',
        auction_client_secret=''):

    oauth_provider.debug = True
    if sentinels:
        oauth_provider.sentinel_cluster_name = sentinel_cluster_name
        oauth_provider.sentinal = Sentinel(loads(sentinels), socket_timeout=0.1, password=redis_password, db=redis_database)
    else:
        oauth_provider.db = Redis.from_url(redis)
    oauth_provider.secret_key = secret
    oauth_provider.hash_secret_key = hash_secret_key
    oauth_provider.config['OAUTH2_PROVIDER_TOKEN_EXPIRES_IN'] = openprocurement.auth.models.GRANT_EXPIRES

    oauth_provider.auction_client = openprocurement.auth.models.Client(
        client_id=auction_client_id,
        client_secret=auction_client_secret,
        _redirect_uris=' '.join(
            ['http:\/\/localhost:.*',
             '(http|https):\/\/[\w\-_]+\.office\.quintagroup\.com.*',
             '(http|https):\/\/[.\w\-_]+\.openprocurement\.org\.*']
        ),
        _default_scopes='email'
    )

    return oauth_provider
