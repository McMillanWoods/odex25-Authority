odoo.define('web_project.TaskGanttView', function (require) {
'use strict';
var GanttView = require('web_project.GanttView');
var GanttController = require('web_project.GanttController');
var GanttRenderer = require('web_project.GanttRenderer');
var TaskGanttModel = require('web_project.TaskGanttModel');

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