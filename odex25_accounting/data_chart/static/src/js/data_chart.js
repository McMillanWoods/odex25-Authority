odoo.define('data_chart.data_chart', function (require) {
    "use strict";

    // var ControlPanelMixin = require('web.ControlPanel');
    var core = require('web.core');
    const AbstractAction = require('web.AbstractAction');  
    var rpc = require('web.rpc');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var _t = core._t;

    var dataChart = AbstractAction.extend({
        hasControlPanel: true,
        contentTemplate: "data_chart_temp",





        init: function (parent, params) {
            this._super(parent, params);
            this.params = params;
            if (this.params['context']['admin_view'] == undefined) {
                $('.o_control_panel').addClass('o_hidden');
            }
        },

        load_data: function (with_default = false) {
            var self = this;
            var call_data = {
                model: 'data_chart_model',
                method: "data_chart_details",
                args: [this.params['context']['model'], this.params['context']["active_id"], with_default],
            }
            rpc.query(call_data)
                .then(function (result) {
                    var data = result['data'];

                    var header = '',
                        footer = '',
                        cols_types;
                    if (result['options'] != undefined) {
                        var options = JSON.parse(result['options']);
                    }
                    if (result['slice'] != undefined) {
                        var slice = JSON.parse(result['slice']);
                    }
                    if (result['conditions'] != undefined) {
                        var conditions = JSON.parse(result['conditions']);
                    }
                    if (result['formats'] != undefined) {
                        var formats = JSON.parse(result['formats']);
                    }

                    if (result['cols_types'] != undefined) {
                        var cols_types = JSON.parse(result['cols_types']);
                    }


                    if (result['header'] != undefined) {
                        header = result['header'];
                    }

                    if (result['footer'] != undefined) {
                        footer = result['footer'];
                    }

                    if (result['company_image'] != undefined) {
                        var company_image = result['company_image'];
                    }


                    var lang = self.params['context']['lang']

                    // stop arabic 
                    // if (lang == 'ar' || lang == 'ar_SY') {
                    //     var lang_file = "/data_chart/static/src/json/ar.json";
                    // }
                    self.pivot = new WebDataRocks({
                        beforetoolbarcreated: self.customizeToolbar,
                        container: "#wdr-component",
                        toolbar: true,
                        report: {
                            dataSource: {
                                data: [cols_types].concat(data)
                            },
                            slice: slice,
                            options: options,
                            conditions: conditions,
                            formats: formats,
                        },


                        global: {
                            // replace this path with the path to your own translated file

                            // localization: lang_file
                        },


                    });
                    console.log("----------------------self.customizeToolbar",self.customizeToolbar)

                    webdatarocks.on('reportcomplete', function () {
                        webdatarocks.refresh();
                    });
                    var old_export = self.pivot.exportTo

                    webdatarocks.exportTo = function (type, options, callback) {
                        if (options == undefined) {
                            options = {}
                        }
                        options.header = "<div><img src='data:image/png;base64, " + company_image + "' alt='my company' width='80' height='80'>" + header + "</br></br></div>"
                        options.footer = footer + "</br></br>"
                        old_export(type, options, callback)
                    }



                    if (self.params['context']['title'] != undefined) {
                        webdatarocks.setOptions({
                            grid: {
                                title: self.params['context']['title']
                            }
                        });
                    }


                    self.pivot.model_params = self.params;
                    self.pivot.parent_w = self;
                    self.pivot.background_image = company_image
                    self.pivot.cols_types = cols_types
                    self.pivot.orignal_data = result['data'];




                }, function () {
                    alert("ERROR IN REPORT CONFIGURATION !");
                });
        },


        start: function () {
            var self = this;

            try {
                self.load_data();
            } catch (error) {

            }

            return this._super();

            var call_data = {
                model: 'data_chart_model',
                method: "data_chart_details",
                args: [this.params['context']['model'], this.params['context']["active_id"]],
            }

            rpc.query(call_data)
                .then(function (result) {
                    var data = result['data'];
                    if (result['options'] != undefined) {
                        var options = JSON.parse(result['options']);
                    }
                    if (result['slice'] != undefined) {
                        var slice = JSON.parse(result['slice']);
                    }
                    if (result['conditions'] != undefined) {
                        var conditions = JSON.parse(result['conditions']);
                    }

                    var pivot = new WebDataRocks({
                        beforetoolbarcreated: self.customizeToolbar,
                        container: "#wdr-component",
                        toolbar: true,
                        report: {
                            dataSource: {
                                data: data
                            },
                            slice: slice,
                            options: options,
                            conditions: conditions,
                        },
                        global: {
                            // replace this path with the path to your own translated file
                            localization: "/data_chart/static/src/json/ar.json"
                        }
                    });


                    if (self.params['context']['title'] != undefined) {
                        webdatarocks.setOptions({
                            grid: {
                                title: self.params['context']['title']
                            }
                        });
                    }


                    pivot.model_params = self.params;


                    // var options = pivot.getOptions();
                    // options.params = this.params;
                    // pivot.setOptions(options);
                    // pivot.refresh();




                });

            return this._super();
        },

        set_default: function () {
            var options = JSON.stringify(this.pivot.getOptions());
            var slice = JSON.stringify(this.pivot.getReport()['slice']);
            var conditions = JSON.stringify(this.pivot.getReport()['conditions']);
            var formats = JSON.stringify(this.pivot.getReport()['formats']);
            var cols_types = JSON.stringify(this.pivot.cols_types);

            var call_data = {
                model: 'data_chart_model',
                method: "set_default",
                args: [this.pivot.model_params['context']['model'], this.pivot.model_params['context']['active_id'], options, slice, conditions, formats, cols_types],
            }
            rpc.query(call_data)
                .then(function (result) {});
        },

        get_default: function () {
            self.load_data(true);
        },

        update_data: function (toolbar) {
            webdatarocks.updateData({
                data: [toolbar.pivot.cols_types].concat(toolbar.pivot.orignal_data)
            });
        },
        fillColTypesDropDown: function (DropDown, selected) {
            DropDown[0] = new Option('string', 'string');
            DropDown[1] = new Option('date string', 'date string');
            DropDown[2] = new Option('date', 'date');
            DropDown[3] = new Option('year/month/day', 'year/month/day');
            DropDown[4] = new Option('year/quarter/month/day', 'year/quarter/month/day');
            DropDown[5] = new Option('number', 'number');
            DropDown[6] = new Option('weekday', 'weekday');
            DropDown[7] = new Option('month', 'month');
            DropDown[8] = new Option('datetime', 'datetime');
            DropDown[9] = new Option('time', 'time');
            DropDown.value = (selected);
        },
        set_cols_types: function (toolbar) {
            var options = JSON.stringify(toolbar.pivot.getOptions());
            var slice = JSON.stringify(toolbar.pivot.getReport()['slice']);
            var conditions = JSON.stringify(toolbar.pivot.getReport()['conditions']);
            var formats = JSON.stringify(toolbar.pivot.getReport()['formats']);
            var cols_types = JSON.stringify(toolbar.pivot.cols_types);

            var a = toolbar,
                b = toolbar.Labels,
                d = toolbar.popupManager.createPopup();


            d.setTitle('Column Types');
            d.setToolbar([{
                id: "wdr-btn-apply",
                label: b.apply,
                handler: function () {
                    var new_col_types = {};
                    for (var key in toolbar.pivot.cols_types) {
                        var key_id = "ctse_" + (key.split(' ').join('_'));
                        var el = document.getElementById(key_id);
                        new_col_types[key] = {
                            'type': el.value
                        }

                    };
                    toolbar.pivot.cols_types = new_col_types
                    toolbar.pivot.parent_w.update_data(toolbar);
                },
                isPositive: !0
            }, {
                id: "wdr-btn-cancel",
                label: b.cancel
            }]);
            var f = document.createElement("div");


            for (var key in toolbar.pivot.cols_types) {
                var selected_type = toolbar.pivot.cols_types[key]['type'];

                var row = document.createElement("div");
                row.classList.add("wdr-cr-inner");
                var label = document.createElement("div");
                label.classList.add("wdr-cr-lbl");
                label.style.width = "40%";
                a.setText(label, key + ":");
                row.appendChild(label);

                var select = a.createSelect();

                select.style.width = "40%";

                select.select.id = "ctse_" + (key.split(' ').join('_'));

                toolbar.pivot.parent_w.fillColTypesDropDown(select.select, selected_type);
                row.appendChild(select);
                f.appendChild(row);
            }

            d.setContent(f);
            toolbar.popupManager.addPopup(d.content)


            var call_data = {
                model: 'data_chart_model',
                method: "set_default",
                args: [toolbar.pivot.model_params['context']['model'], toolbar.pivot.model_params['context']['active_id'], options, slice, conditions, formats, cols_types],
            }
            rpc.query(call_data)
                .then(function (result) {});
        },




        customizeToolbar: function (toolbar) {
            var self = this;
            var tabs = toolbar.getTabs(); // get all tabs from the toolbar
            toolbar.getTabs = function () {
                delete tabs[0]; // delete the first tab
                delete tabs[1];
                tabs[2]['handler'] = function () {
                    var options = JSON.stringify(this.pivot.getOptions());
                    var slice = JSON.stringify(this.pivot.getReport()['slice']);
                    var conditions = JSON.stringify(this.pivot.getReport()['conditions']);
                    var formats = JSON.stringify(this.pivot.getReport()['formats']);
                    var cols_types = JSON.stringify(this.pivot.cols_types);

                    var call_data = {
                        model: 'data_chart_model',
                        method: "save_options",
                        args: [this.pivot.model_params['context']['model'], this.pivot.model_params['context']['active_id'], options, slice, conditions, formats, cols_types],
                    }

                    rpc.query(call_data)
                        .then(function (result) {});


                }

                delete tabs[3]['menu'][0];
                delete tabs[3]['menu'][1];

                tabs.unshift({
                    id: "wdr-tab-get-default",
                    title: "Original",
                    handler: function () {
                        this.pivot.parent_w.load_data(true);
                    },
                    icon: '<svg width="36" height="36" xmlns="http://www.w3.org/2000/svg"> <desc>This graphic links to an external image </desc> <image width="36" height="36" href="data_chart/static/src/img/icons8-reset-64.png"> <title>Get Default</title> </image> </svg>'

                });
                if (this.pivot.model_params['context']['admin_view'] != undefined) {
                    tabs.unshift({
                        id: "wdr-tab-set-default",
                        title: "Default",
                        handler: this.pivot.parent_w.set_default,
                        icon: '<svg width="36" height="36" xmlns="http://www.w3.org/2000/svg"> <desc>This graphic links to an external image </desc> <image width="36" height="36" href="data_chart/static/src/img/user-cog-solid.svg"> <title>Set Default</title> </image> </svg>'

                    });
                }

                tabs.unshift({
                    id: "wdr-tab-set-cols_types",
                    title: "Types",
                    handler: function () {
                        this.pivot.parent_w.set_cols_types(toolbar);
                    },
                    icon: '<svg width="36" height="36" xmlns="http://www.w3.org/2000/svg"> <desc>This graphic links to an external image </desc> <image width="36" height="36" href="data_chart/static/src/img/icons8-data-48.png"> <title>Filds Types</title> </image> </svg>'

                });





                return tabs;
            }
        },







    });

    core.action_registry.add('data_view', dataChart);


    return dataChart;

});