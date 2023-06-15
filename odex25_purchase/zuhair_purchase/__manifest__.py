{
    'name': "Zuhair Purchase",
    'version': '14.0.1.0.0',
    'summary': """add new purchase features for zuhair project in particular""",
    'category': 'Purchase',
    'author': 'Expert Co. Ltd.',
    'company': 'Expert Co. Ltd.',
    'website': "https://www.exp-sa.com",
    'depends': [
        'base',
        'mail',
        'purchase',
    ],
    
    'data': [
        'security/ir.model.access.csv',
        'security/secuirty.xml',
        'views/product.xml',
        'views/purchase_order.xml',
    ],
    'installable': True,
    'application': False,
}
