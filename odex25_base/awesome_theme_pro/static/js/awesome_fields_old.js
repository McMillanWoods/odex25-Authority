/**
 * change the fields
 */
odoo.define('awesome.basic_fields', function (require) {
    "use strict";
    // TODO: boolean fields widget needs testing to slove issue 
    // var basic_fields = require('web.basic_fields.deprecated')
    // var FieldBoolean = basic_fields.FieldBoolean

    // FieldBoolean.include({
    //     _render: function () {
    //         var $checkbox = this._formatValue(this.value);
    //         this.$input = $checkbox.find('input');
    //         this.$input.prop('disabled', this.mode === 'readonly');
    //         this.$el.addClass($checkbox.attr('class'));
    //         var $wraper = $('<div class="d-flex align-items-center"/>')
    //         $wraper.append($wraper.contents());
    //         console.log($wraper);
    //         this.$el.empty();
    //         $wraper.appendTo(this.$el)
    //     },
    // })

    // return FieldBoolean;
})
