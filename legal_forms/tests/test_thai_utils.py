from datetime import date

from odoo.tests.common import TransactionCase

from ..models.thai_utils import (
    num_to_thai_text,
    to_arabic_digits,
    to_thai_date,
    to_thai_digits,
    to_thai_year,
)


class TestThaiDigits(TransactionCase):

    def test_basic_conversion(self):
        self.assertEqual(to_thai_digits('123'), '๑๒๓')

    def test_mixed_text(self):
        self.assertEqual(
            to_thai_digits('คดีหมายเลข 1234/2569'),
            'คดีหมายเลข ๑๒๓๔/๒๕๖๙',
        )

    def test_empty(self):
        self.assertFalse(to_thai_digits(''))
        self.assertIsNone(to_thai_digits(None))

    def test_no_digits(self):
        self.assertEqual(to_thai_digits('ทดสอบ'), 'ทดสอบ')

    def test_arabic_roundtrip(self):
        original = '1234567890'
        thai = to_thai_digits(original)
        self.assertEqual(thai, '๑๒๓๔๕๖๗๘๙๐')
        self.assertEqual(to_arabic_digits(thai), original)


class TestThaiDate(TransactionCase):

    def test_long_format(self):
        d = date(2026, 3, 15)
        result = to_thai_date(d, 'long')
        self.assertEqual(result, 'วันที่ ๑๕ เดือน มีนาคม พุทธศักราช ๒๕๖๙')

    def test_short_format(self):
        d = date(2026, 3, 15)
        result = to_thai_date(d, 'short')
        self.assertEqual(result, '๑๕ มี.ค. ๒๕๖๙')

    def test_full_format(self):
        d = date(2026, 3, 15)  # Sunday
        result = to_thai_date(d, 'full')
        self.assertIn('วัน', result)
        self.assertIn('มีนาคม', result)
        self.assertIn('๒๕๖๙', result)

    def test_empty(self):
        self.assertEqual(to_thai_date(None), '')
        self.assertEqual(to_thai_date(False), '')

    def test_january(self):
        d = date(2026, 1, 1)
        result = to_thai_date(d, 'long')
        self.assertIn('มกราคม', result)

    def test_december(self):
        d = date(2025, 12, 31)
        result = to_thai_date(d, 'long')
        self.assertIn('ธันวาคม', result)
        self.assertIn('๒๕๖๘', result)


class TestThaiYear(TransactionCase):

    def test_basic(self):
        self.assertEqual(to_thai_year(date(2026, 1, 1)), '๒๕๖๙')

    def test_empty(self):
        self.assertEqual(to_thai_year(None), '')


class TestNumToThaiText(TransactionCase):

    def test_zero(self):
        self.assertEqual(num_to_thai_text(0), 'ศูนย์บาทถ้วน')

    def test_none(self):
        self.assertEqual(num_to_thai_text(None), '')

    def test_integer(self):
        self.assertEqual(num_to_thai_text(100), 'หนึ่งร้อยบาทถ้วน')

    def test_five_hundred_thousand(self):
        self.assertEqual(num_to_thai_text(500000), 'ห้าแสนบาทถ้วน')

    def test_with_satang(self):
        result = num_to_thai_text(1001.50)
        self.assertEqual(result, 'หนึ่งพันเอ็ดบาทห้าสิบสตางค์')

    def test_one_million(self):
        result = num_to_thai_text(1000000)
        self.assertEqual(result, 'หนึ่งล้านบาทถ้วน')

    def test_eleven(self):
        result = num_to_thai_text(11)
        self.assertEqual(result, 'สิบเอ็ดบาทถ้วน')

    def test_twenty_one(self):
        result = num_to_thai_text(21)
        self.assertEqual(result, 'ยี่สิบเอ็ดบาทถ้วน')

    def test_large_number(self):
        result = num_to_thai_text(2500000)
        self.assertEqual(result, 'สองล้านห้าแสนบาทถ้วน')

    def test_satang_only(self):
        result = num_to_thai_text(0.75)
        self.assertIn('สตางค์', result)
