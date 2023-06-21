odoo.define('odex25_hr_gantt.GanttRenderer', function (require) {
    'use strict';

    const GanttRenderer = require('odex25_web_gantt.GanttRenderer');
    const HrGanttRow = require('odex25_hr_gantt.GanttRow');

    const HrGanttRenderer = GanttRenderer.extend({
        config: Object.assign({}, GanttRenderer.prototype.config, {
            GanttRow: HrGanttRow
        }),
    });

    return HrGanttRenderer;
});
