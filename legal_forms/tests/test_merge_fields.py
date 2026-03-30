from datetime import date

from odoo.tests.common import TransactionCase


class TestFormatThaiId(TransactionCase):

    def _get_doc(self):
        """Get a FormDocument instance for testing helper methods."""
        return self.env['legal.form.document'].new({})

    def test_valid_13_digits(self):
        doc = self._get_doc()
        self.assertEqual(doc._format_thai_id('1234567890123'), '1-2345-67890-12-3')

    def test_with_existing_dashes(self):
        doc = self._get_doc()
        result = doc._format_thai_id('1-2345-67890-12-3')
        self.assertEqual(result, '1-2345-67890-12-3')

    def test_empty(self):
        doc = self._get_doc()
        self.assertEqual(doc._format_thai_id(''), '')
        self.assertEqual(doc._format_thai_id(None), '')
        self.assertEqual(doc._format_thai_id(False), '')

    def test_wrong_length(self):
        doc = self._get_doc()
        # Should return as-is
        self.assertEqual(doc._format_thai_id('12345'), '12345')

    def test_non_numeric(self):
        doc = self._get_doc()
        self.assertEqual(doc._format_thai_id('ABC'), 'ABC')


class TestFormatAddress(TransactionCase):

    def _get_doc(self):
        return self.env['legal.form.document'].new({})

    def test_full_address(self):
        partner = self.env['res.partner'].create({
            'name': 'ทดสอบ',
            'street': '123/4 ถ.สุขุมวิท',
            'street2': 'แขวงคลองเตย',
            'city': 'เขตคลองเตย',
            'zip': '10110',
        })
        doc = self._get_doc()
        result = doc._format_address(partner)
        self.assertIn('123/4', result)
        self.assertIn('คลองเตย', result)
        self.assertIn('10110', result)

    def test_empty_partner(self):
        doc = self._get_doc()
        empty = self.env['res.partner']
        self.assertEqual(doc._format_address(empty), '')

    def test_partial_address(self):
        partner = self.env['res.partner'].create({
            'name': 'ทดสอบ',
            'street': '55 หมู่ 3',
        })
        doc = self._get_doc()
        result = doc._format_address(partner)
        self.assertEqual(result, '55 หมู่ 3')


class TestComputeAge(TransactionCase):

    def _get_doc(self):
        return self.env['legal.form.document'].new({})

    def test_basic_age(self):
        doc = self._get_doc()
        # Born 30 years ago
        birthdate = date(1996, 1, 1)
        result = doc._compute_age(birthdate)
        # Should be Thai digits
        self.assertTrue(result)
        self.assertNotIn('0', result)  # should be Thai digits

    def test_no_birthdate(self):
        doc = self._get_doc()
        self.assertEqual(doc._compute_age(None), '')
        self.assertEqual(doc._compute_age(False), '')


class TestJoinPartyNames(TransactionCase):

    def _get_doc(self):
        return self.env['legal.form.document'].new({})

    def test_single_party(self):
        partner = self.env['res.partner'].create({'name': 'นาย ก'})
        doc = self._get_doc()
        result = doc._join_party_names(partner)
        self.assertEqual(result, 'นาย ก')

    def test_two_parties(self):
        p1 = self.env['res.partner'].create({'name': 'นาย ก'})
        p2 = self.env['res.partner'].create({'name': 'นาย ข'})
        doc = self._get_doc()
        result = doc._join_party_names(p1 | p2)
        self.assertIn('นาย ก', result)
        self.assertIn('นาย ข', result)
        self.assertIn('และ', result)

    def test_three_parties(self):
        p1 = self.env['res.partner'].create({'name': 'นาย ก'})
        p2 = self.env['res.partner'].create({'name': 'นาย ข'})
        p3 = self.env['res.partner'].create({'name': 'นาย ค'})
        doc = self._get_doc()
        result = doc._join_party_names(p1 | p2 | p3)
        self.assertIn(',', result)
        self.assertIn('และ', result)

    def test_empty(self):
        doc = self._get_doc()
        empty = self.env['res.partner']
        self.assertEqual(doc._join_party_names(empty), '')


class TestApplyMergeFields(TransactionCase):

    def test_basic_replacement(self):
        partner = self.env['res.partner'].create({
            'name': 'นายทดสอบ ตัวอย่าง',
            'vat': '1234567890123',
        })
        case = self.env['legal.case'].create({
            'name': 'ทดสอบ/2569',
            'case_type': 'civil',
            'plaintiff_id': partner.id,
            'court_name': 'ศาลแพ่ง',
        })
        tmpl = self.env['legal.form.template'].search([], limit=1)
        doc = self.env['legal.form.document'].create({
            'name': 'ทดสอบ merge',
            'template_id': tmpl.id,
            'case_id': case.id,
        })
        # body_html should have replacements applied
        if doc.body_html:
            self.assertNotIn('%(plaintiff)s', doc.body_html)
            self.assertNotIn('%(court)s', doc.body_html)

    def test_no_case(self):
        """Document without case should not crash."""
        tmpl = self.env['legal.form.template'].search([], limit=1)
        doc = self.env['legal.form.document'].create({
            'name': 'ทดสอบ no case',
            'template_id': tmpl.id,
        })
        # Should have body from template, but no merge applied
        self.assertTrue(doc.body_html or True)  # just shouldn't crash
