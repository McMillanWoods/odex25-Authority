odoo.define('hr_hierarchical_chart.hierarchical_chart', function (require) {


    var ControlPanelMixin = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var _t = core._t;

    var hrhierarchicalChart = ControlPanelMixin.extend({
        template: "hr_hierarchical_chart.hierarchical_chart_hrs",
        init: function (parent, params) {
            this._super(parent, params);
            this.params = params;
        },
        getTitle() {
        return _t("Confirmation");
    },

        start: function () {
            var self = this;
            var call_data = {
                model: 'hr_hierarchical_chart_model',
                method: "hierarchical_chart_details",
                args: [this.params['context']['model']],
            }
            rpc.query(call_data)
                .then(function (result) {
                    self.cols = result['cols'];
                    self.hr_data = result['all_data'];
                    self.fields_names = result['fields_names'];
                    self.fields_types = result['fields_types'];
                    $('.hr_chart_list').html(QWeb.render('hr_hierarchical_chart.hr_chartList', { widget: self }));
                    $('#basic').simpleTreeTable({
                        expander: $('#expander'),
                        collapser: $('#collapser')
                    });
                });

            return this._super();
        },

    });
    console.log('Registred')
    core.action_registry.add('hr_hierarchical_view', hrhierarchicalChart);
    return hrhierarchicalChart;

});
