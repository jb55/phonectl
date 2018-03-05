from setuptools import setup

setup(
   name='phonectl',
   version='1.0',
   description='phone controlling daemon',
   license="MIT",
   long_description='gtalksms phone controlling daemon',
   author='William Casarin',
   author_email='jb55@jb55.com',
   url="https://jb55.com",
   packages=['phonectl'],  #same as name
   install_requires=['sleekxmpp'], #external packages as dependencies
   scripts=['phonectld']
)
