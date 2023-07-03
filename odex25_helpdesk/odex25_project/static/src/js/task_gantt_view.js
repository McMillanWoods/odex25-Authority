odoo.define('odex25_project.TaskGanttView', function (require) {
'use strict';
var GanttView = require('odex25_web_gantt.GanttView');
var GanttController = require('odex25_web_gantt.GanttController');
var GanttRenderer = require('odex25_web_gantt.GanttRenderer');
var TaskGanttModel = require('odex25_project.TaskGanttModel');

var view_registry = require('web.view_registry');

var TaskGanttView = GanttView.extend({
    config: _.extend({}, GanttView.prototype.config, {
        Controller: GanttController,
        Renderer: GanttRenderer,
        Model: TaskGanttModel,
    }),
});

view_registry.add('task_gantt', TaskGanttView);
return TaskGanttView;
});