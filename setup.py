from setuptools import find_packages, setup


setup(
    version='3.2.0',
    name='incuna-groups',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django_crispy_forms>=1.4.0,<2',
        'django-polymorphic>=0.7.2,<1',
    ],
    description='Generic group/forum framework.',
    author='Incuna Ltd',
    author_email='admin@incuna.com',
    url='https://github.com/incuna/incuna-groups',
)
