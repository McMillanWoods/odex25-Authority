odoo.define('odex25_hr_gantt.GanttView', function (require) {
    'use strict';

    const viewRegistry = require('web.view_registry');
    const GanttView = require('odex25_web_gantt.GanttView');
    const HrGanttRenderer = require('odex25_hr_gantt.GanttRenderer');

    const HrGanttView = GanttView.extend({
        config: Object.assign({}, GanttView.prototype.config, {
            Renderer: HrGanttRenderer,
        }),
    });

    viewRegistry.add('odex25_hr_gantt', HrGanttView);
    return HrGanttView;
});
