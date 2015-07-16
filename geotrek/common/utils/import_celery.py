import os

def subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(subclasses(subclass))

    return all_subclasses

def create_tmp_destination(name):
    save_dir = '/tmp/geotrek/{}'.format(name)
    if not os.path.exists('/tmp/geotrek'):
        os.mkdir('/tmp/geotrek')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    return save_dir, '/'.join((save_dir, name))