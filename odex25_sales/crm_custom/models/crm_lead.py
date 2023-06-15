# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    inquiry_date = fields.Date('Inquiry Date')
    site_visit_date = fields.Date('Site Visit Date')
    submit_date = fields.Date('Submit Date', default=fields.Date.context_today)

    bidbond = fields.Boolean('Bid Bond')

    project_country_id = fields.Many2one('res.country', 'Country')
    project_state_id = fields.Many2one('res.country.state', string='Region')
    city_id = fields.Many2one('res.country.city', 'City')
    industry_id = fields.Many2one('res.partner.industry', 'Industry(Classification)')
    sector_id = fields.Many2one('sector', 'Sector(Role)')
    department_id = fields.Many2one('hr.department',string='Business Unit')
    product_id = fields.Many2one('product.product',string='Services(Contract Type)', store=True)

    must_lead = fields.Boolean('Must Lead (RFI)')

    project_category_id = fields.Many2one('project.category', 'Project Category')
    project_duration = fields.Integer('Project Duration (Months) As per (SOW)')
    project_duration_internal = fields.Integer('Project Duration (Internal)')
    total_site_area = fields.Float('Total Site Area (m2) (Excluding Building Footprint)')
    main_building_prototype = fields.Float('Main Building Prototype Area (m2)')
    main_building_site = fields.Float('Main Building Site Adaptation Area (m2)')
    main_building_total = fields.Float('Main Building Total Area (m2)')
    floor_area_ratio = fields.Float('Floor Area Ratio (FAR)')
    site_works_area = fields.Float('Site Works Area (m2)')
    ancillary_building_prototype = fields.Float('Ancillary Building Prototype Area (m2)')
    ancillary_building_site = fields.Float('Ancillary Building Site Adaptation Area (m2)')
    ancillary_building_total = fields.Float('Ancillary Buildings Total Area (m2)')


    def action_crm_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        # template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        # template = self.env['mail.template'].browse(template_id)
        # if template.lang:
        #     lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'crm.lead',
            'default_res_id': self.ids[0],
            # 'default_use_template': bool(template_id),
            # 'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            "default_partner_ids": self.partner_id.ids,
            'force_email': True,
            'model_description': self.with_context(lang=lang).type,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


    def convert_rfp(self):

        self.type = 'opportunity'
        self.must_lead = True
