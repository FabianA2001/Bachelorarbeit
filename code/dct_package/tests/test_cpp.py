from dc_triangulation import FieldNumber


def test_field_number():
    x1 = FieldNumber(1)
    x2 = FieldNumber(2)
    assert x1 + x2 == FieldNumber(3)
