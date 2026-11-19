"""A1: remove one return statement in an isolated copy of the real function."""
import inspect
import json
from unittest.mock import patch

from nlp_project import parsing

raw = 'Here is your JSON: ' + json.dumps({
    'category': 'spor',
    'entities': {'persons': [], 'organizations': ['Fenerbahçe'], 'locations': []},
}) + ' Thank you.'

source = inspect.getsource(parsing._first_balanced_json_object)
statement = 'return text[start : index + 1]'
assert source.count(statement) == 1, 'Recheck the demo after changing the parser.'
# pass only keeps the if block syntactically valid after removing its return.
modified_source = source.replace(statement, 'pass  # return statement removed')
namespace = {}
exec(compile(modified_source, '<one-line-ablation>', 'exec'), namespace)

print('REMOVED LINE:', statement)
print('This line returns the complete JSON object, without surrounding prose.')
print('INPUT:', raw)
before = parsing.parse_raw_and_cleaned(raw)
print('WITH line: raw=', before.raw_success, 'cleaned=', before.clean_success)
with patch.object(parsing, '_first_balanced_json_object', namespace['_first_balanced_json_object']):
    after = parsing.parse_raw_and_cleaned(raw)
    print('WITHOUT line: raw=', after.raw_success, 'cleaned=', after.clean_success)
    print('HANDLED ERROR:', after.error)
assert before.clean_success and not after.clean_success
print('Synthetic fixture; no production files or evaluation results were changed.')
