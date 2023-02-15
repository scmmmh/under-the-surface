from os import path, mkdir
from shutil import rmtree, copytree
from subprocess import run


if path.exists('docs'):
    rmtree('docs')

mkdir('docs')

for lang in ['en', 'de']:
    run(['jupyter-book', 'build', lang])
    copytree(path.join(lang, '_build', 'html'), path.join('docs', lang))
