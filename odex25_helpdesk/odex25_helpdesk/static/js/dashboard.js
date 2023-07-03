
let dashboard = gsap.timeline({})
dashboard.from(".animation", { duration: .5, opacity: 0, y: 20, stagger: .2 })


//////////////////////// Line Chart //////////////////////////////

const ctx = document.getElementById('lineChart').getContext('2d');

var gradient = ctx.createLinearGradient(0, 0, 0, 300);
gradient.addColorStop(0.3, 'rgba(108,179,160,1)');
gradient.addColorStop(.8, 'rgba(0,0,0,0)');

const lineChartSection = new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [{
      label: 'Success Rate',
      data: [50, 48, 30, 25, 28, 38, 40, 33, 31, 36, 41, 40],
      borderWidth: 3,
      borderColor: 'rgba(5,197,166,1)',
      tension: .3,
      fill: true,
      backgroundColor: gradient,
    }]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    },
    maintainAspectRatio: false,
    scales: {
      y: {
        min: 10,
        max: 50,
        ticks: {
          // forces step size to be 50 units
          stepSize: 10
        },
        stacked: true,
        grid: {
          display: true,
          color: "rgba(197,197,197,.5)"
        }
      },
      x: {
        grid: {
          display: false
        }
      }
    }
  }
});

//////////////////////// Bar Chart //////////////////////////////


const ctx2 = document.getElementById('barChart').getContext('2d');
const barChartSection = new Chart(ctx2, {
  type: 'bar',
  data: {
    labels: ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8', 'team9', 'team10', 'team11', 'team12'],
    datasets: [{
      label: 'Team Progress',
      data: [43, 25, 58, 46, 34, 17, 22, 30, 60, 12, 25, 52],
      backgroundColor: [
        'rgb(71, 145, 255)',
        'rgb(216, 173, 2)',
        'rgb(12, 177, 139)',
        'rgb(71, 145, 255)',
        'rgb(216, 173, 2)',
        'rgb(247, 97, 97)',
        'rgb(247, 97, 97)',
        'rgb(216, 173, 2)',
        'rgb(12, 177, 139)',
        'rgb(247, 97, 97)',
        'rgb(216, 173, 2)',
        'rgb(12, 177, 139)',
      ],
      borderWidth: 1,
      borderRadius: 6,
      barPercentage: .2,
    }]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    },
    maintainAspectRatio: false,
    scales: {
      y: {
        min: 10,
        max: 60,
        ticks: {
          // forces step size to be 50 units
          stepSize: 10
        },
        stacked: true,
        grid: {
          display: true,
          color: "rgba(197,197,197,.5)"
        }
      },
      x: {
        grid: {
          display: false
        }
      }
    }
  }
});


//////////////////////// Donatus Chart //////////////////////////////

const ctx3 = document.getElementById('donatusChart').getContext('2d');
const DonatusChartSection = new Chart(ctx3, {
  type: 'doughnut',
  data: {
    labels: ['Urgent', 'High', 'Low'],
    datasets: [{
      label: 'Team Progress',
      data: [320, 670, 210],
      backgroundColor: [
        '#F76161',
        '#6489A0',
        '#0CB18B',
      ],
      borderWidth: 1,
      borderRadius: 6,
      barPercentage: .2,
    }]
  },
  options: {
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        enabled: false,
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    },
    maintainAspectRatio: false,
    scales: {
      y: {
        display: false,
        stacked: true,
        grid: {
          display: false,
        },
        ticks: {
          display: false,
        },
      },
      x: {
        display: false,
        grid: {
          display: false
        },
        ticks: {
          display: false,
        },
      }
    }
  }
});


//////////////////////// Projects //////////////////////////////
const ctx4 = document.getElementById('progressChart').getContext('2d');
const progressChartSection = new Chart(ctx4, {
  type: 'bar',
  data: {
    labels: ['Progress'],
    datasets: [{
      label: '',
      data: [75],
      backgroundColor: [
        '#306DB8',
        'gray',
      ],
      borderWidth: 1,
      borderRadius: 6,
      borderSkipped: false,
      barPercentage: 1,
    }]
  },
  options: {
    indexAxis: 'y',
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        enabled: false,
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    },
    maintainAspectRatio: false,
    scales: {
      y: {
        display: false,
        stacked: true,
        grid: {
          display: false,
          drawBorder: false,
        },
        ticks: {
          display: false,
        },
      },
      x: {
        display: false,
        min: 0,
        max: 100,
        ticks: {
          stepSize: 10
        },
        grid: {
          display: false,
          drawBorder: false,
        },
      }
    }
  }
});
