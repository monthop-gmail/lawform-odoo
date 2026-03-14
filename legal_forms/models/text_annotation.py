from odoo import fields, models


class TextAnnotation(models.Model):
    """ข้อความแทรกอิสระบนฟอร์ม
    ใช้สำหรับ: ขีดฆ่าแก้ไข, เพิ่มข้อความนอก field, เซ็นชื่อรับรอง
    เก็บตำแหน่ง x, y บนหน้าฟอร์ม
    """
    _name = 'legal.text.annotation'
    _description = 'ข้อความแทรกอิสระ'
    _order = 'page_number, pos_y, pos_x'

    document_id = fields.Many2one(
        'legal.form.document', string='เอกสาร',
        required=True, ondelete='cascade')
    page_number = fields.Integer(
        string='หน้าที่', default=1, required=True)
    pos_x = fields.Float(
        string='ตำแหน่ง X (mm)', default=0.0,
        help='ระยะจากขอบซ้าย (มิลลิเมตร)')
    pos_y = fields.Float(
        string='ตำแหน่ง Y (mm)', default=0.0,
        help='ระยะจากขอบบน (มิลลิเมตร)')
    content = fields.Char(
        string='ข้อความ', required=True)
    font_size = fields.Float(
        string='ขนาดตัวอักษร (pt)', default=16.0)
    is_strikethrough = fields.Boolean(
        string='ขีดฆ่า', default=False,
        help='แสดงเส้นขีดฆ่าทับข้อความเดิม')
    annotation_type = fields.Selection([
        ('text', 'ข้อความ'),
        ('strikethrough', 'ขีดฆ่า'),
        ('signature', 'ลายเซ็น/รับรอง'),
    ], string='ประเภท', default='text')
    notes = fields.Char(string='หมายเหตุ')
