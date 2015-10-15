from __future__ import print_function
import sponge
import json
import uuid
from flask.ext.testing import TestCase
from sponge.orm import db


class SpongeTest(TestCase):
    """
    Base test class
    """

    def create_app(self):
        app = sponge.app
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        app.config['TRAP_HTTP_EXCEPTIONS'] = True

        return sponge.app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class ContractTest(SpongeTest):
    """
    Test the api views
    """

    def test_ping(self):
        """
        Start with something simple
        """
        response = self.client.get('/ping')
        self.assert200(response)
        self.assertEqual(response.data, 'pong')

    def test_create_release(self):
        """
        Create a release

        Return the response so it can be used by other tests
        """
        response = self.client.post('/release',
            data=json.dumps({
                'note': 'test note asdf',
                'platforms': ['test_platform'],
                'references': ['TestTicket-123'],
                'team': 'Test Team',
                'user': 'testuser',
            }),
            content_type='application/json',
        )
        self.assert200(response)

        release_id = response.json['id']
        self.assertEqual(uuid.UUID(release_id).get_version(), 4)

        return release_id

    def test_create_package(self):
        """
        Create a package

        Calls create_release first, and returns both ids for future tests
        """
        release_id = self.test_create_release()

        package_response = self.client.post(
            '/release/{}/packages'.format(release_id),
            data=json.dumps({
                'name': 'test-package',
                'version': '1.2.3'
            }),
            content_type='application/json',
        )
        self.assert200(package_response)

        package_id = package_response.json['id']
        self.assertEqual(uuid.UUID(package_id).get_version(), 4)

        return release_id, package_id

    def test_add_package_results(self):
        """
        Add the results of a package deploy
        """
        release_id, package_id = self.test_create_package()

        results_response = self.client.post(
            '/release/{}/packages/{}/results'.format(
                release_id, package_id),
            data=json.dumps({
                'success': 'true',
                'foo': 'bar',
            })
        )
        self.assertEqual(results_response.status_code, 204)

    def test_add_release_log(self):
        """
        Add a log a release
        """
        pass

    def test_set_release_success(self):
        """
        Set the status of a release

        IN_PROGRESS, SUCCESSFUL, FAILED
        """
        pass

    def test_create_release_optional(self):
        """
        Create a release, omitting all optional parameters
        """
        response = self.client.post('/release',
                                    data=json.dumps({
                                        'platforms': ['test_platform'],
                                        'user': 'testuser',
                                    }),
                                    content_type='application/json',
                                    )
        self.assert200(response)

