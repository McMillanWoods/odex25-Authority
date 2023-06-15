odoo.define('online_tendering.online_tender', function (require) {
    "use strict";
    require('web.dom_ready');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var QWeb = core.qweb;
    $('.subtotal').text("0");
    $('.untax_total').text("0");
    $('.tax_total').text("0");
    $('.price').change(function(event){
        var subtotal = 0;
        var  parent_tr = $(event.currentTarget).parent().parent();
        var old_subtotal = parseInt(parent_tr.children(".subtotal").text())
        subtotal = event.currentTarget.value * parseInt(parent_tr.children(".qty").text())
        var untax_total = Math.abs((parseInt($('.untax_total').text()) - old_subtotal) + subtotal)
        $('.untax_total').text(untax_total)
        var tax_total = untax_total +  (untax_total * parseInt($('#tax').text())/100)
        parent_tr.children(".subtotal").text(subtotal)
        $('.tax_total').text(tax_total)
    });

    $('#tax').change(function(event){
        var untax_total = parseInt($('.untax_total').text())
        var tax_total = untax_total +  untax_total * parseInt($(event.currentTarget).text())/100
        $('.tax_total').text(tax_total)
    })

    
});