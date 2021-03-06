# import unittest
# import requests
# import sys, os
# testdir = os.path.dirname(__file__)
# srcdir = '../python/'
# sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))
# sys.argv.append('-t')
# from webapp import app
# import json, jwt, datetime

# # COMPLETO
# class TesteAlunos(unittest.TestCase):
#     def setUp(self):
#         self.app = app.test_client()
#         with self.app.session_transaction() as session:
#             session['token'] = jwt.encode({'id_geral': 4, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes = 40)}, app.config['SECRET_KEY'])

#     def tearDown(self):
#         with self.app.session_transaction() as session:
#             session.pop('token', None)

#     def test_retorna_todos_os_alunos(self):
#         response = self.app.get(
#             '/cp/aluno'
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertNotIn('"Mensagem":', str(response.data))

#     def test_1_retorna_um_aluno(self):
#         response = self.app.get(
#             '/cp/aluno/1234567'
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertNotIn('"Mensagem":', str(response.data))

#     def test_2_deleta_um_aluno(self):
#         response = self.app.delete(
#             '/cp/aluno/1234567'
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('sucesso', str(response.data))

# if __name__ == '__main__':
#     unittest.main()