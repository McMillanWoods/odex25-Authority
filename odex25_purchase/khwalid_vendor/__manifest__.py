{
    'name': "Khwalid Vendor",
    'version': '14.0.1.0.0',
    'summary': """Khwalid Vendor""",
    'category': 'Purchase',
    'author': 'Expert Co. Ltd.',
    'company': 'Expert Co. Ltd.',
    'website': "https://www.exp-sa.com",
    'depends': ['base','mail','contacts'],
    
    'data': [
        'security/ir.model.access.csv',
        'security/secuirty.xml',
        'data/res_partner_sequence.xml',
        'views/res_partner.xml',
        'wizard/messeage_wiz.xml',
    ],
    'installable': True,
    'application': False,
}
