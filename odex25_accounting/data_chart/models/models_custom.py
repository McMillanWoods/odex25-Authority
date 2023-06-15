from odoo import models, fields, api, _


class BaseModelExtend(models.BaseModel):
    _name = 'basemodel.extend_custom_data_chart'

    def _register_hook(self):

        @api.model
        @api.returns(
            'self', upgrade=lambda self, value, args, offset=0, limit=None, order=None,
            count=False: value if count else self.browse(value), downgrade=lambda self, value, args,
            offset=0, limit=None, order=None, count=False: value if count else value.ids)
        def search(self, args, offset=0, limit=None, order=None, count=False):
            context = dict(self.env.context)
            if context.get('data_chart_search', False):
                res = self._search([], offset=offset, limit=limit, order=order, count=count)
            else:
                res = self._search(args, offset=offset, limit=limit, order=order, count=count)
            
            return res if count else self.browse(res)


# -------------------------------------------------------
        models.BaseModel.search = search
        return super(BaseModelExtend, self)._register_hook()
