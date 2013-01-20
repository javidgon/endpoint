from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from endpoint.run_server import application
from endpoint.tests.schema import (schema_batch, schema_single,
                                   schema_error)
import unittest
import validictory
import json

class SentinelTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client(application(), BaseResponse)
    
    def test_redirect_wrong_url(self):
        """
        Check if the app serves a proper error status
        if we request an invalid url
        """
        resp = self.client.get('tests/example/')

        assert resp.status == '404 NOT FOUND'
    
    def test_fetch_all_endpoints(self):
        """
        Check if we are able to retrieve all the endpoints. 
        """
        resp = self.client.get('/tests/')
        output = json.loads(resp.data)
        
        assert len(output) == 11
        assert validictory.validate(output, schema_batch) == None
        
    def test_fetch_endpoints_with_limit(self):
        """
        Check if we can retrieve endpoints based on a
        limit number
        """
        resp = self.client.get('tests/?limit=1')
        output = json.loads(resp.data)

        assert output[0]['tests_passed'] == True
        assert validictory.validate(output, schema_batch) == None

    def test_fetch_single_endpoint_with_id(self):
        """
        Check if we can retrieve endpoints based on
        their ids
        """
        resp = self.client.get('tests/1')
        output = json.loads(resp.data)

        assert output['tests_passed'] == True
        assert validictory.validate(output, schema_single) == None
    
    def test_fetch_single_endpoint_with_alias(self):
        """
        Check if we can retrieve endpoints based on
        their aliases
        """
        resp = self.client.get('tests/get')
        output = json.loads(resp.data)
        
        assert output['tests_passed'] == True
        assert validictory.validate(output, schema_single) == None
        
    def test_fetch_single_endpoint_with_basic_auth(self):
        """
        Check if we can successfully make requests over a
        endpoint under basic auth
        """
        resp = self.client.get('tests/post_basic')
        output = json.loads(resp.data)
        
        assert output['tests_passed'] == True
        assert validictory.validate(output, schema_single) == None
        
    def test_fetch_single_endpoint_with_digest_auth(self):
        """
        Check if we can successfully make requests over a
        endpoint under digest auth
        """
        resp = self.client.get('tests/post_digest')
        output = json.loads(resp.data)
        
        assert output['tests_passed'] == True
        assert validictory.validate(output, schema_single) == None
        
    def test_fetch_single_endpoint_with_basic_auth_and_wrong_credentials(self):
        """
        Try to reproduce the case when we provide wrong
        credentials to a basic auth
        """
        resp = self.client.get('tests/post_basic_unauthorized')
        output = json.loads(resp.data)
        
        assert output['tests_passed'] == True
        assert validictory.validate(output, schema_single) == None
        
    def test_fetch_single_endpoint_with_digest_auth_and_wrong_credentials(self):
        """
        Try to reproduce the case when we provide wrong
        credentials to a digest auth
        """
        resp = self.client.get('tests/post_digest_unauthorized')
        output = json.loads(resp.data)
        
        assert output['tests_passed'] == True
        assert validictory.validate(output, schema_single) == None
    
    def test_fetch_unexisting_endpoint(self):
        """
        Check what we'd get if we tried to access to an
        unexisting endpoint from the .yaml file
        """
        resp = self.client.get('tests/33')
        
        assert resp.data == '{}'
        
    def test_fetch_invalid_endpoint(self):
        """
        Check what we'd get if we tried to access to an
        invalid endpoint from the .yaml file
        """
        resp = self.client.get('tests/invalid_url')
        output = json.loads(resp.data)
        
        assert output['log'] == 'BAD_REQUEST'
        assert output['tests_passed'] == True
        assert validictory.validate(output, schema_error) == None
        
    def test_fetch_endpoint_from_inactive_server(self):
        """
        Check what we'd get if we tried to access to an
        inactive server
        """
        resp = self.client.get('tests/inactive_server')
        output = json.loads(resp.data)
        
        assert output['log'] == 'SERVER_UNREACHABLE'
        assert output['tests_passed'] == True
        assert validictory.validate(output, schema_error) == None
        
    def test_fetch_endpoint_with_high_speed_requirements(self):
        """
        Check what we'd get if we tried to get a response
        within a utopic timing range
        """
        resp = self.client.get('tests/request_timeout')
        output = json.loads(resp.data)
        
        assert output['log'] == 'REQUEST_TIMEOUT'
        assert output['tests_passed'] == True
        assert validictory.validate(output, schema_error) == None
        
    def test_fetch_endpoint_with_an_unimplemented_method(self):
        """
        Check what we'd get if we tried to get a response
        using a unimplemented method
        """
        resp = self.client.get('tests/not_implemented')
        output = json.loads(resp.data)
        
        assert output['log'] == 'NOT_IMPLEMENTED'
        assert output['tests_passed'] == True
        assert validictory.validate(output, schema_error) == None
