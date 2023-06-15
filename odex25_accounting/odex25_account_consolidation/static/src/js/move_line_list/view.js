odoo.define('odex25_account_consolidation.MLListView', function (require) {
    "use strict";

    var ParentListView = require('odex25_account_accountant.MoveLineListView').AccountMoveListView;
    var viewRegistry = require('web.view_registry');
    var MLListRenderer = require('odex25_account_consolidation.MLListRenderer');

    var MLListView = ParentListView.extend({
        config: _.extend({}, ParentListView.prototype.config, {
            Renderer: MLListRenderer
        })
    });

    viewRegistry.add('consolidation_move_line_list', MLListView);

    return MLListView;
});
