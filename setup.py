from setuptools import find_packages, setup


setup(
    version='4.0.2',
    name='incuna-groups',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django_crispy_forms>=1.4.0,<2',
        'django-polymorphic>=1.2,<1.3',
        'incuna-pagination>=0.1.1,<1',
    ],
    description='Generic group/forum framework.',
    author='Incuna Ltd',
    author_email='admin@incuna.com',
    url='https://github.com/incuna/incuna-groups',
)
