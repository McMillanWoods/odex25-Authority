from odoo import models, api, _
from odoo.exceptions import ValidationError


class Superset(models.TransientModel):
    _name = 'superset'
    _description = "superset"

    @api.model
    def get_html(self, given_context=None):
        print("----------------------------------------")
        params = self.env['ir.config_parameter'].sudo()
        if not params.get_param('superset.bi_url', default=False):
            raise ValidationError(_("Kindly set bi configuration in general setting"))
        url = params.get_param('superset.bi_url', default='')+"login/?standalone=true"
        user = self.env['res.users'].browse(self._uid)
        if user.superset_uid:
            usr = user.login
            pwd = user.superset_uid.password
        else:
            usr = params.get_param('superset.username', default=False)
            pwd = params.get_param('superset.password', default=False)
        lang = user.lang.split('_')[0]
        lang_url = params.get_param('superset.bi_url', default='')+"lang/"+lang+'?standalone=true'
        result = {'html': """<form id="login" target="frame" method="post" action="%s">
                                <input type="hidden" name="username" value="%s" />
                                <input type="hidden" name="password" value="%s" />
                            </form>

                            <iframe id="frame" name="frame" marginwidth="0" marginheight="0" frameborder="no" style="height:100vh; width:100%%;" allowtransparency="true" src="about:blank"></iframe>
                            document.cookie = 'SameSite=None;';
                            <script type="text/javascript">
                                console.log(document.getElementById('login'))
                                document.getElementById('login').submit();
                                var iframe = document.getElementById('frame');
                                iframe.onload = function() {
                                    if (iframe.src != "%s") {
                                        iframe.src = "%s";
                                    }
                                }
                            </script>""" % (url, usr, pwd, lang_url, lang_url)}
        print("000000000000000000000000000000000000000000000000000000",result)
        return result