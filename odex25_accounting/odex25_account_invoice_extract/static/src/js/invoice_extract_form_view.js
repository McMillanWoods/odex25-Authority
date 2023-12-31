odoo.define('odex25_account_invoice_extract.FormView', function (require) {
"use strict";

/**
 * This subview adds features related to OCR on attachments. An attachment
 * in the chatter can be sent to the OCR, which will add boxes per fields on
 * the attachment. Visually, the attachment preview displays boxes that are
 * generated by the OCR, and clicking on the boxes updates the form accordingly.
 * @see odex25_account_invoice_extract.FormRenderer
 */
var InvoiceExtractFormRenderer = require('odex25_account_invoice_extract.FormRenderer');

var FormView = require('web.FormView');
var view_registry = require('web.view_registry');

var InvoiceExtractFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
        Renderer: InvoiceExtractFormRenderer,
    }),
});

view_registry.add('odex25_account_invoice_extract_preview', InvoiceExtractFormView);

return InvoiceExtractFormView;

});
