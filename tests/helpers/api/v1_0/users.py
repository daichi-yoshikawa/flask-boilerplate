from http import HTTPStatus


users = [
  {
    'request': dict(name='test001', email='test001@test', password='testtest'),
    'expected': dict(url='http://localhost/api/v1_0/users/1/'),
    'status_code': HTTPStatus.CREATED,
  },
  {
    'request': dict(name='test002', email='test002@test', password='testtest'),
    'expected': dict(url='http://localhost/api/v1_0/users/2/'),
    'status_code': HTTPStatus.CREATED,
  },
  {
    'request': dict(name='test003', email='test003@test', password='testtest'),
    'expected': dict(url='http://localhost/api/v1_0/users/3/'),
    'status_code': HTTPStatus.CREATED,
  },
]

users_to_signup = list(users)
users_to_signup += [
  {
    'request': dict(name='test001', email='test004@test', password='testtest'),
    'expected': dict(error={'message': 'Username:test001 is already used.'}),
    'status_code': HTTPStatus.CONFLICT,
  },
  {
    'request': dict(name='test004', email='test001@test', password='testtest'),
    'expected': dict(error={'message': 'Email:test001@test is already used.'}),
    'status_code': HTTPStatus.CONFLICT,
  },
]

users_to_get = [
  {
    'request': 1,
    'expected': dict(id=1, name='test001', email='test001@test', agreed_eula=False, url='http://localhost/api/v1_0/users/1/'),
    'status_code': HTTPStatus.OK,
  },
  {
    'request': 3,
    'expected': dict(id=3, name='test003', email='test003@test', agreed_eula=False, url='http://localhost/api/v1_0/users/3/'),
    'status_code': HTTPStatus.OK,
  },
  {
    'request': 100,
    'expected': dict(error={'message': 'User ID:100 was not found.'}),
    'status_code': HTTPStatus.NOT_FOUND,
  },
]
