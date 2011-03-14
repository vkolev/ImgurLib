#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:noet:sw=4:ts=4:ft=vim

import json
import urlparse
import urllib
import base64
import oauth2 as oauth

'''
File:  imgurlib.py
Author:  Vladimir Kolev
Description: Python library to communicate with Imgur.com
'''

__author__ = "Vladimir Kolev"
__version__ = "1.0a"
__doc__ = "Python library to communicate with the Auth. API of Imgur.com"

REQUEST_TOKEN_URL = 'https://api.imgur.com/oauth/request_token'
AUTHORIZE_URL = 'http://api.imgur.com/oauth/authorize'
ACCESS_TOKEN_URL = 'https://api.imgur.com/oauth/access_token'


class ImgurLib:
    """
    Python library to communicate with the Authenticated Imgur.com API.

    For more information and undestanding the api, please visit the
    official website of Imgur U{http://api.imgur.com/}.

    @author: Vladimir Kolev <vladimir.r.kolev@gmail.com>
    @license: MIT License
    @version: 1.0a
    """

    def __init__(self, key, secret):
        """
        Initialisation of the library with a consumer key and consumer
        secret.
        @type key: string
        @param key: The consumer key
        @type secret: string
        @param secret: The consumer secret
        """
        self.consumer = oauth.Consumer(key, secret)
        self.client = oauth.Client(self.consumer)
        self.oauth_token = ""
        self.oauth_token_secret = ""
        self.token = ""
        self.token_u = ""

    def authorize(self, pin):
        """
        Verification of the tokens with a pin
        @type pin: string
        @param pin: The PIN to authenticate the client
        @rtype: bool
        @return: B{True} if the authentication was successful
        """
        self.token_u.set_verifier(pin)
        client = oauth.Client(self.consumer, self.token_u)
        resp, content = client.request(ACCESS_TOKEN_URL, "POST")
        resp['status']
        result = dict(urlparse.parse_qsl(content))
        self.oauth_token = result['oauth_token']
        self.oauth_token_secret = result['oauth_token_secret']
        self.token = oauth.Token(self.oauth_token, self.oauth_token_secret)
        self.client = oauth.Client(self.consumer, self.token)
        if resp['status'] == '200':
            return True
        else:
            return False

    def authorize_with_token(self, token="", token_secret=""):
        """
        If you have already a token for the user you can use this method
        @type token: string
        @param token: the oauth_token of the user
        @type token_secret: string
        @param token_secret: the oauth_token_secret of the user
        @rtype: bool
        @return: True if the authentication was successful
        """
        self.oauth_token = token
        self.oauth_token_secret = token_secret
        self.token = oauth.Token(self.oauth_token, self.oauth_token_secret)
        self.client = oauth.Client(self.consumer, self.token)
        if(self.account_info() != None):
            return True
        else:
            return False

    def get_auth_url(self):
        """
        Generates an url, so the user can open it and enable the access
        to the API.
        @rtype: dict
        @return: a dictionary with key I{success} with a bool value and
        a I{result} with the response
        """
        resp, content = self.client.request(REQUEST_TOKEN_URL, "POST")
        result = dict(urlparse.parse_qsl(content))
        oauth_token = result['oauth_token']
        oauth_token_secret = result['oauth_token_secret']
        self.token_u = oauth.Token(oauth_token, oauth_token_secret)
        url = AUTHORIZE_URL + "?oauth_token=%s" % oauth_token
        if resp['status'] == '200':
            return {'success': True, 'result': url}
        else:
            return {'success': False, 'result': None}

    def account_info(self):
        """
        Lists all the account information.
        @rtype: dict
        @return: a dictionary with key I{success} with a bool value and
        a I{result} with the response
        """
        url = "http://api.imgur.com/2/account.json"
        method = 'GET'
        resp, result = self.client.request(url, method)
        if resp['status'] == '200':
            return {'success': True, 'result': result}
        else:
            return {'success': False, 'result': None}

    def upload_image(self, filename, title="", caption=""):
        """
        Uploads an image to imgur.com.
        @type filename : string
        @param filename: The full path or URL to imagefile to upload.
        @type title: string
        @param title: I{optional} the title of the image.
        @type caption: string
        @param caption: I{optional} the caption of the image.
        @rtype: dict
        @return: a dictionary with key I{success} with a bool value and
        a I{result} with the response
        """
        url = "http://api.imgur.com/2/account/images.json"
        method = 'POST'
        if 'http://' in filename:
            typeup = 'url'
            imagedata = filename
        else:
            typeup = 'base64'
            imagedata = open(filename).read().encode('base64')

        params = urllib.urlencode({
            'image': imagedata,
            'type': typeup,
            'title': title,
            'caption': caption,
        })
        resp, result = self.client.request(url, method, params)
        if resp['status'] == '200':
            return {'success': True, 'result': result}
        else:
            return {'success': False, 'result': result}

    def get_account_images(self):
        """
        Gets a list with images in current account.
        @rtype: dict
        @return: a dictionary with key I{success} with a bool value and
        a I{result} with the response
        """
        url = "http://api.imgur.com/2/account/images.json"
        method = 'GET'
        resp, result = self.client.request(url, method)
        if resp['status'] == '200':
            return {'success': True, 'result': result}
        else:
            return {'success': False, 'result': result}

    def delete_image(self, imagehash):
        """
        Deletes an image from imgur.com account.
        @type imagehash: string
        @param imagehash: the hash of the image to be deleted.
        @rtype: dict
        @return: a dictionary with key I{success} with a bool value and
        a I{result} with the response
        """
        url = "http://api.imgur.com/2/account/images/%s.json" % imagehash
        method = 'DELETE'
        resp, result = self.client.request(url, method)
        if resp['status'] == '200':
            return {'success': True, 'result': result}
        else:
            return {'success': False, 'result': result}

    def get_image_info(self, imagehash):
        """
        Information about an image from account.
        @type imagehash: string
        @param imagehash: the hash of the image to get the information for.
        @rtype: dict
        @return: a dictionary with key I{success} with a bool value and
        a I{result} with the response
        """
        url = "http://api.imgur.com/2/account/images/%s.json" % imagehash
        method = 'GET'
        resp, result = self.client.request(url, method)
        if resp['status'] == '200':
            return {'success': True, 'result': result}
        else:
            return {'success': False, 'result': result}

    def get_image_count(self):
        """
        Returns the total number of images that are in an account. This can
        be used when using paginations
        @rtype: dict
        @return: a dictionary with key I{success} with a bool value and
        a I{result} with the response
        """
        url = "http://api.imgur.com/2/account/images_count.json"
        method = 'GET'
        resp, result = self.client.request(url, method)
        if resp['status'] == '200':
            return {'success': True, 'result': result}
        else:
            return {'success': False, 'result': result}

    def get_albums(self, count=30, page=1):
        """
        Lists the albums in account.
        @type count: number
        @param count: How many albums to return.
        @type page: number
        @param count: What page from the results to return.
        @rtype: dict
        @return: a dictionary with key I{success} with a bool value and
        a I{result} with the response
        """
        url = "http://api.imgur.com/2/account/albums.json"
        method = 'GET'
        params = urllib.urlencode({
            'count': count,
            'page': page,
        })
        resp, lists = self.client.request(url, method, params)
        if resp['status'] == '200':
            return {'success': True, 'result': lists}
        else:
            return {'success': False, 'result': lists}

    def create_album(self, title="", description="", privacy="public"):
        """
        Creates an album in imgur.com account
        @type title: string
        @param title: The title of the album
        @type description: string
        @param description: The description of the album
        @type privacy: string
        @param privacy: Album privacy setting can be C{public, hidden, secret}
        @rtype: dict
        @return: a dictionary with key I{success} with a bool value and
        a I{result} with the response
        """
        url = "http://api.imgur.com/2/account/albums.json"
        method = 'POST'
        params = urllib.urlencode({
            'title': title,
            'description': description,
            'privacy': privacy,
        })
        resp, result = self.client.request(url, method, params)
        if resp['status'] == '200':
            return {'success': True, 'result': result}
        else:
            return {'success': False, 'result': result}

    def get_album_count(self):
        """
        Gets the count of the albums for account
        @rtype: dict
        @return: a dictionary with key I{success} with a bool value and
        a I{result} with the response
        """
        url = "http://api.imgur.com/2/account/albums_count.json"
        method = 'GET'
        resp, count = self.client.request(url, method)
        if resp['status'] == '200':
            return {'success': True, 'result': count}
        else:
            return {'success': False, 'result': count}

    def get_credits(self):
        """
        Gets the credits information for the current account
        @rtype: dict
        @return: a dictionary with key I{success} with a bool value and
        a I{result} with the response
        """
        url = "http://api.imgur.com/2/credits.json"
        method = 'GET'
        resp, credits = self.client.request(url, method)
        if resp['status'] == '200':
            return {'success': True, 'result': credits}
        else:
            return {'success': False, 'result': credits}

    def generate_links(self, imagehash):
        """
        Generates special links for Forums/HTML etc.
        @type imagehash: string
        @param imagehash: The hash of the image to generate the links for.
        @rtype: dict
        @return: dictionary with keys I{forums} and I{html}.
        """
        formpath = '[url=%s][img]%s[/img][/url]'
        htmlpath = '<a href="%s" target="_blank"><img src="%s" /></a>'
        links = {}
        response = self.get_image_info(imagehash)
        if response['success'] == True:
            data = json.loads(response['result'])
            thumb = data['images']['links']['small_square']
            link = data['images']['links']['original']
            links['forums'] = formpath % (link, thumb)
            links['html'] =  htmlpath % (link, thumb)
            return links
        else:
            return None
