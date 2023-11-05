from unittest import TestCase
from model.path import CacheRequest, Station

dep_st_test = Station(id=0, title='ЗЕМЛЯ')
arr_st_test = Station(id=1, title='ВОЗДУХ')


class TestCacheRequest(TestCase):
    def setUp(self) -> None:
        self.CacheRequest = CacheRequest([dep_st_test], [arr_st_test])


class TestInit(TestCacheRequest):
    def test_initial_dep_time(self):
        self.assertEquals(self.CacheRequest.dep_time, '0')

    def test_initial_sort_type(self):
        self.assertEquals(self.CacheRequest.sort_type, 0)

    def test_initial_filter_type(self):
        self.assertEquals(self.CacheRequest.filter_type, 0)

    def test_initial_col(self):
        self.assertEquals(self.CacheRequest.col, 5)


class TestParams(TestCacheRequest):
    def test_params(self):
        self.assertEquals(self.CacheRequest.get_params(), "0 1 0 0 0 5")

    def test_params_change_false(self):
        self.CacheRequest.dep_st.append(arr_st_test)
        self.assertNotEqual(self.CacheRequest.get_params(), "0 1 -- 1 0 0 0 5")
        self.CacheRequest.dep_st = [dep_st_test]

    def test_params_change_true(self):
        self.CacheRequest.dep_st.append(arr_st_test)
        self.CacheRequest.is_mlt = True
        self.assertNotEqual(self.CacheRequest.get_params(), "0 1 -- 1 0 0 0 5")
        self.CacheRequest.dep_st = [dep_st_test]
