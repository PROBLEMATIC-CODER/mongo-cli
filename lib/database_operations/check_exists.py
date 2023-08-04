
def check_db_exists(client,name):
    dbs = client.list_database_names()
    lowercase_db = [item.strip().lower() for item in dbs]
    if name.lower() in lowercase_db:
        lower_index = lowercase_db.index(name.lower())
        db_name = dbs[lower_index]
        return {'exists': True, 'name': db_name}
    else:
        return {'exists': False}
