import React, { useEffect, useRef, useState } from 'react';
import Highcharts from 'highcharts';

const LaminateLineChart = () => {
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
      .then(config => setWsUrl(config.webSockets.laminateCof))
      .catch(error => console.error('Error loading config:', error));
  }, []);

  useEffect(() => {
    if (!wsUrl) return;

    let ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (Array.isArray(data)) {
        const laminateCofData = data.map(item => ({
          x: new Date(item.timestamp).getTime(),
          y: item.laminate_cof_value
        }));
        const servoMotorCurrentData = data.map(item => ({
          x: new Date(item.timestamp).getTime(),
          y: item.pulling_servo_motor_current
        }));

        if (chart && chart.series.length === 2) {
          const series1 = chart.series[0];
          const series2 = chart.series[1];

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
            laminateCofData.forEach(point => series1.addPoint(point, false));
            servoMotorCurrentData.forEach(point => series2.addPoint(point, false));

            chart.redraw();
          } else {
            console.error('Series not found');
          }
        } else {
          setChart(createChart(laminateCofData, servoMotorCurrentData));
        }
      } else {
        const time = new Date(data.timestamp).getTime();
        const laminateCofValue = data.laminate_cof_value;
        const pullingServoMotorCurrent = data.pulling_servo_motor_current;

        if (chart && chart.series.length === 2) {
          const series1 = chart.series[0];
          const series2 = chart.series[1];

          if (series1 && series2) {
            series1.addPoint({ x: time, y: laminateCofValue }, true, series1.data.length >= 100);
            series2.addPoint({ x: time, y: pullingServoMotorCurrent }, true, series2.data.length >= 100);
          } else {
            console.error('Series not found');
          }
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

  const createChart = (laminateCofData, servoMotorCurrentData) => {
    return Highcharts.chart(chartRef.current, {
      chart: {
        type: 'spline',
        animation: false,
        backgroundColor: '#2a2a2b',
        style: {
          fontFamily: 'Lato'
        }
      },
      credits: {
        enabled: false
      },
      title: {
        text: 'Laminate COF Data',
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
        tickColor: '#707073'
      },
      yAxis: {
        title: {
          text: 'Values',
          style: {
            color: '#E0E0E3'
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
        style: {
          color: '#F0F0F0'
        },
        formatter: function() {
          if (this.series) {
            return `<b>${this.series.name}</b><br/>Time: ${Highcharts.dateFormat('%H:%M:%S', this.x)}<br/>Value: ${this.y}`;
          } else {
            console.error('Tooltip formatter error: this.series is undefined');
            return '';
          }
        }
      },
      plotOptions: {
        spline: {
          dataLabels: {
            color: '#F0F0F3'
          },
          marker: {
            lineColor: '#333'
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
        name: 'Laminate COF',
        data: laminateCofData
      }, {
        name: 'Pulling Servo Motor Current',
        data: servoMotorCurrentData
      }]
    });
  };

  return <div ref={chartRef} />;
};

export default LaminateLineChart;
