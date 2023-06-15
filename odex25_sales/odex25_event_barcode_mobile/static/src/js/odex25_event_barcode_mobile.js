odoo.define('web.event.barcode_mobile', function (require) {
"use strict";

const EventBarcodeScanView = require('odex25_event_barcode.EventScanView');
const barcodeMobileMixin = require('odex25_web_mobile.barcode_mobile_mixin');

EventBarcodeScanView.include(Object.assign({}, barcodeMobileMixin, {
    events: Object.assign({}, barcodeMobileMixin.events, EventBarcodeScanView.prototype.events)
}));
});
