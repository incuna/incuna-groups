from setuptools import find_packages, setup


setup(
    version='0.1',
    name='incuna-groups',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django_crispy_forms==1.4.0',
    ],
    description='Generic group/forum framework.',
    author='Incuna Ltd',
    author_email='admin@incuna.com',
    url='https://github.com/incuna/incuna-groups',
)
