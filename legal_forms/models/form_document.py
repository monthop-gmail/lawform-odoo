from odoo import api, fields, models


class FormDocument(models.Model):
    _name = 'legal.form.document'
    _description = 'เอกสารแบบฟอร์ม'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(
        string='ชื่อเอกสาร', required=True, tracking=True)
    template_id = fields.Many2one(
        'legal.form.template', string='แบบฟอร์ม', required=True)
    case_id = fields.Many2one(
        'legal.case', string='คดี', tracking=True)

    state = fields.Selection([
        ('draft', 'ร่าง'),
        ('confirmed', 'ยืนยัน'),
        ('printed', 'พิมพ์แล้ว'),
    ], string='สถานะ', default='draft', tracking=True)

    # ข้อมูลจากคดี (auto-fill)
    plaintiff_id = fields.Many2one(
        'res.partner', string='โจทก์/ผู้ร้อง')
    defendant_id = fields.Many2one(
        'res.partner', string='จำเลย/ผู้คัดค้าน')
    lawyer_id = fields.Many2one(
        'res.partner', string='ทนายความ')
    court_name = fields.Char(string='ศาล')
    black_case_no = fields.Char(string='เลขคดีดำ')
    red_case_no = fields.Char(string='เลขคดีแดง')

    # ตัวเลือกการพิมพ์
    print_mode = fields.Selection([
        ('full', 'พิมพ์ทั้งฟอร์ม'),
        ('data_only', 'พิมพ์เฉพาะข้อมูล'),
    ], string='โหมดพิมพ์', default='full',
        help='พิมพ์เฉพาะข้อมูล: สำหรับพิมพ์ลงกระดาษฟอร์มสำเร็จรูป '
             '(เช่น ลูกความเซ็นชื่อไว้แล้ว)')
    printer_config_id = fields.Many2one(
        'legal.printer.config', string='เครื่องพิมพ์',
        help='เลือกเครื่องพิมพ์เพื่อปรับ offset ตำแหน่ง')

    # เนื้อหาที่กรอก
    body_html = fields.Html(string='เนื้อหาเอกสาร')
    notes = fields.Text(string='หมายเหตุ')

    # ข้อความต่อเนื่อง (40 ก.)
    has_continuous_text = fields.Boolean(
        related='template_id.has_continuous_text')
    continuous_text_ids = fields.One2many(
        'legal.continuous.text', 'document_id',
        string='เนื้อความต่อเนื่อง (40 ก.)')
    continuous_text_preview = fields.Html(
        string='ดูตัวอย่างข้อความต่อเนื่อง',
        compute='_compute_continuous_text_preview')

    # ข้อความแทรกอิสระ
    annotation_ids = fields.One2many(
        'legal.text.annotation', 'document_id',
        string='ข้อความแทรก')
    annotation_count = fields.Integer(
        string='จำนวนข้อความแทรก',
        compute='_compute_annotation_count')

    @api.onchange('case_id')
    def _onchange_case_id(self):
        """ดึงข้อมูลจากคดีมาเติมอัตโนมัติ"""
        if self.case_id:
            self.plaintiff_id = self.case_id.plaintiff_id
            self.defendant_id = self.case_id.defendant_id
            self.lawyer_id = self.case_id.lawyer_id
            self.court_name = self.case_id.court_name
            self.black_case_no = self.case_id.black_case_no
            self.red_case_no = self.case_id.red_case_no

    @api.depends('annotation_ids')
    def _compute_annotation_count(self):
        for rec in self:
            rec.annotation_count = len(rec.annotation_ids)

    @api.depends('continuous_text_ids', 'continuous_text_ids.content',
                 'continuous_text_ids.section_label',
                 'continuous_text_ids.section_number')
    def _compute_continuous_text_preview(self):
        for rec in self:
            if not rec.continuous_text_ids:
                rec.continuous_text_preview = False
                continue
            parts = []
            for ct in rec.continuous_text_ids:
                label = ct.section_label or 'ข้อ'
                number = ct.section_number or ''
                header = f"<strong>{label} {number}</strong>"
                content = ct.content or ''
                parts.append(f"<p>{header} {content}</p>")
            rec.continuous_text_preview = ''.join(parts)

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """ดึง template มาเป็นเนื้อหาเริ่มต้น"""
        if self.template_id and self.template_id.body_html:
            self.body_html = self.template_id.body_html

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_print(self):
        self.write({'state': 'printed'})
        if self.template_id.report_template_id:
            return self.template_id.report_template_id.report_action(self)

    def action_draft(self):
        self.write({'state': 'draft'})
