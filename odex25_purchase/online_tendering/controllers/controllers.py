# -*- coding: utf-8 -*-
import logging
import werkzeug
import re
import base64
from odoo import http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request
from datetime import datetime
from odoo.addons.auth_signup import controllers
from odoo.addons.web.controllers.main import ensure_db, Home, SIGN_UP_REQUEST_PARAMS
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.addons.auth_signup.models.res_users import SignupError

_logger = logging.getLogger(__name__)

SIGN_UP_REQUEST_PARAMS.update({'company_represent', 'vat', 'phone', 'mobile', 'street', 
                                'commercial_register', 'company_type','city','activity_type','documents_ids'})


class main(http.Controller):
    @http.route(["/tenders"], type="http", auth="public", website=True)
    def tenders_get(self, request):
        requisition = request.env["purchase.requisition"]
        tenders = requisition.sudo().browse(requisition.sudo().search([('published_in_portal' , '=' , True),('available_until' , '>=' , datetime.today()),('state' , '=' , 'in_progress')]).ids)

        return request.render(
            "online_tendering.index", {"message": "Open Tenders", "tenders": tenders,}
        )


    @http.route(
        '/tender/details/',
        type="http",
        auth="public",
        website=True,
        csrf=False
    )
    def show_tender_details(self, tender_id):
        return request.render("online_tendering.tender_details", {"tender": request.env['purchase.requisition'].sudo().search([('id' , '=' , tender_id)])})

        
    @http.route(
        '/tenders/apply/',
        type="http",
        auth="user",
        website=True,
        csrf=False
    )
    def show_tender_apply(self, tender_id):
        tax_ids = request.env['account.tax'].sudo().search([('type_tax_use' , '=' , "purchase")])
        return request.render("online_tendering.tender_apply", {"tender": request.env['purchase.requisition'].sudo().search([('id' , '=' , tender_id)]) , 'taxs' :tax_ids })

    @http.route(
        ["/Application_result"],
        type="http",
        # methods=["POST","GET"],
        auth="public",
        website=True,
    )
    def portal_chatter_post(self,**kw):
        #print("KKKKKKKKKKKKKK", kw)
        error = False
        _list = {}
        # tender_id = kw['tender_id']
        for k, val in kw.items():
            if k.find("-price") > 0:
                new_k = k.replace("-price", "")
                _list[new_k] = _list.get(new_k, {})
                _list[new_k]["price"] = val
        if kw:
            _list['tender_id'] = kw['tender_id']
            _list['tax'] = kw['tax']
            _list['vendor_note'] = kw['vendor_note']
        else:
            _list['tender_id'] = False
            _list['vendor_note'] = False
        # url = request.httprequest.referrer
        application = self.tender_application_create(_list)
        if not application:
            error = 'You have already applied for this tender'
        else:
            if kw.get('attachment' , False):
                Attachments = request.env['ir.attachment']
                name = kw.get('attachment').filename  
                file = kw.get('attachment')
                attachment = file.read() 
                attachment_id = Attachments.sudo().create({
                    'name':name,
                    'res_name': name,
                    'type': 'binary',   
                    'res_model': 'tender.application',
                    'res_id': application.id,
                    'datas': base64.b64encode(attachment),
                })
                application.attachment_id = attachment_id.id
        return request.render('online_tendering.user_applications' , {
            'error' : error,
            'applications' : application
        })
        
    def tender_application_create(self, dict):
        print()
        application_obj = request.env['tender.application']
        tender = request.env['purchase.requisition'].sudo().search([('id' , '=' , dict['tender_id'])])
        application = application_obj.sudo().search([('tender_id' , '=' ,tender.id ) , ('user_id' , '=' , request.env.user.id)])
        if application:
            return False
        else:
            application_lines = []
            for tender_line in tender.line_ids:
                application_lines += [(0,6,{
                    'product_id': tender_line.product_id.id,
                    'product_uom_id' : tender_line.product_uom_id.id,
                    'product_qty' : tender_line.product_qty,
                    'price_unit' : dict[str(tender_line.product_id.id)]['price'],
                    'schedule_date' : tender_line.schedule_date,
                    'tax_id': int(dict['tax']),
                })]
            application = application_obj.sudo().create({
            'date' : datetime.today(),
            'vendor_note' : dict['vendor_note'],
            'user_id' : request.env.user.id,
            'email' : request.env.user.email,
            'phone' : request.env.user.phone,
            'mobile' : request.env.user.mobile,
            'tender_id' : tender.id,
            'line_ids' : application_lines
            })
            return application

    @http.route(
        ["/tenders/my_applications"],
        type="http",
        methods=["GET"],
        auth="user",
        website=True,
    )
    def get_user_applications(self):
        application_obj = request.env['tender.application']
        applications = application_obj.sudo().search([('user_id' , '=' , request.env.user.id)],order="create_date desc")
        return request.render("online_tendering.user_applications", {"applications": applications })
    #attechment
    @http.route(["/my/account"], methods=['POST'], type='http', auth="public", website=True)
    def get_my_account(self, **kw):
        attachment = kw.get('attachment')
        msg = None
        suc = False
        if attachment and request.env.uid and name_of and amount:
          create_vals = {
              'name': request.env['res.users'].sudo().browse(request.env.uid).name,
              'document_ids': base64.encodestring(attachment.read()),
              # 'filename': attachment.filename,
          }
          print(create_vals)
          new_partner_id = request.env['res.partner'].sudo().create(create_vals)
          msg =  new_partner_id.id
          suc = True
          return http.request.make_response(new_partner_id)

        else:
            msg = _('Problem happened while submitting your request.\n Please Try again later')
            request.session['new_partner_id'] = msg
            request.session['new_partner_id-status'] = suc
            return http.request.make_response(msg)
            # return http.redirect_with_hash('/xxxxxxx')

# from odoo.addons.web.controllers.main import Home
# class HomeExt(Home):
#     @http.route(csrf=False)
#     def authenticate(self, db, login, password, base_location=None):
#         request.session.authenticate(db, login, password)
#         return request.env['ir.http'].session_info()

class CustomUserSignup(controllers.main.AuthSignupHome):
    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def do_signup_fill(self, **kw):
        # , csrf=False
        activity_types = request.env['activity.type'].sudo().search([])
        document_types = request.env['document.type'].sudo().search([])
        return http.request.render('auth_signup.signup', {
            'activity_types': activity_types,
            'document_types': document_types,
            'valid': True,

        })

    @http.route(['/tender_signup'], methods=['POST'], type='http', auth="public", website=True, csrf=False)
    def do_tender_signup(self, **qcontext):
        # print("Hiiii.. Tenders")          
        # print('token >>> ',qcontext.get("token"))
        valid = True

        values = {
            key: qcontext.get(key)
            for key in (
                "login",
                "name",
                "password",
                "street",
                "city",
                "activity_type",
                "phone",
                "mobile",
                "company_represent",
                "vat",
                "commercial_register",
                "company_type",
                # "document",
            )
        }
         
        if not values:
            qcontext['valid'] = False
            qcontext['error'] = _("The form was not properly filled in.")
            return request.render("auth_signup.signup", qcontext)
    
          
        if values.get("password") != qcontext.get("confirm_password"):
            qcontext['valid'] = False
            qcontext['error'] = _("Passwords do not match; please retype them.")
            return request.render("auth_signup.signup", qcontext)
            # raise UserError(_("Passwords do not match; please retype them."))

        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', qcontext.get('login'))
        if match == None:
            qcontext['valid'] = False
            qcontext['error'] = _("Not a valid email address; please correct email.")
            return request.render("auth_signup.signup", qcontext)
        
        try:
            # Prepare Data
            name = qcontext.get('name')
            attachment = qcontext.get('document')
            activity_type = qcontext.get('activity_type')
            document_type = qcontext.get('document_type')
            exp_date = qcontext.get('exp_date')
            mobile = qcontext.get('mobile')
            phone = qcontext.get('phone')
            email = qcontext.get('login')
            password = qcontext.get('password')
            # Prepare Objects
            document_file = attachment.read()

            # Set user values
            partner_values = {
                key: qcontext.get(key)
                for key in (
                    "street",
                    "city",
                    "activity_type",
                    "phone",
                    "mobile",
                    "company_represent",
                    "vat",
                    "commercial_register",
                    "company_type",
                )
            }
            partner_values['email'] = email

            supported_langs = [
                lang["code"]
                for lang in request.env["res.lang"].sudo().search_read([], ["code"])
            ]
            if request.lang in supported_langs:
                values["lang"] = request.lang
            values['supplier_rank'] = 1
            values['groups_id'] = [(6, 0, [request.env.ref('base.group_portal').id])]

            print(values)

            user = request.env['res.users'].sudo().with_context(no_reset_password=True).create(values)

            attached_files = request.httprequest.files.getlist('document')
            for attachment in attached_files:
                attached_file = attachment.read()
                document_id = request.env['partner.document'].sudo().create({
                   'name': attachment.filename,
                    'type_id': document_type,
                    'partner_id':  user.partner_id.id,
                    'exp_date': exp_date,
                    'attachment': base64.encodebytes( attached_file),
                })


            return http.redirect_with_hash('/my')

        except Exception as e:
            qcontext['valid'] = False
            qcontext['error'] = str(e)
            return request.render("auth_signup.signup", qcontext)

              
    
    
