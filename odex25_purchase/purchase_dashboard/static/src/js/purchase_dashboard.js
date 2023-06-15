odoo.define('purchase_dashboard.PurchaseDashboard', function(require) {

    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var session = require('web.session');
    var _t = core._t;
    var QWeb = core.qweb;
    var self = this;
    var currency;
    var PurchaseDashboard = AbstractAction.extend({
        contentTemplate: 'PurchaseDashboard',


        events: {
            'click #update_graphs': 'update_graphs'
        },

        renderElement: function() {
            var self = this;
            $.when(this._super()).then(function(){
                // We use setTimeout because it avoids rendering issues
                // FIXME: Find out why is this happening and then fix it
                setTimeout(function(){
                    self.render_filters();
                }, 0);
            });
        },

        start: function() {
            var self = this;
            const res = this._super();
            return res;
        },
        render_filters: function(){
            var self = this;

            self.$("#period_filter").hide();
            var view_type_year = self.$("#view_year");
            view_type_year.on('change', function(){
                self.$("#period_filter").hide();
                self.$("#year_filter").show();
                self.render_dashboard();
            });

            var view_type_period = self.$("#view_period");
            view_type_period.on('click', function(){
                self.$("#period_filter").show();
                self.$("#year_filter").hide();
                self.render_dashboard();
            });

            var default_from_date = '01/01/' + (new Date()).getFullYear();
            self.$('#from_date').datepicker({
                showOn: "focus",
            });
            self.$('#from_date').val(default_from_date);

            var default_to_date = '12/31/' + (new Date()).getFullYear();
            self.$('#to_date').datepicker({
                showOn: "focus",
            });
            self.$('#to_date').val(default_to_date);

            self.populate_departments();
            self.populate_vendors();
            self.populate_years();

            var year_field = self.$('#year');
            year_field.on("change", function(){
                self.render_dashboard();
            });

            var state_field = self.$('#state');
            state_field.on("change", function(){
                self.render_dashboard();
            });

            self.$('#from_date').on("change", function(){
                self.render_dashboard();
            });

            self.$('#to_date').on("change", function(){
                self.render_dashboard();
            });

            self.$("#select_all_departments").on("click", function(){
                var depts = self.$('.dropdown-mul-departments').data('dropdown').config.data;
                depts = depts.map(dept => dept.id);
                self.$('.dropdown-mul-departments').data('dropdown').choose(depts, true);
                self.render_dashboard();
            });

            self.$("#clear_departments").on("click", function(){
                self.$('.dropdown-mul-departments').data('dropdown').reset();
                self.render_dashboard();
            });

            self.$("#select_all_vendors").on("click", function(){
                var vendors = self.$('.dropdown-mul-vendors').data('dropdown').config.data;
                vendors = vendors.map(vendor => vendor.id);
                self.$('.dropdown-mul-vendors').data('dropdown').choose(vendors, true);
                self.render_dashboard();
            });

            self.$("#clear_vendors").on("click", function(){
                self.$('.dropdown-mul-vendors').data('dropdown').reset();
                self.render_dashboard();
            });
        },

        populate_departments: function(){
            var departments_json = [];
            var self = this;
            this._rpc({
                model: 'purchase.order',
                method: 'get_cost_centers',
            }).then(function (result) {
                result.forEach(function(department){
                    departments_json.push({id: department.id, name: department.name});
                });
                self.$('.dropdown-mul-departments').dropdown({
                    data: departments_json,
                    limitCount: Infinity,
                    multipleMode: 'label',
                    searchNoData: '<li style="color:#ddd">No Results</li>',
                    input:'<input type="text" maxLength="50" placeholder="">',
                    choice: function() {
                        self.render_dashboard();
                    }
                });
            });
        },

        populate_vendors: function(){
            var vendors_json = [];
            var self = this;
            this._rpc({
                model: 'purchase.order',
                method: 'get_vendors',
            }).then(function (result) {
                result.forEach(function(vendor){
                    vendors_json.push({id: vendor.id, name: vendor.name});
                });
                self.$('.dropdown-mul-vendors').dropdown({
                    data: vendors_json,
                    limitCount: Infinity,
                    multipleMode: 'label',
                    searchNoData: '<li style="color:#ddd">No Results</li>',
                    input:'<input type="text" maxLength="50" placeholder="">',
                    choice: function() {
                        self.render_dashboard();
                    }
                });
            });
        },

        populate_years: function(){
            var self = this;
            var year_field = self.$('#year');
            self._rpc({
                model: 'purchase.order',
                method: 'get_years',
            }).then(function (result) {
                result.forEach(function(year){
                    year_field.append(`<option value=${year}>${year}</option>`);
                });
                self.render_dashboard();
            });
        },

        render_dashboard: function(){
            var self = this;
            var year = self.$('#year').val();
            var state = self.$('#state').val();
            var view_type = $("input[name='view_type']:checked").val();
            var depts = [];
            if ($(".dropdown-mul-departments").data('dropdown') != undefined){
                depts = $(".dropdown-mul-departments").data('dropdown').config.data;
                depts = _.filter(depts, function(dept){
                    return dept.selected == true;
                })
                depts = depts.map(dept => dept.id);
            }

            var vendors = [];
            if ($(".dropdown-mul-vendors").data('dropdown') != undefined){
                vendors = $(".dropdown-mul-vendors").data('dropdown').config.data;
                vendors = _.filter(vendors, function(vendor){
                    return vendor.selected == true;
                })
                vendors = vendors.map(vendor => vendor.id);
            }

            var from_date = self.$('#from_date').val();
            var to_date = self.$('#to_date').val();

            if (view_type != undefined){
                if (view_type == 'year' && year != undefined){
                    self._rpc({
                        model: 'purchase.order',
                        method: 'get_annual_purchase_data',
                        args: [year, state, depts, vendors],
                    }).then(function(result) {
                        $("#purchase_quarter_pie_graph").show();
                        $("#purchase_dashboard_content").html(`
                            <b><h1 class="text-center dash-text-info dash-text-bold">تفاصيل أوامر الشراء خلال عام ${year}</h1></b>
                            <b><h2 class="text-center dash-text-primary dash-text-bold">إجمالي عدد أوامر الشراء الصادرة : ${result.purchase_count}</h2></b>
                            <br/>
                            <div class="row">
                                <div class="col-md-3 col-sm-3 col-lg-3">
                                    <div class="dash-bg-primary text-center dash-rounded dash-box col-md-8 col-md-offset-2 col-lg-8 col-lg-offset-2 col-sm-8 col-sm-offset-2">
                                        <h1>Q1</h1>
                                    </div>
                                    <div class="col-md-12 col-sm-12 col-lg-12">
                                        <h1 class="dash-text-primary dash-text-bold">${result.purchase_by_quarter[0].y}</h1>
                                        <p>ريال سعودي</p>
                                    </div>
                                </div>
                                <div class="col-md-3 col-sm-3 col-lg-3">
                                    <div class="dash-bg-success text-center dash-rounded dash-box col-md-8 col-md-offset-2 col-lg-8 col-lg-offset-2 col-sm-8 col-sm-offset-2">
                                        <h1>Q2</h1>
                                    </div>
                                    <div class="col-md-12 col-sm-12 col-lg-12">
                                        <h1 class="dash-text-success dash-text-bold">${result.purchase_by_quarter[1].y}</h1>
                                        <p>ريال سعودي</p>
                                    </div>
                                </div>
                                <div class="col-md-3 col-sm-3 col-lg-3">
                                    <div class="dash-bg-info text-center dash-rounded dash-box col-md-8 col-md-offset-2 col-lg-8 col-lg-offset-2 col-sm-8 col-sm-offset-2">
                                        <h1>Q3</h1>
                                    </div>
                                    <div class="col-md-12 col-sm-12 col-lg-12">
                                        <h1 class="dash-text-info dash-text-bold">${result.purchase_by_quarter[2].y}</h1>
                                        <p>ريال سعودي</p>
                                    </div>
                                </div>
                                <div class="col-md-3 col-sm-3 col-lg-3">
                                    <div class="dash-bg-warning text-center dash-rounded dash-box col-md-8 col-md-offset-2 col-lg-8 col-lg-offset-2 col-sm-8 col-sm-offset-2">
                                        <h1>Q4</h1>
                                    </div>
                                    <div class="col-md-12 col-sm-12 col-lg-12">
                                        <h1 class="dash-text-warning dash-text-bold">${result.purchase_by_quarter[3].y}</h1>
                                        <p>ريال سعودي</p>
                                    </div>
                                </div>
                            </div>
                            <div class="row mt64">
                                <div class="col-md-12 col-lg-12 col-sm-12 items-v-center" style="height: 350px;">
                                    <img src="/purchase_dashboard/static/src/img/calculator.png"
                                         class="img-responsive img-md img" height="20%" width="20%"/>
                                    <div class="col-md-10 col-lg-10 col-sm-10">
                                        <h2 class="text-center dash-text-info dash-text-bold">قيمة المشتريات الإجمالية للعام ${year}</h2>
                                        <div class="text-center dash-text-primary dash-bg-success dash-text-white
                                         dash-text-bold col-md-10 col-lg-10 col-sm-10">
                                            <h1>${result.purchase_total_year}</h1>
                                        </div>
                                        <p class="col-md-2 col-lg-2 col-sm-2">ريال سعودي</p>
                                    </div>
                                </div>
                            </div>
                        `);

                        Highcharts.chart('chart1', {
                            chart: {
                                type: 'pie'
                            },
                            title: {
                                text: 'إجمالي أوامر الشراء بالأرباع'
                            },
                            plotOptions: {
                                pie: {
                                    allowPointSelect: true,
                                    cursor: 'pointer',
                                    dataLabels: {
                                        enabled: false
                                    },
                                    showInLegend: true
                                }
                            },
                            tooltip: {
                                valueSuffix: 'ر. س.'
                            },
                            series: [{
                                name: _t('Purchases'),
                                data: result.purchase_by_quarter,
                                innerSize: '40%',
                                dataLabels: {
                                    formatter: function () {
                                        return this.y > 5 ? this.point.name : null;
                                    },
                                    color: '#ffffff',
                                    distance: -30
                                }
                            }],
                            exporting: {
                                csv: {
                                    columnHeaderFormatter: function(item, key) {
                                        if (item instanceof Highcharts.Series) {
                                            return _t('Purchases')
                                        }

                                        return _t('Quarter');
                                    }
                                }
                            }
                        });

                        Highcharts.chart('chart2', {
                            chart: {
                                type: 'pie'
                            },
                            title: {
                                text: 'إجمالي أوامر الشراء بالموردين'
                            },
                            plotOptions: {
                                pie: {
                                    allowPointSelect: true,
                                    cursor: 'pointer',
                                    dataLabels: {
                                        enabled: false
                                    },
                                    showInLegend: true
                                }
                            },
                            tooltip: {
                                valueSuffix: 'ر. س.'
                            },
                            series: [{
                                name: _t('Purchases'),
                                data: result.purchase_by_partner,
                                innerSize: '40%',
                                dataLabels: {
                                    formatter: function () {
                                        return this.y > 5 ? this.point.name : null;
                                    },
                                    color: '#ffffff',
                                    distance: -30
                                }
                            }],
                            exporting: {
                                csv: {
                                    columnHeaderFormatter: function(item, key) {
                                        if (item instanceof Highcharts.Series) {
                                            return _t('Purchases')
                                        }

                                        return _t('Partner');
                                    }
                                }
                            }
                        });

                        Highcharts.chart('chart3', {
                            chart: {
                                type: 'pie'
                            },
                            title: {
                                text: 'إجمالي أوامر الشراء بالإدارات'
                            },
                            plotOptions: {
                                pie: {
                                    allowPointSelect: true,
                                    cursor: 'pointer',
                                    dataLabels: {
                                        enabled: false
                                    },
                                    showInLegend: true
                                }
                            },
                            tooltip: {
                                valueSuffix: 'ر. س.'
                            },
                            series: [{
                                name: _t('Purchases'),
                                data: result.purchase_by_department,
                                innerSize: '40%',
                                dataLabels: {
                                    formatter: function () {
                                        return this.y > 5 ? this.point.name : null;
                                    },
                                    color: '#ffffff',
                                    distance: -30
                                }
                            }],
                            exporting: {
                                csv: {
                                    columnHeaderFormatter: function(item, key) {
                                        if (item instanceof Highcharts.Series) {
                                            return _t('Purchases')
                                        }

                                        return _t('Department');
                                    }
                                }
                            }
                        });

                    });
                }else if (view_type == 'period' && !isNaN(Date.parse(from_date)) && !isNaN(Date.parse(to_date))){
                    self._rpc({
                        model: 'purchase.order',
                        method: 'get_period_purchase_data',
                        args: [from_date, to_date, state, depts, vendors],
                    }).then(function(result) {
                        $("#purchase_quarter_pie_graph").hide();
                        $("#purchase_dashboard_content").html(`
                            <b><h1 class="text-center dash-text-info dash-text-bold"> تفاصيل أوامر الشراء في الفترة من ${from_date}  الى  ${to_date} </h1></b>
                            <b><h2 class="text-center dash-text-primary dash-text-bold">إجمالي عدد أوامر الشراء الصادرة : ${result.purchase_count}</h2></b>
                            <br/>
                            <div class="row mt64">
                                <div class="col-md-12 col-lg-12 col-sm-12 items-v-center" style="height: 350px;">
                                    <img src="/purchase_dashboard/static/src/img/calculator.png"
                                         class="img-responsive img-md img" height="20%" width="20%"/>
                                    <div class="col-md-10 col-lg-10 col-sm-10">
                                        <h2 class="text-center dash-text-info dash-text-bold"> قيمة المشتريات الإجمالية في الفترة من ${from_date}  الى  ${to_date} </h2>
                                        <div class="text-center dash-text-primary dash-bg-success dash-text-white
                                         dash-text-bold col-md-10 col-lg-10 col-sm-10">
                                            <h1>${result.purchase_period_total}</h1>
                                        </div>
                                        <p class="col-md-2 col-lg-2 col-sm-2">ريال سعودي</p>
                                    </div>
                                </div>
                            </div>
                        `);

                        Highcharts.chart('chart2', {
                            chart: {
                                type: 'pie'
                            },
                            title: {
                                text: 'إجمالي أوامر الشراء بالموردين'
                            },
                            plotOptions: {
                                pie: {
                                    allowPointSelect: true,
                                    cursor: 'pointer',
                                    dataLabels: {
                                        enabled: false
                                    },
                                    showInLegend: true
                                }
                            },
                            tooltip: {
                                valueSuffix: 'ر. س.'
                            },
                            series: [{
                                name: _t('Purchases'),
                                data: result.purchase_by_partner,
                                innerSize: '40%',
                                dataLabels: {
                                    formatter: function () {
                                        return this.y > 5 ? this.point.name : null;
                                    },
                                    color: '#ffffff',
                                    distance: -30
                                }
                            }],
                            exporting: {
                                csv: {
                                    columnHeaderFormatter: function(item, key) {
                                        if (item instanceof Highcharts.Series) {
                                            return _t('Purchases')
                                        }

                                        return _t('Partner');
                                    }
                                }
                            }
                        });

                        Highcharts.chart('chart3', {
                            chart: {
                                type: 'pie'
                            },
                            title: {
                                text: 'إجمالي أوامر الشراء بالإدارات'
                            },
                            plotOptions: {
                                pie: {
                                    allowPointSelect: true,
                                    cursor: 'pointer',
                                    dataLabels: {
                                        enabled: false
                                    },
                                    showInLegend: true
                                }
                            },
                            tooltip: {
                                valueSuffix: 'ر. س.'
                            },
                            series: [{
                                name: _t('Purchases'),
                                data: result.purchase_by_department,
                                innerSize: '40%',
                                dataLabels: {
                                    formatter: function () {
                                        return this.y > 5 ? this.point.name : null;
                                    },
                                    color: '#ffffff',
                                    distance: -30
                                }
                            }],
                            exporting: {
                                csv: {
                                    columnHeaderFormatter: function(item, key) {
                                        if (item instanceof Highcharts.Series) {
                                            return _t('Purchases')
                                        }

                                        return _t('Department');
                                    }
                                }
                            }
                        });
                    });
                }
                self.$(".highcharts-data-table").remove();
            }
        },
    });

    core.action_registry.add('purchase_dashboard', PurchaseDashboard);

    return PurchaseDashboard;
});
