$(document).ready(function () {
    $('.dashboard14-theme-2 [data-target="extra-nav"]').on('click',function () {
        $("header.dashboard14-header").toggleClass("open-extra");   
    });
    // $(':not([data-target="extra-nav"])').on('click',function () {
    //     $("header.dashboard14-header").removeClass("open-extra");   
    // });

    $('.dashboard14-theme-2 li[data-target="menu-section"]').click(function (){
        // change menu status
        $('li[data-target="menu-section"]').removeClass('active');
        $(this).addClass('active');
        let section = $(this).attr("data-section");
        // change section status
        $('.dashboard14-section').removeClass("active");
        $('.dashboard14-section#section-'+section).addClass("active");
    });

    for(let i=0; i < 30;i++){
        $(".dashboard14-theme-2 #self-service-body").append(`
        <div class="col-md-3 service-box">
            <div class="col-12 service-body shadow-sm">
                <div class="col-md-3 service-icon">
                    <div class="service-icons">
                        <img src="/system_dashboard/static/src/icon/dashboard/salary.svg"/>
                    </div>
                </div>
                <div class="col-md-9 service-content">
                    <div class="col-12 p-0">
                        <h3>15</h3>
                        <p>Annul Leaves</p>
                        <a href="#">
                            <img src="/system_dashboard/static/src/icon/right-arrow.svg"/>
                        </a>
                    </div>
                </div>
            </div>
        </div>
        `);
    }

    //chart (1)
    var ctx = $('.dashboard14-theme-2 #myChart');
    var myChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017"],
            datasets: [
                {
                    label: "Evaluation",
                    data: [140, 100, 90, 115, 120, 150,160,180],
                    borderColor: "#32C7FF",
                    backgroundColor: "#32C7FF"
                }
            ]
        },
        options: {
            responsive: true,
            animations: {
                tension: {
                    duration: 1000,
                    from: 1,
                    to: 0,
                    loop: false
                }
            },
        }
    });

    // chart (2)
    var ctx2 = $('.dashboard14-theme-2 #myChart2');
    // const gradientBg = ctx2.createLinearradient()
    var myChart2 = new Chart(ctx2, {
        type: "line",
        data: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug","Sep","Oct","Nov","Dec"],
            datasets: [
                {
                    label: "Hours",
                    data: [8, 8, 7, 9, 7.50, 6,7,8,8,8,8,9],
                    borderColor: "#32C7FF",
                    backgroundColor: "rgb(101 178 249 / 48%)",
                    tension: 0.4,
                    fill: true, 
                }
            ]
        },
        options: {
            responsive: true,
            animations: {
                tension: {
                    duration: 1000,
                    from: 1,
                    to: 0.4,
                    loop: false
                }
            },
        }
    });

    // // chart (3)
    var ctx3 = $('.dashboard14-theme-2 #myChart3');
    // const gradientBg = ctx3.createLinearradient()
    var myChart3 = new Chart(ctx3, {
        type: "line",
        data: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug","Sep","Oct","Nov","Dec"],
            datasets: [
                {
                    label: "Hours",
                    data: [8, 8, 7, 9, 7.50, 6,7,8,8,8,8,9],
                    borderColor: "#32C7FF",
                    backgroundColor: "rgb(101 178 249 / 48%)",
                    tension: 0.4,
                    fill: true, 
                }
            ]
        },
        options: {
            responsive: true,
            animations: {
                tension: {
                    duration: 1000,
                    from: 1,
                    to: 0.4,
                    loop: false
                }
            },
        }
    });

    // // chart (4)
    var ctx4 = $('.dashboard14-theme-2 #myChart4');
    var myChart4 = new Chart(ctx4, {
        type: "line",
        data: {
            labels: ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017"],
            datasets: [
                {
                    label: "Evaluation",
                    data: [140, 100, 90, 115, 120, 150,160,180],
                    borderColor: "#32C7FF",
                    backgroundColor: "#32C7FF"
                }
            ]
        },
        options: {
            responsive: true,
            animations: {
                tension: {
                    duration: 1000,
                    from: 1,
                    to: 0,
                    loop: false
                }
            },
        }
    });

    // // chart (1)
    var ctx_1 = $('.dashboard14-theme-2 #chart1');
    var chart1 = new Chart(ctx_1, {
        type: "line",
        data: {
            labels: ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017"],
            datasets: [
                {
                    label: "Evaluation",
                    data: [140, 100, 90, 115, 120, 150,160,180],
                    borderColor: "#32C7FF",
                    backgroundColor: "#32C7FF"
                }
            ]
        },
        options: {
            responsive: true,
            animations: {
                tension: {
                    duration: 1000,
                    from: 1,
                    to: 0,
                    loop: false
                }
            },
        }
    });

    // // chart (2)
    var ctx_2 = $('.dashboard14-theme-2 #chart2');
    var chart2 = new Chart(ctx_2, {
        type: "line",
        data: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug","Sep","Oct","Nov","Dec"],
            datasets: [
                {
                    label: "Hours",
                    data: [8, 8, 7, 9, 7.50, 6,7,8,8,8,8,9],
                    borderColor: "#32C7FF",
                    backgroundColor: "rgb(101 178 249 / 48%)",
                    tension: 0.4,
                    fill: true, 
                }
            ]
        },
        options: {
            responsive: true,
            animations: {
                tension: {
                    duration: 1000,
                    from: 1,
                    to: 0.4,
                    loop: false
                }
            },
        }
    });
});
