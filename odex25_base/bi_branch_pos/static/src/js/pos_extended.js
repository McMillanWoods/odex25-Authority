odoo.define('bi_branch_pos.pos_extended', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');

    

    var QWeb = core.qweb;
    var _t = core._t;

    var _super_posmodel = models.PosModel.prototype;


    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var session_model = _.find(this.models, function(model){ return model.model === 'pos.session'; });
            session_model.fields.push('branch_id','addres','telephone');
            return _super_posmodel.initialize.call(this, session, attributes);
        },

    });
});

