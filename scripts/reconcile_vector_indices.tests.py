import unittest

from reconcile_vector_indices import get_holes, reconcile

cases = [
    ([1,2,3,4,5,6], [0]),
    ([1,3,5,7,9], [0,2,4,6,8]),
    ([1,10], [0,2,3,4,5,6,7,8,9])
]

class TestFindHoles(unittest.TestCase):
    def test_empty_case(self):
        d = []
        self.assertEqual(get_holes(d), [])

    def test_trivial_case(self):
        d = [0,1,2,3,4,5]
        self.assertEqual(get_holes(d), [])

    def test_non_trivial_cases(self):
        for i, (request, result) in enumerate(cases):
            with self.subTest(i=i):
                self.assertEqual(get_holes(request), result)

rcases = [
    [0,1,2,3,4,5,6,7],
    [1,2,3,4,5,6,7,8],
    [0,2,4,6],
    [0,10],
    [1, 10, 100],
]

class TestIndexReconcilation(unittest.TestCase):
    def test_non_trivial_cases(self):
        for i, (request) in enumerate(rcases):
            with self.subTest(i=i):
                map_ = {a: a for a in request}
                for from_,to_ in reconcile(request):
                    map_[from_] = to_
                self.assertEqual(sorted(map_.values()), list(range(len(request))))

if __name__ == "__main__":
    unittest.main()

