import importlib
import pathlib
import sys

root=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'content'))
for directory in ('build','public'):
    (root/directory).mkdir(exist_ok=True)
for suffix in 'abcde':
    name=f'chapters_{suffix}'
    if '--draft' in sys.argv and not (root/'content'/f'{name}.py').exists():
        break
    importlib.import_module(name)
from author import build
build('--draft' in sys.argv)
