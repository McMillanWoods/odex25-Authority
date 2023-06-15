odoo.define('odex_bi.superset_backend', function (require) {
'use strict';

var core = require('web.core');
var Widget = require('web.Widget');
const AbstractAction = require('web.AbstractAction');  
var ReportWidget = require('odex_bi.superset_widget');

var _t = core._t;

var report_backend = AbstractAction.extend({
    // Stores all the parameters of the action.

    init: function(parent, action) {
        this.actionManager = parent;
        this.given_context = {};
        this.odoo_context = action.context;
        this.controller_url = action.context.url;
        if (action.context.context) {
            this.given_context = action.context.context;
        }
        this.given_context.active_id = action.context.active_id || action.params.active_id;
        this.given_context.model = action.context.active_model || false;
        this.given_context.ttype = action.context.ttype || false;
        return this._super.apply(this, arguments);
    },
    willStart: function() {
        return $.when(this.get_html());
    },
    on_attach_callback() {
        return { };
    },

    on_detach_callback() {
        return { };
    },

    canBeRemoved: function () {
            return Promise.resolve();
    },

    getState: function() {
        return { };
    },
    getTitle: function() {
        return _t('BI');
    },
    set_html: function() {
        var self = this;
        var def = $.when();
        if (!this.report_widget) {
            this.report_widget = new ReportWidget(this, this.given_context);
            def = this.report_widget.appendTo(this.$el);
        }
        def.then(function () {
            self.report_widget.$el.html(self.html);
        });
    },
    start: function() {
        this.set_html();
        return this._super();
    },
    // Fetches the html and is previous report.context if any, else create it
    get_html: function() {
        var self = this;
        var defs = [];
        return this._rpc({
                model: this.given_context.model,
                method: 'get_html',
                args: [self.given_context],
                context: self.odoo_context,
            })
            .then(function (result) {
                self.html = result.html;
                defs.push(self.update_cp());
                return $.when.apply($, defs);
            });
    },
    // // Updates the control panel and render the elements that have yet to be rendered
    update_cp: function() {
        if (this.$buttons) {
            var status = {
                    breadcrumbs: self.action_manager.get_breadcrumbs(),
                    cp_content: {$buttons: self.$buttons},
                };
            return self.updateControlPanel(status);
        }
    },
    do_show: function() {
        this._super();
        this.upupdate_cpdate_cp();
    },
});

core.action_registry.add("superset_backend", report_backend);
return report_backend;
});
