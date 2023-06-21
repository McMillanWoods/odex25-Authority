odoo.define('odex25_timesheet_grid.TimerGridView', function (require) {
    "use strict";

    const viewRegistry = require('web.view_registry');
    const WebGridView = require('odex25_web_grid.GridView');
    const TimerGridController = require('odex25_timesheet_grid.TimerGridController');
    const TimerGridModel = require('odex25_timesheet_grid.TimerGridModel');
    const GridRenderer = require('odex25_timesheet_grid.TimerGridRenderer');
    const TimesheetConfigQRCodeMixin = require('odex25_timesheet_grid.TimesheetConfigQRCodeMixin');
    const { onMounted, onPatched } = owl.hooks;

    class TimerGridRenderer extends GridRenderer {
        constructor() {
            super(...arguments);
            onMounted(() => this._bindPlayStoreIcon());
            onPatched(() => this._bindPlayStoreIcon());
        }
    }

    // QRCode mixin to bind event on play store icon
    Object.assign(TimerGridRenderer.prototype, TimesheetConfigQRCodeMixin);

    const TimerGridView = WebGridView.extend({
        config: Object.assign({}, WebGridView.prototype.config, {
            Model: TimerGridModel,
            Controller: TimerGridController,
            Renderer: TimerGridRenderer
        })
    });

    viewRegistry.add('timesheet_timer_grid', TimerGridView);

    return TimerGridView;
});
