odoo.define('odex25_web_mobile.Dialog', function (require) {
"use strict";

var Dialog = require('web.Dialog');
var mobileMixins = require('odex25_web_mobile.mixins');

Dialog.include(_.extend({}, mobileMixins.BackButtonEventMixin, {
    /**
     * Ensure that the on_attach_callback is called after the Dialog has been
     * attached to the DOM and opened.
     *
     * @override
     */
    init() {
        this._super(...arguments);
        this._opened = this._opened.then(this.on_attach_callback.bind(this));
    },
    /**
     * As the Dialog is based on Bootstrap's Modal we don't handle ourself when
     * the modal is detached from the DOM and we have to rely on their events
     * to call on_detach_callback.
     * The 'hidden.bs.modal' is triggered when the hidding animation (if any)
     * is finished and the modal is detached from the DOM.
     *
     * @override
     */
    willStart: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self.$modal.on('hidden.bs.modal', self.on_detach_callback.bind(self));
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Close the current dialog on 'backbutton' event.
     *
     * @private
     * @override
     * @param {Event} ev
     */
    _onBackButton: function () {
        this.close();
    },
}));

});
