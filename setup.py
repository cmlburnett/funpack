from distutils.core import setup

majv = 1
minv = 0

setup(
	name = 'funpack',
	version = "%d.%d" %(majv,minv),
	description = "Python module make the built-in struct module easier to use for unpacking",
	author = "Colin ML Burnett",
	author_email = "cmlburnett@gmail.com",
	url = "",
	packages = ['funpack'],
	package_data = {'funpack': ['funpack/__init__.py']},
	classifiers = [
		'Programming Language :: Python :: 3.4'
	]
)
