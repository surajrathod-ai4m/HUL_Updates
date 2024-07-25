import React, { useEffect, useRef, useState } from 'react';
import Highcharts from 'highcharts';

const VerticalLineChart = ({ id, wsUrl, chartTitle, seriesOptions }) => {
  const chartRef = useRef(null);
  const [chart, setChart] = useState(null);

  const initializeChart = (seriesDataArray) => {
    const series = seriesOptions.map((option, index) => ({
      name: option.name,
      data: seriesDataArray[index]
    }));

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
        text: chartTitle,
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
            // color: '#E0E0E3'
            color: '#FFFFFF'
          }
        },
        lineColor: '#707073',
        tickColor: '#707073'
      },
      yAxis: {
        title: {
          text: 'Values',
          style: {
            // color: '#E0E0E3'
            color: '#FFFFFF'
          }
        },
        gridLineColor: '#707073',
        labels: {
          style: {
            color: '#E0E0E3'
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
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
        style: {
          color: '#F0F0F0'
        }
      },
      plotOptions: {
        series: {
          dataLabels: {
            color: '#F0F0F3'
          },
          marker: {
            lineColor: '#333'
          }
        },
        boxplot: {
          fillColor: '#505053'
        },
        candlestick: {
          lineColor: 'white'
        },
        errorbar: {
          color: 'white'
        }
      },
      series
    }));
  };

  useEffect(() => {
    let ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (Array.isArray(data)) {
        const seriesDataArray = seriesOptions.map(option => data.map(item => ({
          x: new Date(item.timestamp).getTime(),
          y: item[option.key]
        })));

        if (chart !== null && chart.series !== undefined) {
          chart.series.forEach((series, index) => {
            series.setData(seriesDataArray[index], true);
          });
        } else {
          initializeChart(seriesDataArray);
        }
      } else {
        const time = new Date(data.timestamp).getTime();

        if (chart && chart.series.length === seriesOptions.length) {
          seriesOptions.forEach((option, index) => {
            const value = data[option.key];
            chart.series[index].addPoint({ x: time, y: value }, true, chart.series[index].data.length >= 100);
          });
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
  }, [wsUrl, seriesOptions, chartTitle, chart]);

  return <div ref={chartRef} id={id} />;
};

export default VerticalLineChart;
