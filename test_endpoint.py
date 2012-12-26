from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from app import create_app
from tests.schema import schema_batch, schema_single
import unittest
import validictory
import json

class EndPointTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client(create_app(test_mode=True), BaseResponse)
    
    def test_redirect_wrong_url(self):
        resp = self.client.get('/enddpoints/')

        assert resp.status == '404 NOT FOUND'
    
    def test_fetch_all_endpoints(self):
        resp = self.client.get('/endpoints/')
        output = json.loads(resp.data)
        
        assert len(output) == 2
        assert validictory.validate(output, schema_batch) == None
        
    def test_fetch_endpoints_with_limit(self):
        resp = self.client.get('/endpoints/?limit=1')
        output = json.loads(resp.data)
        
        assert len(output) == 1
        assert validictory.validate(output, schema_batch) == None

    def test_fetch_single_endpoint_with_id(self):
        resp = self.client.get('/endpoints/0')
        output = json.loads(resp.data)

        assert validictory.validate(output, schema_single) == None
    
    def test_fetch_single_endpoint_with_alias(self):
        resp = self.client.get('/endpoints/post')
        output = json.loads(resp.data)
        
        assert validictory.validate(output, schema_single) == None
    
    def test_fetch_unexisting_endpoint(self):
        resp = self.client.get('/endpoints/33')
        
        assert resp.data == '[]'
    
    
if __name__ == '__main__':
    unittest.main()