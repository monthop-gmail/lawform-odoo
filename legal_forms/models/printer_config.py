from odoo import fields, models


class PrinterOffsetConfig(models.Model):
    """ตั้งค่า offset สำหรับพิมพ์เฉพาะข้อมูลลงกระดาษฟอร์มสำเร็จรูป
    แต่ละเครื่องพิมพ์อาจมี offset ต่างกัน
    """
    _name = 'legal.printer.config'
    _description = 'ตั้งค่าเครื่องพิมพ์'

    name = fields.Char(string='ชื่อเครื่องพิมพ์', required=True)
    active = fields.Boolean(string='ใช้งาน', default=True)
    offset_top = fields.Float(
        string='ชดเชยด้านบน (mm)', default=0.0,
        help='ค่าบวก = เลื่อนลง, ค่าลบ = เลื่อนขึ้น')
    offset_left = fields.Float(
        string='ชดเชยด้านซ้าย (mm)', default=0.0,
        help='ค่าบวก = เลื่อนขวา, ค่าลบ = เลื่อนซ้าย')
    notes = fields.Text(string='หมายเหตุ')
