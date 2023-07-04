odoo.define('odex25_planning.PlanningGanttView', function (require) {
    'use strict';

    const HrGanttView = require('odex25_hr_gantt.GanttView');
    const PlanningGanttController = require('odex25_planning.PlanningGanttController');
    const PlanningGanttModel = require('odex25_planning.PlanningGanttModel');
    const PlanningGanttRenderer = require('odex25_planning.PlanningGanttRenderer');

    const view_registry = require('web.view_registry');

    const PlanningGanttView = HrGanttView.extend({
        config: Object.assign({}, HrGanttView.prototype.config, {
            Renderer: PlanningGanttRenderer,
            Controller: PlanningGanttController,
            Model: PlanningGanttModel,
        }),
    });

    view_registry.add('planning_gantt', PlanningGanttView);

    return PlanningGanttView;

});
