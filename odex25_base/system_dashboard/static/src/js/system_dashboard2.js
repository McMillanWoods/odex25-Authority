odoo.define('system_dashboard.dashboard2', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var ajax = require('web.ajax');
var ActionManager = require('web.ActionManager');
var view_registry = require('web.view_registry');
var Widget = require('web.Widget');
var AbstractAction = require('web.AbstractAction'); 

var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;
var functions = [];
window.click_actions = [];
var SystemDashboardView = AbstractAction.extend( {
    template: 'system_dashboard.dashboard_template_2',
    init: function(parent, context) {
        console.log("Hello World !!!");
        this._super(parent, context);
        this.render();
    },
    willStart: function() {
         return $.when(ajax.loadLibs(this), this._super());
    },
    start: function() {
        var self = this;
        return this._super();
    },
    render: function() {
        var super_render = this._super;
        $( ".o_control_panel" ).addClass( "o_hidden" );
        var self = this;
    },
    reload: function () {
        window.location.href = this.href;
    }
});

core.action_registry.add('system_dashboard.dashboard2', SystemDashboardView);
    return SystemDashboardView
});