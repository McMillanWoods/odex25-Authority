odoo.define('DynamicReject', function (require) {
"use strict";
    var FormRenderer = require('web.FormRenderer');

    FormRenderer.include({
        willStart: function () {
            var self = this;
            self.buttons = []
            var def = this._rpc({
                model: 'reject.workflow',
                method: 'check_reject_workflow',
                args: [this.state.model],
                kwargs: {'model': this.state.model},
            }).then(function (result) {
                self.buttons = result;
            });
            return $.when(def,this._super.apply(this, arguments));
        },
        _renderHeaderButton:function(node){
            var self = this;
            _.each(this.buttons, function (button) {
                var attrs_invisible = (JSON.stringify(node.attrs.modifiers.invisible)).replace(/[^A-Z0-9]+/ig, "");;
                var invisible = (button.invisible).replace(/[^A-Z0-9]+/ig, "");;
                if (button.name == node.attrs.name && button.string == node.attrs.string
                && button.states == node.attrs.states && attrs_invisible == invisible
                ) {
                    node.attrs.context = {'record_reject_name':node.attrs.name};
                    node.attrs.name = 'action_reject_workflow';
                    console.log(node);
                }
            });
            return this._super.apply(this, arguments)
        },
    });
});
