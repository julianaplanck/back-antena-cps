import unittest
import requests
import sys, os
testdir = os.path.dirname(__file__)
srcdir = '../python/'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))
sys.argv.append('-t')
from webapp import app
import json, jwt, datetime

# COMPLETO
class TesteAdm(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        with self.app.session_transaction() as session:
            session['token'] = jwt.encode({'id_geral': 1, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes = 40)}, app.config['SECRET_KEY'])

    def tearDown(self):
        with self.app.session_transaction() as session:
            session.pop('token', None)


    def test_cadastra_um_adm(self):
        response = self.app.post(
            '/cp/adm', 
            data = json.dumps({
                "id": "2"
            }),
            follow_redirects = True, 
            content_type = "application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('cadastrado', str(response.data))

    def test_exclui_um_adm(self):
        response = self.app.delete(
            '/cp/adm', 
            data = json.dumps({
                "id": "2"
            }),
            follow_redirects = True, 
            content_type = "application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('deletado', str(response.data))

if __name__ == '__main__':
    unittest.main()