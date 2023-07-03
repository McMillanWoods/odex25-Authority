# -*- coding: utf-8 -*-
import logging
import werkzeug
import basehash

from datetime import timedelta
from odoo import http, fields, _
from odoo.http import request

from odoo.exceptions import UserError, ValidationError,Warning

_logger = logging.getLogger(__name__)


class WebsiteHelpdesk(http.Controller):

    def get_helpdesk_team_data(self, team, search=None):
        return {'team': team}

    def _get_partner_data(self):
        partner = request.env.user.partner_id
        partner_values = {}
        if partner != request.website.user_id.sudo().partner_id:
            partner_values['name'] = partner.name
            partner_values['email'] = partner.email
        return partner_values

    @http.route(['/odex25_helpdesk/', '/odex25_helpdesk/<model("odex25_helpdesk.team"):team>'], type='http', auth="public", website=True, sitemap=True)
    def odex25_website_helpdesk_teams(self, team=None, **kwargs):
        search = kwargs.get('search')
        # For breadcrumb index: get all team
        # portal_user_id
        teams = None
        # print(request.env.user.is_customer_support)
        # if not request.env.user.has_group('odex25_helpdesk.group_helpdesk_manager'):
        #     teams = request.env['odex25_helpdesk.team'].search(['|', '|', ('use_website_helpdesk_form', '=', True), ('use_website_helpdesk_forum', '=', True), ('use_website_helpdesk_slides', '=', True)], order="id asc")
        #     teams = teams.filtered(lambda team: team.website_published)

        teams_not_subscribed = None
        teams_appended = None
        if request.env.user.id: #.is_customer_support
            teams = request.env['odex25_helpdesk.team'].search([('portal_user_id', '=', request.env.user.id)], order="id asc")
            # print("teams", teams) #website_published
            # '|',('fully_paid', '=', False),'&',
            teams_not_subscribed = request.env['odex25_helpdesk.team'].search([('portal_user_id', '=', request.env.user.id), ('subscription_id', '=', False)], order="id asc")
            teams_appended = request.env['odex25_helpdesk.team'].search([('portal_user_id', '=', request.env.user.id), ('subscription_id', '!=', False)], order="id asc")
            teams_appended = teams_appended.filtered(lambda team: not team.fully_paid)
            teams = teams.filtered(lambda team: (team.fully_paid and team.sub_status == 'open') or team.is_trial)

        if not teams:
            result = {}
            result['teams_not_subscribed'] = teams_not_subscribed
            result['teams_appended'] = teams_appended
            return request.render("odex25_website_helpdesk.not_published_any_team", result)

        result = self.get_helpdesk_team_data(team or teams[0], search=search)
        # For breadcrumb index: get all team
        result['teams'] = teams
        result['teams_not_subscribed'] = teams_not_subscribed
        result['teams_appended'] = teams_appended
        result['default_partner_values'] = self._get_partner_data()
        return request.render("odex25_website_helpdesk.team", result)


class CustomerSupportAccount(http.Controller):
    @http.route(['/helpdesk/create_support_account'], methods=['POST'], type='http', auth="public", website=True)
    def helpdesk_create_support_account(self, **kw):
        msg = {}
        ref_id = kw.get('ref_id', False)
        ref_email = kw.get('ref_email', False)
        email = kw.get('username', False)
        password1 = kw.get('password1', False)
        password2 = kw.get('password2', False)
        
        plan_id = kw.get('recurrency', False)
        date_start = kw.get('date_start', False)
        date_end = kw.get('date_end', False)

        sub_id = kw.get('sub_id', False)
        month_num = kw.get('month_num', False)
        try:
            month_num = int(month_num)
            date_start = fields.Date.from_string(date_start)
            date_end = date_start + timedelta(days= (month_num * 30))
        except Exception as e:
            month_num = 0

        values = {
            'name': kw.get('fullname', False),
            'login': email,
            'phone': kw.get('phone', False),
            'password': password1,
            'is_customer_support': True,
            'password': password1,
        }

        if not values:
            msg['error'] = _("The form was not properly filled in.")
            return request.render('odex25_website_helpdesk.error_support_account', msg)

        if ref_email != email:
            print('ref_email', ref_email)
            print('email', email)
            msg['error'] = _("Invalid email")
            return request.render('odex25_website_helpdesk.error_support_account', msg)

        if password1 != password2:
            msg['error'] = _("Passwords do not match; please retype them.")
            return request.render('odex25_website_helpdesk.error_support_account', msg)

        subscription_id = False
        if sub_id:
            subscription_id = request.env['subscription.service'].sudo().search([
            ('id', '=', sub_id),
        ], limit=1)

        # Plan
        if not subscription_id:
            plan = request.env['helpdesk.price'].sudo().search([('id', '=', plan_id),('is_active', '=', True)])
            if not plan:
                msg['error'] = _("No plan")
                return request.render('odex25_website_helpdesk.error_support_account', msg)

        helpdesk_team = request.env['odex25_helpdesk.team'].sudo().search([
            ('id', '=', ref_id),
        ], limit=1)
        if not helpdesk_team:
            msg['error'] = _("No support for this project")
            return request.render('odex25_website_helpdesk.error_support_account', msg)

        if helpdesk_team.portal_user_id:
            msg['error'] = _("Support account already registered for this project")
            return request.render('odex25_website_helpdesk.error_support_account', msg)
            
        supported_langs = [
            lang["code"]
            for lang in request.env["res.lang"].sudo().search_read([], ["code"])
        ]
        if request.lang in supported_langs:
            values["lang"] = request.lang

        values['partner_id'] = helpdesk_team.partner_id.id
        values['groups_id'] = [(6, 0, [request.env.ref('base.group_portal').id])]

        try:
            user = request.env['res.users'].sudo().with_context(no_reset_password=True).create(values)
            if not subscription_id:
                # Create a subscription
                subscription_id = request.env["subscription.service"].sudo().create({
                    "type": 'sale',
                    "date_start": date_start,
                    "recurring_next_date": date_start,
                    "date_end": date_end,
                    "partner_id": user.partner_id.id,
                    "recurrency": 'monthly',
                    "recurring_interval": 1,
                    "currency_id": user.sudo().company_id.currency_id.id or request.env.ref('base.main_company').sudo().currency_id.id,
                })
                print("subscription_id", subscription_id)

                # Create product #template
                product_id = request.env["product.product"].sudo().create({
                    'name': helpdesk_team.name,
                    "default_code": subscription_id.code,
                    "list_price": plan.amount,
                    "type": "service",
                    "description": subscription_id.display_name,
                    "so_subscription": True,
                })
                print("product_id", product_id)

                # Create a subscription
                subscription_lines = request.env["subscription.service.line"].sudo().create({
                    'subscription_serv_id': subscription_id.id,
                    "name": plan.name + ' - ' + helpdesk_team.name,
                    "product_id": product_id.id,
                    "qty": 1,
                    "unit_price": plan.amount,
                    'sub_line_tax_ids': [(6, 0 , plan.tax_id.ids)],
                })
                print("subscription_lines", subscription_lines)

        except Exception as e:
            msg['error'] = str(e)
            return request.render('odex25_website_helpdesk.error_support_account', msg)

        if helpdesk_team:
            helpdesk_team.sudo().write({
                    'portal_user_id': user.id,
                })

        if subscription_id:
            # Update Helpdesk
            helpdesk_team.sudo().write({
                'subscription_id': subscription_id.id,
            })
            print("subscription_id month", subscription_id.sudo().month_num)
            subscription_id.sudo()._compute_days_period()
            print("subscription_id month", subscription_id.sudo().month_num)
            subscription_id.sudo().set_open()
        # return http.redirect_with_hash('/web/login')
        # return http.redirect_with_hash('/my')
        # return http.redirect_with_hash('/odex25_helpdesk')
        return request.render('odex25_website_helpdesk.success_support_account')

    # For Validate
    @http.route(['/support_account/<string:token>'], type='http', auth="public",website=True)
    def post_support_account(self, token, **kw):
        unhashed_id = False
        msg = {}
        try:
            hash_fn = basehash.base36()  # you can initialize a 36, 52, 56, 58, 62 and 94 base fn
            # hash_value = hash_fn.hash(6) # returns 'M8YZRZ' PHTYNU
            unhashed_id = hash_fn.unhash(token) # returns 1
            # return request.not_found()
            # return request.render('website.404') in v11
        except Exception as e:
            return request.render('website.page_404')
        
        if not unhashed_id:
            return request.render('website.page_404')

        helpdesk = request.env['odex25_helpdesk.team'].sudo().search([('id', '=', unhashed_id),], limit=1)
        if not helpdesk:
            return request.render('website.page_404')

        if helpdesk.portal_user_id:
            msg['error'] = _("Support account already registered for this project")
            return request.render('odex25_website_helpdesk.error_support_account', msg)


        helpdesk_prices = request.env['helpdesk.price'].sudo().search([('is_active', '=', True),])             
        # recurrency_list = [('daily', 'Day(s)'), ('weekly', 'Week(s)'), ('monthly', 'Month(s)'), ('yearly', 'Year(s)')]
        
        recurrency_list = []
        for price in helpdesk_prices:
            recurrency_list.append((price.id, price.name))

        subscription = helpdesk.subscription_id
        is_sub = False
        if subscription:
            is_sub = True
        print("subscription", subscription)
        values = {
            'obj_id': helpdesk.id,
            'name': helpdesk.name,
            'docs': helpdesk_prices,
            'is_sub': is_sub,
            'subscription': subscription,
            'recurrency_list': recurrency_list,
            'obj_email': helpdesk.partner_id.email,
            'obj_name': helpdesk.partner_id.name,
            'description': helpdesk.description,
        }

        # print("values", values)
        # print("token", token)
        # print("unhashed_id", unhashed_id)
        return request.render("odex25_website_helpdesk.support_account_form",values)

    @http.route(['/helpdesk_plan/manipulate'], type='json', auth="public", website=True)
    def helpdesk_plan_manipulate(self, **arg):
        date_start = arg.get('date_start', False)
        month_num = arg.get('month_num', False)
        try:
            month_num = int(month_num)
        except Exception as e:
            month_num = 0
        
        plan_id = arg.get('plan_id', False);
        msg = ''
        plan_scale = ''
        plan_duration = ''
        plan_info = ''
        amount = 0
        total = 0
        days_period = 0
        date_end = None
        if plan_id and date_start and month_num >0:
            days_period = (month_num * 30)
            date_start = fields.Date.from_string(date_start)
            date_end = date_start + timedelta(days= days_period)
            days_period = days_period

        else:
            msg = _("Both start date and month number are required")
        
            # if plan_id:
            # if date_end <= date_start:
            #     msg = _("End date should be greater than start date")
            #     days_period = 0
            # else:
            #     days_period = int(abs((date_end - date_start).days))


            # if helpdesk_price.recurrency == "daily" and days_period < 1:
            #     msg = _("Check the dates, subscription should at least one day.")
            # elif helpdesk_price.recurrency == "weekly" and days_period < 7:
            #     msg = _("Check the dates, subscription should at least one week.")
            # elif helpdesk_price.recurrency == "monthly" and days_period < 30:
            #     msg = _("Check the dates, subscription should at least one month.")
            # elif helpdesk_price.recurrency == "yearly" and days_period < 365:
            #     msg = _("Check the dates, subscription should at least one year.")

        if not msg:
            helpdesk_price = request.env['helpdesk.price'].sudo().search([('id', '=', plan_id),], limit=1)
            # total = helpdesk_price.amount * days_period
            amount = helpdesk_price.amount + helpdesk_price.tax_amount
            plan_duration = _("Your plan is") + ' {} '.format(int(month_num)) + _("months.")
            plan_scale = _("You will pay amount of ") + ' {} '.format(amount) + _("SAR on every month, the total amount will be") + ' {} '.format(month_num * amount) + _("SAR.") + " " +_("Plan end date will be") + ' {} .'.format(date_end.strftime('%d %B %Y'))
            plan_info = plan_duration + plan_scale  #+ _("Total amount is") + ' {} '.format(total) + _("SAR.")

        res = {
         'plan_info': plan_info,
         'error_msg': msg,
        }

        return res

    # For support subscription
    @http.route(['/support_subscription/<int:team_id>'], type='http', auth="public",website=True)
    def post_support_subscription(self, team_id, **kw):
        msg = {}
        try:
            team_id = int(team_id)
        except Exception as e:
            return request.render('website.page_404')
        
        if not team_id:
            return request.render('website.page_404')

        helpdesk = request.env['odex25_helpdesk.team'].sudo().search([('id', '=', team_id),], limit=1)
        if not helpdesk:
            return request.render('website.page_404')

        if helpdesk.subscription_id:
            msg['error'] = _("The project already has a subscription")
            return request.render('odex25_website_helpdesk.error_support_account', msg)


        helpdesk_prices = request.env['helpdesk.price'].sudo().search([('is_active', '=', True),])             
   
        recurrency_list = []
        for price in helpdesk_prices:
            recurrency_list.append((price.id, price.name))

        values = {
            'obj_id': helpdesk.id,
            'name': helpdesk.name,
            'docs': helpdesk_prices,
            'recurrency_list': recurrency_list,
            'obj_email': helpdesk.partner_id.email,
            'obj_name': helpdesk.partner_id.name,
            'description': helpdesk.description,
        }

        print("values", values)
        return request.render("odex25_website_helpdesk.support_subscription_form",values)

    # Added
    @http.route(['/helpdesk/create_support_subscription'], methods=['POST'], type='http', auth="public", website=True)
    def helpdesk_create_support_subscription(self, **kw):
        msg = {}
        ref_id = kw.get('ref_id', False)
        
        plan_id = kw.get('recurrency', False)
        date_start = kw.get('date_start', False)
        month_num = kw.get('month_num', 0)
        month_num = int(month_num)
        date_start = fields.Date.from_string(date_start)
        date_end = date_start + timedelta(days= (month_num * 30))

        # Plan
        plan = request.env['helpdesk.price'].sudo().search([('id', '=', plan_id),('is_active', '=', True)])
        if not plan:
            msg['error'] = _("No plan")
            return request.render('odex25_website_helpdesk.error_support_account', msg)

        helpdesk_team = request.env['odex25_helpdesk.team'].sudo().search([
            ('id', '=', ref_id),
        ], limit=1)
        if not helpdesk_team:
            msg['error'] = _("No support for this project")
            return request.render('odex25_website_helpdesk.error_support_account', msg)

        if helpdesk_team.subscription_id:
            msg['error'] = _("The project already has a subscription")
            return request.render('odex25_website_helpdesk.error_support_account', msg)
            
        if not helpdesk_team.portal_user_id:
            msg['error'] = _("No support account registered for this project")
            return request.render('odex25_website_helpdesk.error_support_account', msg)
        
        subscription_id = False
        user = helpdesk_team.sudo().portal_user_id
        try:
            # Create a subscription
            subscription_id = request.env["subscription.service"].sudo().create({
                "type": 'sale',
                "date_start": date_start,
                "recurring_next_date": date_start,
                "date_end": date_end,
                "month_num": month_num,
                "partner_id": user.partner_id.id,
                "recurrency": 'monthly',
                "recurring_interval": 1,
                "currency_id": user.company_id.currency_id.id or request.env.ref('base.main_company').sudo().currency_id.id,
            })
            print("subscription_id", subscription_id)

            # Create product #template
            product_id = request.env["product.product"].sudo().create({
                'name': helpdesk_team.name,
                "default_code": subscription_id.code,
                "list_price": plan.amount,
                "type": "service",
                "description": subscription_id.display_name,
                "so_subscription": True,
            })
            print("product_id", product_id)

            # Create a subscription
            subscription_lines = request.env["subscription.service.line"].sudo().create({
                'subscription_serv_id': subscription_id.id,
                "name": plan.name + ' - ' + helpdesk_team.name,
                "product_id": product_id.id,
                "qty": 1,
                "unit_price": plan.amount,
                'sub_line_tax_ids': [(6, 0 , plan.tax_id.ids)],
            })
            print("subscription_lines", subscription_lines)
            
        except Exception as e:
            msg['error'] = str(e)
            return request.render('odex25_website_helpdesk.error_support_account', msg)

        
        if subscription_id:
            # Update Helpdesk
            helpdesk_team.sudo().write({
                'subscription_id': subscription_id.id,
            })
            print("subscription_id month", subscription_id.sudo().month_num)
            subscription_id.sudo()._compute_days_period()
            print("subscription_id month", subscription_id.sudo().month_num)
            subscription_id.sudo().set_open()

            return http.redirect_with_hash('/my/subscriptions/{}'.format(subscription_id.id))
        return http.redirect_with_hash('/my')
