#!/usr/bin/env python
import xml.etree.cElementTree as etree
from cgi import escape

import oauth
from oauth import OAuthConsumer, OAuthRequest


SIGNATURE_METHOD = oauth.OAuthSignatureMethod_HMAC_SHA1()


class InvalidOption(Exception):
    pass


class PesaPal(object):

    def __init__(self, consumer_key, consumer_secret, testing=True):

        self.oauth_consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)

        self.base_url = 'https://www.pesapal.com/api/'
        if testing:
            self.base_url = 'http://demo2.pesapal.com/api/'

    def validateOptions(self, options, default_options):
        for k, v in options.iteritems():
            if k not in default_options:
                msg = 'Option %s not found in %s' % (k, default_options.keys())
                raise InvalidOption(msg)


    def getOauthRequest(self, http_url, params, default_params):

        """ build and return oauth request """
        
        # validate options
        self.validateOptions(params, default_params)

        default_params.update(params)
        params = default_params

        http_method='GET'
        token = params.pop('token', None)

        url = self.base_url + http_url

        request = OAuthRequest.from_consumer_and_token(
            self.oauth_consumer,
            http_url= url,
            http_method=http_method,
            parameters=params
        )
        request.sign_request(SIGNATURE_METHOD, self.oauth_consumer, token)
        return request


    def postDirectOrder(self, params, request_data):
        """
        PostPesapalDirectOrderV4
        ---
        Use this to post a transaction to PesaPal. PesaPal will present the user with a page which contains the available payment options and will redirect to your site once the user has completed the payment process.
        """

        default_request_data = {
            'Amount': '',
            'Description': '',
            'Type': 'MERCHANT',
            'Reference': '',
            'Email': '',
            'PhoneNumber': '',
            # optional
            'Currency': '',
            'FirstName': '',
            'LastName': '',
            'LineItems': [
                # {
                #     'UniqueId': '',
                #     'Particulars': '',
                #     'Quantity': '',
                #     'UnitCost': '',
                #     'SubTotal': ''
                # }
            ]
        }

        # validate xml data
        self.validateOptions(request_data, default_request_data)
        default_request_data.update(request_data)
        request_data = default_request_data


        root_xml = etree.Element('PesapalDirectOrderInfo')
        root_xml.attrib['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
        root_xml.attrib['xmlns:xsd'] = 'http://www.w3.org/2001/XMLSchema'
        root_xml.attrib['xmlns'] = 'http://www.pesapal.com'

        # populate line items
        line_items = request_data.pop('LineItems')
        if len(line_items) > 0:
            line_items_xml = etree.SubElement(root_xml, 'LineItems')
            for item in line_items:
                item_xml = etree.SubElement(line_items_xml)
                item_xml.attrib.update(item)

        # populate info
        root_xml.attrib.update(request_data)

        # pesapal_request_data
        pesapal_request_data = escape(etree.tostring(root_xml))

        default_params = {
            'oauth_callback': '',
            #'oauth_consumer_key': '',
            #'oauth_nonce': '',
            #'oauth_signature': '',
            #'oauth_signature_method': '',
            #'oauth_timestamp': '',
            #'oauth_version': '1.0',
            'pesapal_request_data': pesapal_request_data
        }

        http_url = 'PostPesapalDirectOrderV4'
        
        request = self.getOauthRequest(http_url, params, default_params)
        return request

    def queryPaymentStatus(self, params):
        """
        Use this to query the status of the transaction. When a transaction is posted to PesaPal, it may be in a PENDING, COMPLETED or FAILED state. If the transaction is PENDING, the payment may complete or fail at a later stage. Both the unique order id generated by your system and the pesapal tracking id are required as input parameters.
        """
        http_url = 'QueryPaymentStatus'

        default_params = {
            'pesapal_merchant_reference': '',
            'pesapal_transaction_tracking_id': ''
        }
        
        request = self.getOauthRequest(http_url, params, default_params)
        return request
        
    def queryPaymentStatusByMerchantRef(self, params):
        """
        Same as QueryPaymentStatus, but only the unique order id genereated by your system is required as the input parameter.
        """
        
        http_url = 'QueryPaymentStatusByMerchantRef'

        default_params = {
            'pesapal_merchant_reference': ''
        }

        request = self.getOauthRequest(http_url, params, default_params)
        return request

    def queryPaymentDetails(self, params):
        """
        Same as QueryPaymentStatus, but additional information is returned.
        """

        http_url = 'QueryPaymentStatusByMerchantRef'

        default_params = {
            'pesapal_merchant_reference': '',
            'pesapal_transaction_tracking_id': ''
        }

        request = self.getOauthRequest(http_url, params, default_params)
        return request
