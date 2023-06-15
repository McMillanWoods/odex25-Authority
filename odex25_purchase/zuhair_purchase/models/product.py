from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class ProductCategory(models.Model):
    _inherit = 'product.category'

    it_categ = fields.Boolean('IT Category?')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    it_categ = fields.Boolean('IT Category?',related='categ_id.it_categ')


    @api.model
    def create(self, vals):
        categ_id = self.env['product.category'].browse(vals['categ_id'])
        seq_id = self.env['ir.sequence'].search([('code','=','it.category')])
        seq_id.write({'prefix':(categ_id.name[0:4] + '/' ).replace(' ', '')})
        if categ_id.it_categ:
            vals['default_code'] = self.env['ir.sequence'].next_by_code('it.category') or '/'
        else:    
           gen_code = str(categ_id.name.split('/')[-1]) + ' / {}'.format(self.env['ir.sequence'].next_by_code('genearl.category') or "")
           vals['default_code'] = gen_code   

        return super(ProductTemplate, self).create(vals)


    def write(self, vals):
        if vals.get('categ_id',False):
            categ_id = self.env['product.category'].browse(vals['categ_id'])
            if categ_id.it_categ:
                default_code = (categ_id.name[0:4] + '/' ).replace(' ', '')
                vals_default_code = self.default_code.split('/')
                if vals_default_code:
                    vals['default_code'] = default_code + vals_default_code[0]
            # elif not categ_id.it_categ and not vals.get('default_code',False) :
            #     vals['default_code'] = ''
            else:
               gen_code = str(categ_id.name.split('/')[-1]) + ' / {}'.format(self.env['ir.sequence'].next_by_code('genearl.category') or "")
               vals['default_code'] = gen_code           

        return super(ProductTemplate, self).write(vals)

  