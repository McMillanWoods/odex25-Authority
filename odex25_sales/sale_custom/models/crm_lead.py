# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    is_won = fields.Boolean(related='stage_id.is_won')

    def action_new_quotation(self):

        action = super(CrmLead, self).action_new_quotation()

        action['context']['default_bidbond'] = self.bidbond
        action['context']['default_proposal_name'] = self.name
        action['context']['default_project_country_id'] = self.project_country_id.id if self.project_country_id else False
        action['context']['default_project_state_id'] = self.project_state_id.id if self.project_state_id else False
        action['context']['default_city_id'] = self.city_id.id if self.city_id else False
        action['context']['default_industry_id'] = self.industry_id.id if self.industry_id else False
        action['context']['default_sector_id'] = self.sector_id.id if self.sector_id else False
        action['context']['default_department_id'] = self.department_id.id if self.department_id else False
        action['context']['default_product_id'] = self.product_id.id if self.product_id else False
        action['context']['default_project_category_id'] = self.project_category_id.id if self.project_category_id else False
        action['context']['default_project_duration'] = self.project_duration
        action['context']['default_project_duration_internal'] = self.project_duration_internal
        action['context']['default_total_site_area'] = self.total_site_area
        action['context']['default_main_building_prototype'] = self.main_building_prototype
        action['context']['default_main_building_site'] = self.main_building_site
        action['context']['default_main_building_total'] = self.main_building_total
        action['context']['default_floor_area_ratio'] = self.floor_area_ratio
        action['context']['default_site_works_area'] = self.site_works_area
        action['context']['default_ancillary_building_prototype'] = self.ancillary_building_prototype
        action['context']['default_ancillary_building_site'] = self.ancillary_building_site
        action['context']['default_ancillary_building_total'] = self.ancillary_building_total

        return action
