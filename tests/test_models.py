# create a in memory temporary db
from app.models import User, Post
from app import app, db
import unittest
from datetime import datetime, timedelta, timezone
import os
os.environ['DATABASE_URL'] = 'sqllite://'


# unittest uses the classic class and methods style to create test cases
class UserModelCase(unittest.TestCase):  # inherits unittest'sTestCase class
    # create app context and db
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    # clean up db and pop app context
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # method to test password hash
    def test_password_hashing(self):
        u = User(username='john', email='john@gmail.com')
        u.set_password('test@123')
        self.assertFalse(u.check_password('best@123'))
        self.assertTrue(u.check_password('test@123'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
