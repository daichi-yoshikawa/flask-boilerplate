from app import create_app
from app.models import db
from app.models.role import Role


app = create_app()
app.app_context().push()

DefaultRoles = [
  {
    'name': 'user',
  },
  {
    'name': 'admin',
  },
]

def insert_default_roles():
  try:
    if Role.query.count() == 0:
      print('roles table is empty. Insert default roles.')
      for i, role in enumerate(DefaultRoles):
        print(f"role:{role['name']} is inserted.")

        role['id'] = i + 1
        row = Role(**role)
        db.session.add(row)
      db.session.commit()
      print('Default roles are inserted.')
    else:
      print('roles table has some data already. Skip inserting data.')
  except Exception as e:
    print(f'Error occurred. {type(e)}: {str(e)}\nExecute rollback.')
    db.session.rollback()
    print('Rollback done.')


if __name__ == '__main__':
  insert_default_roles()
