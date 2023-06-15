odoo.define("dms_search_panel_model_extension", function (require) {
    "use strict";
    const ActionModel = require("web/static/src/js/views/action_model.js");
    const SearchPanelModelExtension = require("web/static/src/js/views/search_panel_model_extension.js");
//    alert('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb');

    SearchPanelModelExtension.include({

         _getCategoryDomain(excludedCategoryId) {
            const domain = super._getCategoryDomain(...arguments);
            alert('gggggggggggggggggggggggggggggg')
            console.log(domain,">>>>>>>>>>>>>>")
            return domain

         }
    })

//    ActionModel.registry.add("DmsSearchPanel", DmsSearchPanelModelExtension, );
//
//    return DmsSearchPanelModelExtension;
   });