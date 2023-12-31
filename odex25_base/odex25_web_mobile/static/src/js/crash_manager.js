odoo.define('odex25_web_mobile.CrashManager', function (require) {
"use strict";

var CrashManager = require('web.CrashManager').CrashManager;

const mobile = require('odex25_web_mobile.core');

CrashManager.include({
    /**
     * @override
     */
    rpc_error: function (error) {
        if (mobile.methods.crashManager) {
            mobile.methods.crashManager(error);
        }
        return this._super.apply(this, arguments);
    },
});

});
