import React, { useEffect, useRef, useState } from 'react';
import Highcharts from 'highcharts';

const PullingLineChart = () => {
  const chartRef = useRef(null);
  const [chart, setChart] = useState(null);
  const [wsUrl, setWsUrl] = useState('');

  useEffect(() => {
    fetch('config.json')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(config => setWsUrl(config.webSockets.pullingRoller))
      .catch(error => console.error('Error loading config:', error));
  }, []);

  useEffect(() => {
    if (!wsUrl) return;

    let ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (Array.isArray(data)) {
        const pullingservo = data.map(item => ({
          x: new Date(item.timestamp).getTime(),
          y: item.pulling_servo_motor_current
        }));
        const cam = data.map(item => ({
          x: new Date(item.timestamp).getTime(),
          y: item.cam
        }));

        if (chart) {
          const series1 = chart.series[0];
          const series2 = chart.series[1];

          // Ensure series1 and series2 exist
          if (series1 && series2) {
            // Remove old points if the number of new records exceeds the limit
            const numPointsToRemove = 100;
            if (series1.data.length >= numPointsToRemove) {
              for (let i = 0; i < numPointsToRemove; i++) {
                series1.data[0]?.remove(false);
                series2.data[0]?.remove(false);
              }
            }

            // Add new points
            pullingservo.forEach(point => series1.addPoint(point, false));
            cam.forEach(point => series2.addPoint(point, false));

            chart.redraw();
          }
        } else {
          setChart(createChart(pullingservo, cam));
        }
      } else {
        const time = new Date(data.timestamp).getTime();
        const pullingservo = data.pulling_servo_motor_current;
        const cam = data.cam;

        if (chart && chart.series.length === 2) {
          const series1 = chart.series[0];
          const series2 = chart.series[1];

          series1.addPoint({ x: time, y: pullingservo }, true, series1.data.length >= 100);
          series2.addPoint({ x: time, y: cam }, true, series2.data.length >= 100);
        }
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket closed, attempting to reconnect...');
      setTimeout(() => {
        ws = new WebSocket(wsUrl);
      }, 2000);
    };

    return () => {
      ws.close();
    };
  }, [wsUrl, chart]);

  const createChart = (pullingservo, cam) => {
    return Highcharts.chart(chartRef.current, {
      chart: {
        type: 'line',
        animation: false,
        backgroundColor: '#2a2a2b',
        style: {
          fontFamily: 'Lato'
        }
      },
      credits: {
        enabled: false,
      },
      title: {
        text: 'Pulling',
        style: {
          color: '#E0E0E3'
        }
      },
      xAxis: {
        type: 'datetime',
        labels: {
          formatter: function() {
            return Highcharts.dateFormat('%H:%M:%S', this.value);
          },
          style: {
            color: '#E0E0E3'
          }
        },
        lineColor: '#707073',
        tickColor: '#707073',
      },
      yAxis: [{
        title: {
          text: 'Pulling Servo Motor Current',
          style: {
            color: '#E0E0E3'
          }
        },
        min: 0,
        max: 10,
        opposite: true,
        gridLineColor: '#707073',
        labels: {
          style: {
            color: '#E0E0E3'
          }
        },
      }, {
        title: {
          text: 'Virtual Access Master Position',
          style: {
            color: '#E0E0E3'
          }
        },
        min: 0,
        max: 360,
        gridLineColor: '#707073',
        labels: {
          style: {
            color: '#E0E0E3'
          }
        },
        opposite: false
      }],
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
        style: {
          color: '#F0F0F0'
        }
      },
      plotOptions: {
        line: {
          dataLabels: {
            color: '#F0F0F3'
          },
          marker: {
            enabled: false  // Disable markers
          }
        }
      },
      legend: {
        itemStyle: {
          color: '#E0E0E3'
        },
        itemHoverStyle: {
          color: '#FFF'
        },
        itemHiddenStyle: {
          color: '#606063'
        }
      },
      series: [{
        name: 'Pulling Servo Motor Current',
        data: pullingservo,
        yAxis: 0
      }, {
        name: 'Virtual Access Master Position',
        data: cam,
        yAxis: 1
      }]
    });
  };

  return <div ref={chartRef} />;
};

export default PullingLineChart;
