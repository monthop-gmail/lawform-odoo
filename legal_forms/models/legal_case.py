from odoo import api, fields, models


class LegalCase(models.Model):
    _name = 'legal.case'
    _description = 'คดีความ'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='เลขคดี',
        required=True,
        tracking=True,
    )
    case_type = fields.Selection([
        ('civil', 'คดีแพ่ง'),
        ('criminal', 'คดีอาญา'),
        ('bankruptcy', 'คดีล้มละลาย'),
        ('labor', 'คดีแรงงาน'),
        ('admin', 'คดีปกครอง'),
        ('consumer', 'คดีผู้บริโภค'),
        ('other', 'อื่นๆ'),
    ], string='ประเภทคดี', required=True, tracking=True)

    state = fields.Selection([
        ('draft', 'ร่าง'),
        ('filed', 'ยื่นฟ้อง'),
        ('hearing', 'นัดพิจารณา'),
        ('judged', 'พิพากษา'),
        ('appeal', 'อุทธรณ์'),
        ('supreme', 'ฎีกา'),
        ('closed', 'ปิดคดี'),
    ], string='สถานะ', default='draft', tracking=True)

    # คู่ความ
    plaintiff_id = fields.Many2one(
        'res.partner', string='โจทก์', tracking=True)
    defendant_id = fields.Many2one(
        'res.partner', string='จำเลย', tracking=True)
    lawyer_id = fields.Many2one(
        'res.partner', string='ทนายความ', tracking=True)

    # ศาล
    court_name = fields.Char(string='ศาล')
    black_case_no = fields.Char(string='เลขคดีดำ')
    red_case_no = fields.Char(string='เลขคดีแดง')

    # รายละเอียดคดี
    case_category = fields.Char(
        string='ประเภทความ',
        help='เช่น แพ่ง, อาญา, ผู้บริโภค — ใช้แสดงในช่อง "ความ ..." ของฟอร์ม')
    charge = fields.Char(
        string='ข้อหา/ฐานความผิด',
        help='เช่น ผิดสัญญากู้ยืม, ลักทรัพย์')
    claim_amount = fields.Float(
        string='จำนวนทุนทรัพย์',
        help='จำนวนเงินที่เรียกร้อง (บาท)')
    description = fields.Html(string='รายละเอียดคดี')

    # วันที่สำคัญ
    date_filed = fields.Date(string='วันที่ยื่นฟ้อง')
    date_hearing = fields.Date(string='วันนัดพิจารณา')
    judgment_date = fields.Date(string='วันพิพากษา')
    judgment_read_date = fields.Date(string='วันอ่านคำพิพากษา')

    # เอกสาร
    document_ids = fields.One2many(
        'legal.form.document', 'case_id', string='เอกสาร')
    document_count = fields.Integer(
        string='จำนวนเอกสาร', compute='_compute_document_count')

    @api.depends('document_ids')
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = len(rec.document_ids)

    def action_view_documents(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'เอกสาร',
            'res_model': 'legal.form.document',
            'view_mode': 'list,form',
            'domain': [('case_id', '=', self.id)],
            'context': {'default_case_id': self.id},
        }
