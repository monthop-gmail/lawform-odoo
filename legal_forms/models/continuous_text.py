from odoo import api, fields, models


class ContinuousText(models.Model):
    """เนื้อความต่อเนื่องสำหรับฟอร์มที่มี 40 ก. ต่อท้าย
    เช่น คำฟ้อง, คำร้อง, อุทธรณ์, ฎีกา ฯลฯ
    แต่ละ section คือ 1 ข้อ (ข้อ ๑, ข้อ ๒, ...)
    """
    _name = 'legal.continuous.text'
    _description = 'เนื้อความต่อเนื่อง (40 ก.)'
    _order = 'sequence, id'

    document_id = fields.Many2one(
        'legal.form.document', string='เอกสาร',
        required=True, ondelete='cascade')
    sequence = fields.Integer(string='ลำดับ', default=10)
    section_label = fields.Char(
        string='หัวข้อ', default='ข้อ',
        help='เช่น ข้อ ๑, ข้อ ๒')
    section_number = fields.Char(string='ลำดับข้อ')
    content = fields.Html(
        string='เนื้อความ',
        help='เนื้อความต่อเนื่อง โปรแกรมจะตัดลงฟอร์ม 40 ก. อัตโนมัติ')

    @api.model
    def _get_display_name(self):
        for rec in self:
            label = rec.section_label or 'ข้อ'
            number = rec.section_number or str(rec.sequence)
            rec.display_name = f"{label} {number}"
