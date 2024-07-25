import React, { useEffect, useRef, useState } from 'react';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';

const VerticleSealingLineChart = () => {
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
      .then(config => setWsUrl(config.webSockets.verticalSealer))
      .catch(error => console.error('Error loading config:', error));
  }, []);

  useEffect(() => {
    if (!wsUrl) return;

    let ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (Array.isArray(data)) {
        const pressureData = data.map(item => ({
          x: new Date(item.timestamp).getTime(),
          y: item.ver_pressure
        }));
        const currentData = data.map(item => ({
          x: new Date(item.timestamp).getTime(),
          y: item.ver_current
        }));
        const positionData = data.map(item => ({
          x: new Date(item.timestamp).getTime(),
          y: item.ver_position
        }));
        const camData = data.map(item => ({
          x: new Date(item.timestamp).getTime(),
          y: item.ver_cam
        }));

        const numNewRecords = pressureData.length;

        if (chart !== null && chart.series !== undefined) {
          const series1 = chart.series[0];
          const series2 = chart.series[1];
          const series3 = chart.series[2];
          const series4 = chart.series[3];

          // Remove the first `numNewRecords` points
          for (let i = 0; i < numNewRecords && series1.data.length > 0; i++) {
            series1.data[0].remove(false);
            series2.data[0].remove(false);
            series3.data[0].remove(false);
            series4.data[0].remove(false);
          }

          // Add the new `numNewRecords` points
          pressureData.forEach(point => {
            series1.addPoint(point, false);
          });
          currentData.forEach(point => {
            series2.addPoint(point, false);
          });
          positionData.forEach(point => {
            series3.addPoint(point, false);
          });
          camData.forEach(point => {
            series4.addPoint(point, false);
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
              text: 'Vertical Sealing Data',
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
                text: 'Pressure / Current',
                style: {
                  color: '#FFFFFF'
                }
              },
              min: 0,
              max: 10,
              opposite: true,
              gridLineColor: '#707073',
              labels: { style: { color: '#E0E0E3' } },
            }, {
              title: {
                text: 'Position / CAM',
                style: {
                  color: '#E0E0E3'
                }
              },
              min: 0,
              max: 360,
              gridLineColor: '#707073',
              labels: { style: { color: '#E0E0E3' } },
            }],
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.85)',
              style: { color: '#E0E0E3' }
            },
            series: [{
              name: 'Pressure',
              data: pressureData,
              
            }, {
              name: 'Current',
              data: currentData
            }, {
              name: 'Position',
              data: positionData
            }, {
              name: 'Cam',
              data: camData
            }]
          }));
        }
      } else {
        const time = new Date(data.timestamp).getTime();
        const pressureValue = data.ver_pressure;
        const currentValue = data.ver_current;
        const positionValue = data.ver_position;
        const camValue = data.ver_cam;

        if (chart && chart.series.length === 4) {
          const series1 = chart.series[0];
          const series2 = chart.series[1];
          const series3 = chart.series[2];
          const series4 = chart.series[3];

          series1.addPoint({
            x: time,
            y: pressureValue
          }, true, series1.data.length >= 100);

          series2.addPoint({
            x: time,
            y: currentValue
          }, true, series2.data.length >= 100);

          series3.addPoint({
            x: time,
            y: positionValue
          }, true, series3.data.length >= 100);

          series4.addPoint({
            x: time,
            y: camValue
          }, true, series4.data.length >= 100);
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

export default VerticleSealingLineChart;
