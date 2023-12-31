odoo.define('odex25_website_helpdesk_form.form', function (require) {
'use strict';

var core = require('web.core');
var FormEditorRegistry = require('website_form.form_editor_registry');

var _t = core._t;

FormEditorRegistry.add('create_ticket', {
    formFields: [{
        type: 'char',
        required: true,
        name: 'partner_name',
        string: 'Your Name',
    }, {
        type: 'email',
        required: true,
        name: 'partner_email',
        string: 'Your Email',
    }, {
        type: 'char',
        modelRequired: true,
        name: 'name',
        string: 'Subject',
    }, {
        type: 'char',
        name: 'description',
        string: 'Description',
    }, {
        type: 'binary',
        custom: true,
        name: 'Attachment',
    }],
    fields: [{
        name: 'team_id',
        type: 'many2one',
        relation: 'odex25_helpdesk.team',
        string: _t('Helpdesk Team'),
    }],
    successPage: '/your-ticket-has-been-submitted',
});

});
