import React, { useEffect, useRef, useState } from 'react';
import Highcharts from 'highcharts';

const HopperChart = () => {
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
      .then(config => setWsUrl(config.webSockets.hopperLevel))
      .catch(error => console.error('Error loading config:', error));
  }, []);

  useEffect(() => {
    if (!wsUrl) return;

    let ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (Array.isArray(data)) {
        const hopperLevel = data.map(item => ({
          x: new Date(item.timestamp).getTime(),
          y: item.hopper_level
        }));
        const rotationalCurrent = data.map(item => ({
          x: new Date(item.timestamp).getTime(),
          y: item.rotational_pulling_current
        }));

        const numNewRecords = hopperLevel.length;

        if (chart !== null && chart.series !== undefined) {
          const series1 = chart.series[0];
          const series2 = chart.series[1];

          // Remove the first `numNewRecords` points
          for (let i = 0; i < numNewRecords && series1.data.length > 0; i++) {
            series1.data[0].remove(false);
            series2.data[0].remove(false);
          }

          // Add the new `numNewRecords` points
          hopperLevel.forEach(point => {
            series1.addPoint(point, false);
          });
          rotationalCurrent.forEach(point => {
            series2.addPoint(point, false);
          });

          chart.redraw();
        } else {
          setChart(Highcharts.chart(chartRef.current, {
            chart: {
              type: 'line',
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
              text: 'Hopper Level',
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
            yAxis: [{
              title: {
                text: 'Hopper Level',
                style: {
                  color: '#E0E0E3'
                }
              },
              opposite: true,
              gridLineColor: '#707073',
              labels: {
                style: {
                  color: '#E0E0E3'
                }
              }
            }, {
              title: {
                text: 'Rotational Valve Position',
                style: {
                  color: '#E0E0E3'
                }
              },
              gridLineColor: '#707073',
              labels: {
                style: {
                  color: '#E0E0E3'
                }
              }
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
              name: 'Hopper Level',
              data: hopperLevel,
              yAxis: 0,
              color: '#FFFFFF' // Ensure the series lines are white
            }, {
              name: 'Rotational Valve Position',
              data: rotationalCurrent,
              yAxis: 1,
              color: '#FFFFFF' // Ensure the series lines are white
            }]
          }));
        }
      } else {
        const time = new Date(data.timestamp).getTime();
        const hopperLevel = data.hopper_level;
        const rotationalCurrent = data.rotational_pulling_current;

        if (chart && chart.series.length === 2) {
          const series1 = chart.series[0];
          const series2 = chart.series[1];

          series1.addPoint({
            x: time,
            y: hopperLevel
          }, true, series1.data.length >= 100);

          series2.addPoint({
            x: time,
            y: rotationalCurrent
          }, true, series2.data.length >= 100);
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

  return <div ref={chartRef} style={{ width: '100%', height: '100%', minHeight: '400px' }} />;
};

export default HopperChart;
