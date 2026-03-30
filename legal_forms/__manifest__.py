{
    'name': 'Legal Forms (แบบฟอร์มศาล)',
    'version': '18.0.1.3.0',
    'category': 'Services/Legal',
    'summary': 'แบบฟอร์มศาลและเอกสารทางกฎหมาย',
    'description': """
        ระบบจัดการแบบฟอร์มศาลและเอกสารทางกฎหมาย
        - จัดการคดีความ
        - สร้างแบบฟอร์มศาลตามมาตรฐาน
        - พิมพ์แบบฟอร์มเป็น PDF
        - เก็บประวัติเอกสารทั้งหมด
    """,
    'author': 'Your Company',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['base', 'contacts', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/form_category_data.xml',
        'data/form_template_data.xml',
        'views/res_partner_views.xml',
        'views/legal_case_views.xml',
        'views/form_template_views.xml',
        'views/form_document_views.xml',
        'views/printer_config_views.xml',
        'reports/report_form_document.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
