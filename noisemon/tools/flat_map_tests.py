from noisemon.tools.flat_map import flat_map


def test_nested_list_of_ints():
    def func(x):
        return x + 1
    res1 = flat_map(func, [[1, 1, 1], [1, 1, 1], [1], [[1, 1], [1, 1]], [[1, [[1, 1], [1, 1]], 1], [1, 1]]])
    assert res1 == [[2, 2, 2], [2, 2, 2], [2], [[2, 2], [2, 2]], [[2, [[2, 2], [2, 2]], 2], [2, 2]]]
