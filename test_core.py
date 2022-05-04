from npbc_core import get_number_of_each_weekday

def test_get_number_of_each_weekday():
    assert list(get_number_of_each_weekday(1, 2022)) == [5, 4, 4, 4, 4, 5, 5]
    assert list(get_number_of_each_weekday(2, 2022)) == [4, 4, 4, 4, 4, 4, 4]
    assert list(get_number_of_each_weekday(3, 2022)) == [4, 5, 5 ,5, 4, 4, 4]
    assert list(get_number_of_each_weekday(2, 2020)) == [4, 4, 4, 4, 4, 5, 4]
    assert list(get_number_of_each_weekday(12, 1954)) == [4, 4, 5, 5, 5, 4, 4]