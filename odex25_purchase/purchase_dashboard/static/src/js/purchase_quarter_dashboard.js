odoo.define('purchase_dashboard.purchase_quarter_dashboard', function(require) {

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
    var PurchaseDashboardQuarter = AbstractAction.extend({
        contentTemplate: 'PurchaseDashboardQuarter',


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
            self.populate_years();

            self.$("#year").on("change", function(){
                self.render_dashboard();
            });

            self.$("#quarter").on("change", function(){
                self.render_dashboard();
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
            var year = self.$("#year").val();
            var quarter = self.$("#quarter").val();
            var quarter_name;

            if (quarter == 'Q1')
                quarter_name = "الربع الأول";
            if (quarter == 'Q2')
                quarter_name = "الربع الثاني";
            if (quarter == 'Q3')
                quarter_name = "الربع الثالث";
            if (quarter == 'Q4')
                quarter_name = "الربع الرابع";

            if (year != undefined){
                self._rpc({
                    model: 'purchase.order',
                    method: 'get_quarter_purchase_data',
                    args: [year, quarter],
                }).then(function(result) {
                    self.$("#top_content").html(`
                        <div class="col-md-3 col-sm-3 col-lg-3 col-sm-offset-1 col-md-offset-1 col-lg-offset-1">
                            <div class="col-md-12 col-sm-12 col-lg-12 text-center">
                                <b><h1 class="dash-text-primary dash-text-bold">ملخص عام</h1></b>
                                <h2 class="dash-text-primary dash-text-bold">${quarter_name}</h2>
                                <h2 class="dash-text-primary dash-text-bold">${year}</h2>
                            </div>
                        </div>
                        <div class="col-md-2 col-sm-2 col-lg-2">
                            <div class="col-md-6 col-sm-6 col-lg-6 text-center">
                                <h1 class="dash-text-info dash-text-bold">${result.contract_count}</h1>
                                <h4>عدد العقود والإتفاقيات</h4>
                            </div>
                            <div class="col-md-6 col-sm-6 col-lg-6 text-center">
                                <h3 class="dash-text-info">عقد</h3>
                                <img src="/purchase_dashboard/static/src/img/purchase_contract.png"
                                 class="img-responsive img-md img" height="100%" width="100%"/>
                            </div>
                        </div>
                        <div class="col-md-2 col-sm-2 col-lg-2">
                            <div class="col-md-6 col-sm-6 col-lg-6 text-center">
                                <h1 class="dash-text-info dash-text-bold">${result.purchase_request_count}</h1>
                                <h4>عدد طلبات الشراء</h4>
                            </div>
                            <div class="col-md-6 col-sm-6 col-lg-6 text-center">
                                <h3 class="dash-text-info">طلب شراء</h3>
                                <img src="/purchase_dashboard/static/src/img/purchase_request.png"
                                 class="img-responsive img-md img" height="100%" width="100%"/>
                            </div>
                        </div>
                        <div class="col-md-2 col-sm-2 col-lg-2">
                            <div class="col-md-6 col-sm-6 col-lg-6 text-center">
                                <h1 class="dash-text-info dash-text-bold">${result.purchase_order_count}</h1>
                                <h4>عدد أوامر الشراء الصادرة</h4>
                            </div>
                            <div class="col-md-6 col-sm-6 col-lg-6 text-center">
                                <h3 class="dash-text-info">أمر شراء</h3>
                                <img src="/purchase_dashboard/static/src/img/purchase_order.png"
                                 class="img-responsive img-md img" height="100%" width="100%"/>
                            </div>
                        </div>
                    `);

                    self.$("#mid_content").html(`
                        <img src="/purchase_dashboard/static/src/img/calculator.png"
                             class="img-responsive img-md img" height="20%" width="20%"/>
                        <div class="col-md-10 col-lg-10 col-sm-10">
                            <h2 class="text-center dash-text-info dash-text-bold">قيمة المشتريات الإجمالية ${quarter_name} ${year}</h2>
                            <div class="text-center dash-text-primary dash-bg-success dash-text-white
                             dash-text-bold col-md-10 col-lg-10 col-sm-10">
                                <h1>${result.purchase_quarter_total}</h1>
                            </div>
                            <p class="col-md-2 col-lg-2 col-sm-2">ريال سعودي</p>
                        </div>
                    `);

                    var bottom_content = ``;
                    for (var dept of result.purchase_by_department){
                        bottom_content += `<div class="col-md-6 col-lg-6 col-sm-6 mb32">
                                                <div class="col-md-6 col-lg-6 col-sm-6 text-center">
                                                    <h2 class="dash-text-info">${dept.name}</h2>
                                                </div>
                                                <div class="col-md-6 col-lg-6 col-sm-6 dash-bg-info text-center dash-text-white">
                                                    <h1>${dept.y}</h1>
                                                </div>
                                            </div>`;
                    }

                    self.$("#bottom_content").html(bottom_content);

                    var chart_title = ' قيمة المشتريات الإجمالية ' + quarter_name + ' ' + year;
                    // Create the chart
                    Highcharts.chart('chart1', {
                        chart: {
                            type: 'pie'
                        },
                        title: {
                            text: chart_title
                        },
                        plotOptions: {
                            pie: {
                                shadow: false,
                                center: ['50%', '50%'],
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
                            name: 'Purchases',
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
                        responsive: {
                            rules: [{
                                condition: {
                                    maxWidth: 400
                                },
                                chartOptions: {
                                    series: [{
                                    }]
                                }
                            }]
                        }
                    });
                });

            }
            self.$(".highcharts-data-table").remove();
        },
    });

    core.action_registry.add('purchase_quarter_dashboard', PurchaseDashboardQuarter);

    return PurchaseDashboardQuarter;
});
