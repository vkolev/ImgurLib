# -*- coding: utf-8 -*-
# vim:noet:sw=4:ts=4:ft=vim

'''
File:  imgurlib.py
Author:  Vladimir Kolev
Version: 1.1a
Description: Python library to communicate with Imgur.com
'''

import json
import urlparse
import urllib
import oauth2 as oauth


REQUEST_TOKEN_URL = 'https://api.imgur.com/oauth/request_token'
AUTHORIZE_URL = 'http://api.imgur.com/oauth/authorize'
ACCESS_TOKEN_URL = 'https://api.imgur.com/oauth/access_token'


class ImgurLib:
    """
    Python library to communicate with the Authenticated Imgur.com API.

    For more information and undestanding the api, please visit the
    official website at http://api.imgur.com
    """

    def __init__(self, key, secret):
        """Initialize the library

        Initialisation of the library with a consumer key and consumer
        secret.

        Attributes:
            key -- The consumer_key for your application
            secret -- the consumer_secret for you application
        """
        self.consumer = oauth.Consumer(key, secret)
        self.client = oauth.Client(self.consumer)
        self.oauth_token = ""
        self.oauth_token_secret = ""
        self.token = ""
        self.token_u = ""

    def authorize(self, pin):
        """Authorizes the client with a ping

        Verification of the tokens with a pin so we get the final
        token. The pin you get opening the url returned by the
        get_auth_url() method.

        Attributes:
            pin -- The pin string from the get_auth_url()
        """
        self.token_u.set_verifier(pin)
        client = oauth.Client(self.consumer, self.token_u)
        resp, content = client.request(ACCESS_TOKEN_URL, "POST")
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
        """Authorize the client with user tokens

        If you have already a token for the user you can use this method to
        authorize the client skipping the get_auth_url() method. If the
        authentication is successful a bool True is returned.

        Attributes:
            token -- The oauth_token you have saved somewhere
            token_secret -- The oauth_token_secret for the bove token
        """
        self.oauth_token = token
        self.oauth_token_secret = token_secret
        self.token = oauth.Token(self.oauth_token, self.oauth_token_secret)
        self.client = oauth.Client(self.consumer, self.token)
        try:
            self.account_info()
            return True
        except UserAuthenticationException:
            return False

    def get_auth_url(self):
        """Generate Authorization URL

        Generates an url, so the user can open it in orther to enable
        access to get access to the user account. A Pin code is given in
        that page, that should be used in the authorize() method.
        """
        resp, content = self.client.request(REQUEST_TOKEN_URL, "POST")
        result = dict(urlparse.parse_qsl(content))
        oauth_token = result['oauth_token']
        oauth_token_secret = result['oauth_token_secret']
        self.token_u = oauth.Token(oauth_token, oauth_token_secret)
        url = AUTHORIZE_URL + "?oauth_token=%s" % oauth_token
        if resp['status'] != '200':
            return None
        return url

    def account_info(self):
        """Gets the account information

        Lists all the account information available through the API.
        """
        url = "http://api.imgur.com/2/account.json"
        method = 'GET'
        return self._submit_request(url, method)

    def upload_image(self, filename, title="", caption=""):
        """Uploads an image

        Uploads an image to imgur.com with given title and caption. Where
        the filename can be either a fullpath to a local image or url to
        existing image from internet.

        Attributes:
            filename -- Filepath or URL to an image
            title -- The title of the image to be saved
            caption -- a caption of the image
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
        return self._submit_request(url, method, params)

    def get_account_images(self):
        """List all images in account

        Gets a list with all images in current account and all the
        information about every image.
        """
        url = "http://api.imgur.com/2/account/images.json"
        method = 'GET'
        return self._submit_request(url, method)

    def delete_image(self, imagehash):
        """Delete an image from account

        Deletes a single image from imgur.com account based on the imagehash.

        Attributes:
            imagehash -- The Image hash string
        """
        url = "http://api.imgur.com/2/account/images/%s.json" % imagehash
        method = 'DELETE'
        return self._submit_request(url, method)

    def get_image_info(self, imagehash):
        """Information about an image

        Get the full information about an image from account. This includes
        the image title, caption and some links to use.

        Attributes:
            imagehash -- The Image hash string
        """
        url = "http://api.imgur.com/2/account/images/%s.json" % imagehash
        method = 'GET'
        return self._submit_request(url, method)

    def get_image_count(self):
        """Counts all the images in account

        Returns the total number of images that are in an account. This can
        be used when using paginations for getting all images from an account
        without albums.
        """
        url = "http://api.imgur.com/2/account/images_count.json"
        method = 'GET'
        return self._submit_request(url, method)

    def get_albums(self, count=30, page=1):
        """Gets the albums in an account

        Lists the albums in account with pagination. That allows to have
        smaller requests. For samller albums count the parameteres cound
        and page can be left empty. But if the user has many albums, you
        can consider using with the the get_album_count() function to get
        the count of all the albums the user has, so you can generate
        the pages and the requests.

        Attribues:
            count -- How many albums should the method get
            page -- From witch page to get the results
        """
        url = "http://api.imgur.com/2/account/albums.json"
        method = 'GET'
        params = urllib.urlencode({
            'count': count,
            'page': page,
        })
        return self._submit_request(url, method, params)

    def create_album(self, title="", description="", privacy="public"):
        """Creates an album

        With this method you can create an album in an imgur account.
        Provifing the information title, description and privacy. The
        title and the description are freely to choose string, but the
        pribacy attribute must be public/hidden/secret. Returns the
        information about the new album created.

        Attributes:
            title -- The Album title
            description -- The album description
            privacy -- How can see your album (public, hidden, secret)
        """
        url = "http://api.imgur.com/2/account/albums.json"
        method = 'POST'
        params = urllib.urlencode({
            'title': title,
            'description': description,
            'privacy': privacy,
        })
        return self._submit_request(url, method, params)

    def get_album_count(self):
        """Returns the number of albums

        Gets the count of the albums for account you are authenticated for.
        The result can be used to use pagination in your request from the
        get_albums() function
        """
        url = "http://api.imgur.com/2/account/albums_count.json"
        method = 'GET'
        return self._submit_request(url, method)

    def get_credits(self):
        """Get the credits information

        Every account at imgur.com using the API has so called credits
        This is the limit of actions used through the API. With this
        method you get the information how much credits you have left.
        """
        url = "http://api.imgur.com/2/credits.json"
        method = 'GET'
        return self._submit_request(url, method)

    def generate_links(self, imagehash):
        """Generate tags for forums and html pages

        Generates special links for Forums/HTML etc. and returns them
        as a dictionary.

        Attributes:
            imagehash -- string containing the imagehash
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
            links['html'] = htmlpath % (link, thumb)
            return links
        else:
            return None

    def _submit_request(self, url, method, params=""):
        """
        Submits a request to the client with given
        URL, method and parameters
        on success returns result
        """
        exceptions = {
            '400': ParameterMissingException,
            '401': UserAuthenticationException,
            '403': ForbiddenException,
            '404': NotSupportedActionException,
            '505': InternalErrorException,
        }
        resp, result = self.client.request(url, method, params)
        if resp['status'] in exceptions:
            raise exceptions[resp['status']]
        return result


class Error(Exception):
    """Base class for exceptions in ImgurLib"""
    pass


class ParameterMissingException(Error):
    """
    Exception rised when parameter is missing.
    """

    def __init__(self):
        self.msg = "Missing parameter or parameter value out of bounds"


class UserAuthenticationException(Error):
    """
    Exception rised when user is not authenticated.
    """

    def __init__(self):
        self.msg = "User is not authenticated"


class ForbiddenException(Error):
    """
    Exception rised when you don't have permission tothis action.
    """

    def __init__(self):
        self.msg = "Don't have access to this action"


class NotSupportedActionException(Error):
    """
    Exception rised when the action is not supported.
    """

    def __init__(self):
        self.msg = "Action not supported"


class InternalErrorException(Error):
    """
    Exception rised when internal Error accured
    """

    def __init__(self):
        self.msg = "Internal server Error"
