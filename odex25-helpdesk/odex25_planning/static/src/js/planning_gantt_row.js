odoo.define('odex25_planning.PlanningGanttRow', function (require) {
    'use strict';
    const HrGanttRow = require('odex25_hr_gantt.GanttRow');

    const PlanningGanttRow = HrGanttRow.extend({
        template: 'PlanningGanttView.Row'
    });

    return PlanningGanttRow;
});
