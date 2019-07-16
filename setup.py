from distutils.core import setup

setup(
    name='jmanager',
    version='0.1a',
    description='A python based jail manager',
    author='Lara Fernandez Cueto',
    author_email='larafercue@gmail.com',
    url='https://github.com/LaraFerCue/jmanager',
    packages=['jmanager', 'jmanager.commands', 'jmanager.factories', 'jmanager/models', 'jmanager.utils'],
    scripts=['jmanager/jmanager']
)
