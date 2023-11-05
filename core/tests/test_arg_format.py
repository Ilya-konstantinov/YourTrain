from unittest import TestCase
from model.arg_format import filter_arg, cor_time
from data.answer_enums import BAD_REQUEST


class TestFilter(TestCase):
    def test_filter_arg_1(self):
        self.assertEquals(filter_arg('0'), 0)

    def test_filter_arg_2(self):
        self.assertEquals(filter_arg('3'), BAD_REQUEST.BAD_FILTER)

    def test_filter_arg_3(self):
        self.assertEquals(filter_arg('скоросные'), BAD_REQUEST.BAD_FILTER)


class TestTime(TestCase):
    def test_cor_time_1(self):
        self.assertTrue(cor_time("+20"))

    def test_cor_time_2(self):
        self.assertTrue(cor_time("-20"))

    def test_cor_time_3(self):
        self.assertTrue(cor_time("8:20"))

    def test_cor_time_4(self):
        self.assertEquals(cor_time("8:80"), BAD_REQUEST.BAD_TIME)
