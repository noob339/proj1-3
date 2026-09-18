"""Set TEST_DATABASE_URL to a freshly seeded, disposable database to run."""
import os
import secrets
import unittest
from unittest.mock import patch
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

if not os.environ.get('TEST_DATABASE_URL'):
    raise RuntimeError('Set TEST_DATABASE_URL to a disposable seeded database')
os.environ['DATABASE_URL'] = os.environ['TEST_DATABASE_URL']
from webserver.server import app, engine, add_person, get_associated_person_id


class DatabaseIntegration(unittest.TestCase):
    def test_application_workflows(self):
        # Bind all route connections to one outer transaction, so committed
        # requests are visible to subsequent requests but leave no test records.
        import webserver.server as server
        connection = engine.connect()
        transaction = connection.begin()
        class RequestConnection:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def close(self):
                pass
            def begin(self):
                return connection.begin_nested()
            def commit(self):
                pass
            def __getattr__(self, name):
                return getattr(connection, name)
        class TestEngine:
            def connect(self):
                return RequestConnection()
        original = server.engine
        server.engine = TestEngine()
        app.config.update(TESTING=True)
        try:
            client = app.test_client()
            self.assertNotIn(b'<svg', client.get('/family_tree').data)
            fixture = connection.execute(text('SELECT username FROM users WHERE userid=8')).scalar_one()
            client.post('/login', data={'username': fixture, 'password': 'anything'})
            with client.session_transaction() as session:
                self.assertNotIn('UserID', session)
            name = 'integration_' + secrets.token_hex(6)
            password = secrets.token_urlsafe(20)
            response = client.post('/register', data=dict(username=name, email=name+'@example.com',
                password=password, first_name='Integration', last_name='Test'))
            self.assertEqual(response.status_code, 302)
            user_id, hashed = connection.execute(text('SELECT userid, password FROM users WHERE username=:name'), {'name':name}).one()
            self.assertNotEqual(password, hashed)
            self.assertTrue(check_password_hash(hashed, password))
            person_id = get_associated_person_id(user_id, connection)
            self.assertEqual(connection.execute(text('SELECT count(*) FROM lineagepersonconnector WHERE personid=:p'), {'p':person_id}).scalar_one(), 1)
            self.assertIsNone(get_associated_person_id(-1, connection))
            client.post('/login', data={'username':name, 'password':'incorrect'})
            with client.session_transaction() as session:
                self.assertNotIn('UserID', session)
            self.assertEqual(client.post('/login', data={'username':name,'password':password}).status_code, 302)
            for path in ['/family_tree', '/person/6', '/user_tags']:
                self.assertEqual(client.get(path).status_code, 200)
            self.assertIn(b'<svg', client.get('/family_tree').data)
            self.assertEqual(client.get('/person/999999').status_code,404)
            # Shared archive behavior remains: a registered user can add to Bruce.
            response = client.post('/person/6', data=dict(form_type='add_person',first_name='New',last_name='Relative',lineage_id=5,relationship_type_id=7))
            self.assertEqual(response.status_code,302)
            new_id=int(response.location.rsplit('/',1)[1])
            self.assertEqual(connection.execute(text('SELECT lineageid FROM lineagepersonconnector WHERE personid=:p'),{'p':new_id}).scalars().all(),[5])
            self.assertEqual(connection.execute(text('SELECT count(*) FROM lineages WHERE lineagename=\'Relative\'')).scalar_one(),0)
            self.assertEqual(connection.execute(text('SELECT directrelationshiptypeid FROM relations WHERE personid=6 AND directrelationship=:p'),{'p':new_id}).scalar_one(),7)
            self.assertEqual(connection.execute(text('SELECT count(*) FROM relations WHERE personid=:p'),{'p':new_id}).scalar_one(),0)
            before=connection.execute(text('SELECT count(*) FROM person')).scalar_one()
            with self.assertRaises(IntegrityError):
                add_person(RequestConnection(),'Rollback','Test',user_id,6,-1,7)
            self.assertEqual(connection.execute(text('SELECT count(*) FROM person')).scalar_one(),before)
            response=client.post('/person/6', data=dict(form_type='add_document',doc_desc="Bound ' document",doc_link='https://example.com/test',doc_date='',tags='New tag, New tag'))
            self.assertEqual(response.status_code,302)
            self.assertIn(b'Bound &#39; document',client.get('/person/6').data)
            doc_id=connection.execute(text('SELECT documentid FROM documents WHERE documentdesc=:d'),{'d':"Bound ' document"}).scalar_one()
            self.assertEqual(connection.execute(text('SELECT count(*) FROM documenttagmapping WHERE documentid=:d'),{'d':doc_id}).scalar_one(),1)
            # View Wayne family tags through the route without enabling a fixture
            # login. Overlapping memberships must not duplicate its documents.
            with client.session_transaction() as session:
                session['UserID'] = 8
            with patch.object(server, 'render_template', return_value='rendered') as render:
                self.assertEqual(client.get('/user_tags').status_code, 200)
                baseline = {row['tag_desc']: row['no_tags'] for row in render.call_args.kwargs['tags']}
                self.assertEqual(baseline['medical document'], 2)
                connection.execute(text('INSERT INTO lineagepersonconnector VALUES (6, 10), (11, 5)'))
                client.get('/user_tags')
                overlapping = {row['tag_desc']: row['no_tags'] for row in render.call_args.kwargs['tags']}
                self.assertEqual(overlapping['medical document'], 2)
                self.assertEqual(overlapping['legal document'], 4)
                client.post('/user_tags', data={'filter_by_user': 'on'})
                authored = {row['tag_desc']: row['no_tags'] for row in render.call_args.kwargs['tags']}
                self.assertEqual(authored, {'government issued': 1, 'legal document': 1, 'medical document': 1})
            client.get('/logout')
            with client.session_transaction() as session:
                self.assertNotIn('UserID',session)
        finally:
            server.engine=original
            transaction.rollback()
            connection.close()

if __name__ == '__main__':
    unittest.main()
