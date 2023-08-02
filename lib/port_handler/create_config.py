def create_config_yaml():
    filename = 'config.yaml'
    try:
        with open(filename, 'x') as file:
            pass
        return True
    except IOError as e:
        return False