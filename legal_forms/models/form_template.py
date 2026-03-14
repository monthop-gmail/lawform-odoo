from odoo import fields, models


class FormCategory(models.Model):
    _name = 'legal.form.category'
    _description = 'หมวดแบบฟอร์ม'
    _order = 'sequence, name'

    name = fields.Char(string='ชื่อหมวด', required=True)
    sequence = fields.Integer(string='ลำดับ', default=10)
    template_ids = fields.One2many(
        'legal.form.template', 'category_id', string='แบบฟอร์ม')
    template_count = fields.Integer(
        string='จำนวนแบบฟอร์ม', compute='_compute_template_count')

    def _compute_template_count(self):
        for rec in self:
            rec.template_count = len(rec.template_ids)


class FormTemplate(models.Model):
    _name = 'legal.form.template'
    _description = 'แบบฟอร์มศาล (Template)'
    _order = 'category_id, sequence, name'

    name = fields.Char(string='ชื่อแบบฟอร์ม', required=True)
    code = fields.Char(string='รหัสแบบฟอร์ม', help='เช่น แบบ ๑, แบบ ๔')
    category_id = fields.Many2one(
        'legal.form.category', string='หมวด', required=True)
    sequence = fields.Integer(string='ลำดับ', default=10)
    active = fields.Boolean(string='ใช้งาน', default=True)

    case_type = fields.Selection([
        ('civil', 'คดีแพ่ง'),
        ('criminal', 'คดีอาญา'),
        ('bankruptcy', 'คดีล้มละลาย'),
        ('labor', 'คดีแรงงาน'),
        ('admin', 'คดีปกครอง'),
        ('consumer', 'คดีผู้บริโภค'),
        ('other', 'อื่นๆ'),
        ('all', 'ทุกประเภท'),
    ], string='ใช้กับประเภทคดี', default='all')

    description = fields.Text(string='คำอธิบาย')
    body_html = fields.Html(
        string='เนื้อหาแบบฟอร์ม',
        help='HTML template ของแบบฟอร์ม ใช้ placeholder เช่น '
             '%(plaintiff)s, %(defendant)s, %(court)s')
    has_continuous_text = fields.Boolean(
        string='มีข้อความต่อเนื่อง (40 ก.)', default=False,
        help='ฟอร์มที่ต้องพิมพ์เนื้อความต่อเนื่องหลายหน้า '
             'เช่น คำฟ้อง, อุทธรณ์, ฎีกา')
    report_template_id = fields.Many2one(
        'ir.actions.report', string='Report Template',
        help='เชื่อมกับ QWeb Report สำหรับพิมพ์ PDF')
