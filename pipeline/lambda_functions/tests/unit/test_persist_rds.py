import pytest
from lambda_functions.persist_rds_lambda.lambda_function import flatten

d1 = {'a': 'abc'}
d2 = {'a': 'abc',
      'b': {'c': 1,
            'd': 2}}
d3 = {'meta': {'partial': {'key': 'abc'}}}


def test_flatten():
    flat_d2 = {'a': 'abc',
               'b.c': 1,
               'b.d': 2}

    assert flatten(d1, delimiter='.') == d1
    assert flatten(d2, delimiter='.') == flat_d2
    assert flatten(d3, delimiter='.') == {'meta.partial.key': 'abc'}
    assert flatten(d3, delimiter='#') == {'meta#partial#key': 'abc'}
    assert flatten({}) == {}
