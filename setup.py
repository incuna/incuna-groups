from setuptools import find_packages, setup


setup(
    version='0.5.0',
    name='incuna-groups',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django_crispy_forms>=1.4.0,<2',
        'django-polymorphic>=0.6.1,<1',
    ],
    description='Generic group/forum framework.',
    author='Incuna Ltd',
    author_email='admin@incuna.com',
    url='https://github.com/incuna/incuna-groups',
)
