odoo.define('exp_late_mail_reminder.notification_popup', function (require) {
    "use strict";
//this file migrate from odoo9 to 11 written by altaher migrate by fatima 18/5/2020
var core = require('web.core');
var ajax = require('web.ajax');
var QWeb = core.qweb;
var rpc = require('web.rpc');
var ActionManager = require('web.ActionManager');
var Widget = require('web.Widget');
var ControlPanelMixin = require('web.ControlPanelMixin');
//
    function save_hashing(url) {
        var _id = '';
        var p1 = /&action=\d+/g;
        var record_id = url.match(p1);
        if (record_id) {
            _id = record_id[0].match(/\d+\d*/g)[0];
            try {
                var h = $.md5(_id.toString(), (new Date()).getFullYear().toString());
                localStorage.setItem("navigator_token", h);
                localStorage.setItem("navigator_token_act", _id);
            }
            catch (err) {

            }
        }
    }

    function save_hashing_record(url) {
        var rec = '';

        try {
            var p1 = /#id=\d+/g;
            var record_id = url.match(p1);
            if (record_id) {
                rec = record_id[0].match(/\d+\d*/g)[0];
                var h = $.md5((new Date()).getFullYear().toString(), rec.toString());
                localStorage.setItem("record_token", h);
                localStorage.setItem("origin_record_id", rec);
            }
        }
        catch (err) {
        }
    }
    $(document).ready(function () {
        function dragElement(elmnt) {
            var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
            if (document.getElementById(elmnt.id + "header")) {
                /* if present, the header is where you move the DIV from:*/
                document.getElementById(elmnt.id + "header").onmousedown = dragMouseDown;
            } else {
                /* otherwise, move the DIV from anywhere inside the DIV:*/
                elmnt.onmousedown = dragMouseDown;
            }

            function dragMouseDown(e) {
                e = e || window.event;
                e.preventDefault();
                // get the mouse cursor position at startup:
                pos3 = e.clientX;
                pos4 = e.clientY;
                document.onmouseup = closeDragElement;
                // call a function whenever the cursor moves:
                document.onmousemove = elementDrag;
            }

            function elementDrag(e) {
                e = e || window.event;
                e.preventDefault();
                // calculate the new cursor position:
                pos1 = pos3 - e.clientX;
                pos2 = pos4 - e.clientY;
                pos3 = e.clientX;
                pos4 = e.clientY;
                // set the element's new position:
                elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
                elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
            }

            function closeDragElement() {
                /* stop moving when mouse button is released:*/
                document.onmouseup = null;
                document.onmousemove = null;
            }
        }
        function load_message_loader() {
            return ajax.jsonRpc('/reminder/notifications', 'call', {})
                .then(function (results) {
                    if (results.length > 0) {
                        var content = '';
                        var no_message = results.length
                        $('body').append('<div class="notifier-container"><h2 style="color:#204060;">التنبيهات</h2><div class="col-md-12 notifier-body"></div></div>');
                        $('body').append('<div class="notifier-overlayer"></div>');
                        $('body').append('<div class="notifier-button style="dir:ltr"><div class="containers"><div class="rectangle"><div class="notification-text"><span><strong>لديك رسائل جديدة</span><span class="badge" id="badge">'+ no_message+'</span></strong></div></div></div></div>');
                        _.each(results, function (item) {
                            $('.notifier-body').append('<div data-id='+ item['id']+' class="alert alert-warning"><ul class="list-unstyled"><li><a href="'+item['base_url']+'/web#id='+ item['res_id']+'&view_type=form&model='+item['res_model']+'&action='+item['action_id'] +'">'+'<p style="color : white;"> '+item['subject'] +'</p></a></li></ul></div>');
                        });
                        var alert = document.querySelectorAll('.alert')
                        $(alert).click(function (event) {
                            var id = $(event.currentTarget).data('id');
                            var MessageModel = rpc.query({
                                        model: 'mail.message',
                                        method: 'mark_all_as_read',
                                                     args:[[],[['id','=',id]]]
                                         }).then(
                                        function () {
                                            $(event.currentTarget).hide();
                                            no_message = no_message - 1;
                                            $('#badge').text(no_message);
                                            $(".notifier-overlayer").fadeOut();
                                            $(".notifier-container").css({"transform":"translateX(400px)"});
                                            if(no_message > 0){
                                                $(".rectangle-text").addClass("animate");
                                                $(".rectangle").addClass("animate");
                                                $(".notifier-button").css({"bottom":"20px"});

                                            }
                                    }
                                );
                            console.log(id);
                        });
                        $(".rectangle").click(function(){
                            $(".notifier-overlayer").show();
                            $(".notifier-container").css({"transform":"translateX(0)"});
                            $(".notifier-button").css({"bottom":"-100px"});
                            $(".rectangle-text").removeClass("animate");
                            $(".rectangle").removeClass("animate");
                        });
                        $(".notifier-overlayer").click(function(){
                            $(".notifier-overlayer").fadeOut();
                            $(".notifier-container").css({"transform":"translateX(400px)"});
                            $(".rectangle-text").addClass("animate");
                            $(".rectangle").addClass("animate");
                            $(".notifier-button").css({"bottom":"20px"});
                        });

                        $(".rectangle-text").addClass("animate");
                        $(".rectangle").addClass("animate");
                        $(".notifier-button").css({"bottom":"20px"});
                    }
                });
        }

        setTimeout(load_message_loader, 2000);
    });

});
