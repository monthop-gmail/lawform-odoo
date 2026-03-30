from datetime import date

from odoo import api, fields, models

from .thai_utils import to_thai_date, to_thai_digits, to_thai_year


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
    document_date = fields.Date(
        string='วันที่เอกสาร', default=fields.Date.today)

    # ตัวเลือกการพิมพ์
    print_mode = fields.Selection([
        ('full', 'พิมพ์ทั้งฟอร์ม'),
        ('data_only', 'พิมพ์เฉพาะข้อมูล'),
    ], string='โหมดพิมพ์', default='full',
        help='พิมพ์เฉพาะข้อมูล: สำหรับพิมพ์ลงกระดาษฟอร์มสำเร็จรูป '
             '(เช่น ลูกความเซ็นชื่อไว้แล้ว)')
    duplex_mode = fields.Selection([
        ('all', 'ทุกหน้า'),
        ('odd', 'เฉพาะหน้าคี่ (ด้านหน้า)'),
        ('even', 'เฉพาะหน้าคู่ (ด้านหลัง)'),
    ], string='เลือกหน้าพิมพ์', default='all',
        help='สำหรับฟอร์มที่พิมพ์หน้า-หลัง: '
             'พิมพ์หน้าคี่ก่อน กลับกระดาษ แล้วพิมพ์หน้าคู่')
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

    # บัญชีพยาน
    has_witness_list = fields.Boolean(
        related='template_id.has_witness_list')
    witness_item_ids = fields.One2many(
        'legal.witness.item', 'document_id',
        string='บัญชีพยาน')
    witness_count = fields.Integer(
        string='จำนวนพยาน', compute='_compute_witness_count')

    # ข้อความแทรกอิสระ
    annotation_ids = fields.One2many(
        'legal.text.annotation', 'document_id',
        string='ข้อความแทรก')
    annotation_count = fields.Integer(
        string='จำนวนข้อความแทรก',
        compute='_compute_annotation_count')

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-fill case data + template body on create"""
        for vals in vals_list:
            # Fill from case
            if vals.get('case_id') and not vals.get('plaintiff_id'):
                case = self.env['legal.case'].browse(vals['case_id'])
                vals.setdefault('plaintiff_id', case.plaintiff_id.id)
                vals.setdefault('defendant_id', case.defendant_id.id)
                vals.setdefault('lawyer_id', case.lawyer_id.id)
                vals.setdefault('court_name', case.court_name)
                vals.setdefault('black_case_no', case.black_case_no)
                vals.setdefault('red_case_no', case.red_case_no)
            # Fill body from template
            if vals.get('template_id') and not vals.get('body_html'):
                tmpl = self.env['legal.form.template'].browse(vals['template_id'])
                vals['body_html'] = tmpl.body_html
        records = super().create(vals_list)
        # Apply mail merge on body_html
        for rec in records:
            if rec.body_html and rec.case_id:
                rec.body_html = rec._apply_merge_fields(rec.body_html)
        return records

    def write(self, vals):
        """Re-apply merge fields when case changes"""
        res = super().write(vals)
        if 'case_id' in vals:
            for rec in self:
                if rec.case_id:
                    rec.plaintiff_id = rec.case_id.plaintiff_id
                    rec.defendant_id = rec.case_id.defendant_id
                    rec.lawyer_id = rec.case_id.lawyer_id
                    rec.court_name = rec.case_id.court_name
                    rec.black_case_no = rec.case_id.black_case_no
                    rec.red_case_no = rec.case_id.red_case_no
                    if rec.body_html:
                        rec.body_html = rec._apply_merge_fields(rec.body_html)
        return res

    def _apply_merge_fields(self, html):
        """Replace merge placeholders in body_html with actual data.

        Supported placeholders:
            %(plaintiff)s, %(defendant)s, %(lawyer)s — ชื่อคู่ความ
            %(court)s — ชื่อศาล
            %(black_case)s, %(red_case)s — เลขคดี
            %(plaintiff_address)s, %(defendant_address)s — ที่อยู่
            %(plaintiff_phone)s, %(lawyer_phone)s — โทรศัพท์
            %(plaintiff_id_no)s, %(defendant_id_no)s — เลขประจำตัว
            %(date_long)s — วันที่ ๑๕ เดือน มีนาคม พุทธศักราช ๒๕๖๙
            %(date_short)s — ๑๕ มี.ค. ๒๕๖๙
            %(date_full)s — วันจันทร์ที่ ๑๕ เดือน มีนาคม พุทธศักราช ๒๕๖๙
            %(thai_year)s — ๒๕๖๙
            %(black_case_thai)s, %(red_case_thai)s — เลขคดี (ตัวเลขไทย)
        """
        if not html:
            return html
        doc_date = self.document_date or date.today()
        replacements = {
            # คู่ความ
            '%(plaintiff)s': self.plaintiff_id.name or '',
            '%(defendant)s': self.defendant_id.name or '',
            '%(lawyer)s': self.lawyer_id.name or '',
            # ศาล / เลขคดี
            '%(court)s': self.court_name or '',
            '%(black_case)s': self.black_case_no or '',
            '%(red_case)s': self.red_case_no or '',
            '%(black_case_thai)s': to_thai_digits(self.black_case_no or ''),
            '%(red_case_thai)s': to_thai_digits(self.red_case_no or ''),
            # ที่อยู่
            '%(plaintiff_address)s': self._format_address(self.plaintiff_id),
            '%(defendant_address)s': self._format_address(self.defendant_id),
            '%(lawyer_address)s': self._format_address(self.lawyer_id),
            # โทรศัพท์
            '%(plaintiff_phone)s': self.plaintiff_id.phone or '',
            '%(defendant_phone)s': self.defendant_id.phone or '',
            '%(lawyer_phone)s': self.lawyer_id.phone or '',
            # เลขประจำตัว
            '%(plaintiff_id_no)s': self.plaintiff_id.vat or '',
            '%(defendant_id_no)s': self.defendant_id.vat or '',
            # วันที่ (พุทธศักราช + ตัวเลขไทย)
            '%(date_long)s': to_thai_date(doc_date, 'long'),
            '%(date_short)s': to_thai_date(doc_date, 'short'),
            '%(date_full)s': to_thai_date(doc_date, 'full'),
            '%(thai_year)s': to_thai_year(doc_date),
        }
        for key, value in replacements.items():
            html = html.replace(key, value)
        return html

    def _format_address(self, partner):
        """Format partner address as single line"""
        if not partner:
            return ''
        parts = [
            partner.street or '',
            partner.street2 or '',
            partner.city or '',
            partner.state_id.name if partner.state_id else '',
            partner.zip or '',
        ]
        return ' '.join(p for p in parts if p)

    @api.onchange('case_id')
    def _onchange_case_id(self):
        """ดึงข้อมูลจากคดีมาเติมอัตโนมัติ (UI)"""
        if self.case_id:
            self.plaintiff_id = self.case_id.plaintiff_id
            self.defendant_id = self.case_id.defendant_id
            self.lawyer_id = self.case_id.lawyer_id
            self.court_name = self.case_id.court_name
            self.black_case_no = self.case_id.black_case_no
            self.red_case_no = self.case_id.red_case_no
            if self.body_html:
                self.body_html = self._apply_merge_fields(self.body_html)

    @api.depends('witness_item_ids')
    def _compute_witness_count(self):
        for rec in self:
            rec.witness_count = len(rec.witness_item_ids)

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
        if self.print_mode == 'data_only':
            return self.env.ref(
                'legal_forms.action_report_form_data_only'
            ).report_action(self)
        if self.duplex_mode == 'odd':
            return self.env.ref(
                'legal_forms.action_report_form_odd_pages'
            ).report_action(self)
        if self.duplex_mode == 'even':
            return self.env.ref(
                'legal_forms.action_report_form_even_pages'
            ).report_action(self)
        return self.env.ref(
            'legal_forms.action_report_form_document'
        ).report_action(self)

    def action_draft(self):
        self.write({'state': 'draft'})
