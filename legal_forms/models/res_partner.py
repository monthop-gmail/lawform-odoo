from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    race = fields.Char(string='เชื้อชาติ')
    nationality = fields.Char(string='สัญชาติ')
    occupation = fields.Char(string='อาชีพ')
    birthdate = fields.Date(string='วันเกิด')
    lawyer_license_no = fields.Char(string='เลขใบอนุญาตทนายความ')
