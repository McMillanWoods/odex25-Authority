odoo.define('odex25_timesheet_grid.GridView', function (require) {
    "use strict";

    const viewRegistry = require('web.view_registry');
    const WebGridView = require('odex25_web_grid.GridView');
    const TimesheetConfigQRCodeMixin = require('odex25_timesheet_grid.TimesheetConfigQRCodeMixin');
    const TimesheetGridController = require('odex25_timesheet_grid.GridController');
    const TimesheetGridModel = require('odex25_timesheet_grid.GridModel');
    const GridRenderer = require('odex25_timesheet_grid.GridRenderer');
    const { onMounted, onPatched } = owl.hooks;

    class TimesheetGridRenderer extends GridRenderer {
        constructor() {
            super(...arguments);
            onMounted(() => this._bindPlayStoreIcon());
            onPatched(() => this._bindPlayStoreIcon());
        }
    }

    // QRCode mixin to bind event on play store icon
    Object.assign(TimesheetGridRenderer.prototype, TimesheetConfigQRCodeMixin);

    // JS class to avoid grouping by date
    const TimesheetGridView = WebGridView.extend({
        config: Object.assign({}, WebGridView.prototype.config, {
            Model: TimesheetGridModel,
            Controller: TimesheetGridController,
            Renderer: TimesheetGridRenderer
        })
    });

    viewRegistry.add('odex25_timesheet_grid', TimesheetGridView);

    return TimesheetGridView;
});
