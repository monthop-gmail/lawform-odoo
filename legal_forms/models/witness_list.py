from odoo import api, fields, models


class WitnessList(models.Model):
    """บัญชีพยาน — ตารางรายชื่อพยานที่ขยายได้หลายหน้า
    คอลัมน์: ลำดับที่, ชื่อ-ที่อยู่, ข้อเท็จจริงที่ต้องการสืบ, หมายเหตุ
    """
    _name = 'legal.witness.item'
    _description = 'รายการพยาน'
    _order = 'sequence, id'

    document_id = fields.Many2one(
        'legal.form.document', string='เอกสาร',
        required=True, ondelete='cascade')
    sequence = fields.Integer(string='ลำดับ', default=10)
    witness_number = fields.Integer(
        string='ลำดับที่', compute='_compute_witness_number',
        store=True)

    # ข้อมูลพยาน
    name = fields.Char(string='ชื่อพยาน', required=True)
    address = fields.Text(string='ที่อยู่')
    witness_type = fields.Selection([
        ('person', 'พยานบุคคล'),
        ('document', 'พยานเอกสาร'),
        ('material', 'พยานวัตถุ'),
        ('expert', 'พยานผู้เชี่ยวชาญ'),
    ], string='ประเภทพยาน', default='person')

    # เนื้อหา
    facts_to_prove = fields.Text(
        string='ข้อเท็จจริงที่ต้องการสืบ')
    notes = fields.Char(string='หมายเหตุ')

    @api.depends('sequence')
    def _compute_witness_number(self):
        for doc_id in set(self.mapped('document_id').ids):
            items = self.filtered(
                lambda r: r.document_id.id == doc_id
            ).sorted('sequence')
            for idx, item in enumerate(items, 1):
                item.witness_number = idx
