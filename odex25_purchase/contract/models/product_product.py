from odoo import models


class ProductCustom(models.Model):
    _inherit = "product.product"

    def get_product_line_description_sale(self):
        """ Compute a line description of this product, in the context of sales
                (do not use for purchases or other display reasons that don't intend to use "description_sale").
            It will often be used as the default description of a sale order line referencing this product.
        """
        name = self.display_name
        if self.description_sale:
            name += '\n' + self.description_sale

        return name
