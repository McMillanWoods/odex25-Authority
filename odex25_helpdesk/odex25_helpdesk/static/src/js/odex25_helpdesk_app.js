odoo.define('odex25_helpdesk.script', function (require) {
    "use strict";
    
    var ajax = require('web.ajax');

    $(document).ready(function() {

        $('#recurrency').change(get_plan_info);
        $('#date_start').change(get_plan_info);
        $('#month_num').change(get_plan_info);
  
        function get_plan_info(){
            var date_start = $('#date_start').val();
            var plan_id = $('#recurrency').val();
            
            var month_num = $('#month_num').val();

            

            if (plan_id == '') {
                $("#plan_info").html('');
                $("#error_msg").html('');
                $("#allow_submit").val('no');
            } else {  
                var params = {
                    'plan_id': plan_id,
                    'date_start': date_start,
                    'month_num': month_num,
                }
                ajax.jsonRpc('/helpdesk_plan/manipulate', 'call', params).then(function(result){
                    var plan_info = result['plan_info'];
                    var error_msg = result['error_msg'];
                    $("#plan_info").html(plan_info);
                    $("#error_msg").html(error_msg);
                    if (error_msg != '') {
                        $('#error_msg').addClass('alert alert-danger');
                        $('#plan_info').removeClass('alert alert-info');
                        $("#allow_submit").val('no');
                    } else {
                        $("#error_msg").removeClass('alert alert-danger');
                        $('#plan_info').addClass('alert alert-info');
                        $("#allow_submit").val('yes');
                    }
                });
                
            }
            // End Function
        }

        //option 1
        $("#create_support_account_form").submit(function(e){
            get_plan_info();
            var allowSubmit = $("#allow_submit").val();
            if (allowSubmit != 'yes')
                e.preventDefault()
        });

        //option 2
        $("#create_support_subscription_form").submit(function(e){
            get_plan_info();
            var allowSubmit = $("#allow_submit").val();
            if (allowSubmit != 'yes')
                e.preventDefault()
        });


    });


});
