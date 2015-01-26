# coding: utf-8

from flask import Flask
from flask_oauthlib.provider import OAuth2Provider


oauth_provider = Flask(__name__, template_folder='templates')
oauth = OAuth2Provider(oauth_provider)
