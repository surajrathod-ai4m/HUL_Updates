// import React, { useEffect, useRef, useState } from 'react';
// import Highcharts from 'highcharts';
// import HighchartsReact from 'highcharts-react-official';

// const HorizontalSealerLineChart = () => {
//   const chartRef = useRef(null);
//   const [options, setOptions] = useState(null);
//   const [wsUrl, setWsUrl] = useState('');

//   useEffect(() => {
//     fetch('config.json')
//       .then(response => {
//         if (!response.ok) {
//           throw new Error('Network response was not ok');
//         }
//         return response.json();
//       })
//       .then(config => setWsUrl(config.webSockets.horizontalSealer))
//       .catch(error => console.error('Error loading config:', error));
//   }, []);

//   useEffect(() => {
//     if (!wsUrl) return;

//     let ws = new WebSocket(wsUrl);

//     ws.onmessage = (event) => {
//       const data = JSON.parse(event.data);
//       console.log("data horizontal data",data)
//       if (Array.isArray(data)) {
//         const seriesData = ['cam_position', 'hor_sealer_pressure', 'horizontal_sealing_time', 'hoz_sealer_servo_current', 'hoz_temp'].map(key => ({
//           name: key.charAt(0).toUpperCase() + key.slice(1),
//           data: data.map(item => ({
//             x: new Date(item.timestamp).getTime(),
//             y: item[`${key}`]
//           }))
//         }));

//         setOptions(prevOptions => ({
//           ...prevOptions,
//           series: seriesData
//         }));
//       } else {
//         const time = new Date(data.timestamp).getTime();
//         setOptions(prevOptions => ({
//           ...prevOptions,
//           series: prevOptions.series.map((series, index) => ({
//             ...series,
//             data: [
//               ...series.data.slice(-99),
//               { x: time, y: data[`hoz_${series.name.toLowerCase()}`] }
//             ]
//           }))
//         }));
//       }
//     };

//     ws.onerror = (error) => console.error('WebSocket error:', error);

//     ws.onclose = () => {
//       console.log('WebSocket closed, attempting to reconnect...');
//       setTimeout(() => { ws = new WebSocket(wsUrl); }, 2000);
//     };

//     setOptions({
//       chart: {
//         type: 'spline',
//         animation: false,
//         backgroundColor: '#2a2a2b',
//         style: {
//           fontFamily: 'Lato'
//         },
//       },
//       credits: { enabled: false },
//       title: {
//         text: 'Horizontal Sealer Data',
//         style: { color: '#E0E0E3' }
//       },
//       xAxis: {
//         type: 'datetime',
//         labels: {
//           formatter: function() { return Highcharts.dateFormat('%H:%M:%S', this.value); },
//           style: { color: '#E0E0E3' }
//         },
//         lineColor: '#707073',
//         tickColor: '#707073',
//       },
//       yAxis: [{
//         title: { text: 'Current / Pressure', style: { color: '#E0E0E3' } },
//         min: 0,
//         max: 6,
//         opposite: true,
//         gridLineColor: '#707073',
//         labels: { style: { color: '#E0E0E3' } },
//       }, {
//         title: { text: 'Temperature / CAM / Sealing Time', style: { color: '#E0E0E3' } },
//         min: 0,
//         max: 360,
//         gridLineColor: '#707073',
//         labels: { style: { color: '#E0E0E3' } },
//       }],
//       tooltip: {
//         backgroundColor: 'rgba(0, 0, 0, 0.85)',
//         style: { color: '#F0F0F0' }
//       },
//       plotOptions: {
//         line: {
//           dataLabels: { color: '#F0F0F3' },
//           marker: { lineColor: '#333' }
//         }
//       },
//       legend: {
//         itemStyle: { color: '#E0E0E3' },
//         itemHoverStyle: { color: '#FFF' },
//         itemHiddenStyle: { color: '#606063' }
//       },
//       series: []
//     });

//     return () => { ws.close(); };
//   }, [wsUrl]);

//   return (
//     <div style={{ width: '100%', height: '100%', minHeight: '400px' }}>
//       {options && (
//         <HighchartsReact
//           highcharts={Highcharts}
//           options={options}
//           ref={chartRef}
//           containerProps={{ style: { width: '100%', height: '100%' } }}
//         />
//       )}
//     </div>
//   );
// };

// export default HorizontalSealerLineChart;

import React, { useEffect, useRef, useState } from 'react';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';

const HorizontalSealerLineChart = () => {
  const chartRef = useRef(null);
  const [options, setOptions] = useState(null);
  const [wsUrl, setWsUrl] = useState('');

  useEffect(() => {
    fetch('config.json')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(config => setWsUrl(config.webSockets.horizontalSealer))
      .catch(error => console.error('Error loading config:', error));
  }, []);

  useEffect(() => {
    if (!wsUrl) return;

    let ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("data horizontal data", data);
      if (Array.isArray(data)) {
        const seriesData = ['cam_position', 'hor_sealer_pressure', 'horizontal_sealing_time', 'hoz_sealer_servo_current', 'hoz_temp'].map(key => ({
          name: key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' '),
          data: data.map(item => ({
            x: new Date(item.timestamp).getTime(),
            y: item[key]
          })),
          yAxis: ['cam_position', 'horizontal_sealing_time', 'hoz_temp'].includes(key) ? 1 : 0  // Assign y-axis
        }));

        setOptions(prevOptions => ({
          ...prevOptions,
          series: seriesData
        }));
      } else {
        const time = new Date(data.timestamp).getTime();
        setOptions(prevOptions => ({
          ...prevOptions,
          series: prevOptions.series.map((series) => ({
            ...series,
            data: [
              ...series.data.slice(-99),
              { x: time, y: data[`hoz_${series.name.toLowerCase().replace(' ', '_')}`] }
            ]
          }))
        }));
      }
    };

    ws.onerror = (error) => console.error('WebSocket error:', error);

    ws.onclose = () => {
      console.log('WebSocket closed, attempting to reconnect...');
      setTimeout(() => { ws = new WebSocket(wsUrl); }, 2000);
    };

    setOptions({
      chart: {
        type: 'spline',
        animation: false,
        backgroundColor: '#2a2a2b',
        style: {
          fontFamily: 'Lato'
        },
      },
      credits: { enabled: false },
      title: {
        text: 'Horizontal Sealer Data',
        style: { color: '#E0E0E3' }
      },
      xAxis: {
        type: 'datetime',
        labels: {
          formatter: function() { return Highcharts.dateFormat('%H:%M:%S', this.value); },
          style: { color: '#E0E0E3' }
        },
        lineColor: '#707073',
        tickColor: '#707073',
      },
      yAxis: [{
        title: { text: 'Current / Pressure', style: { color: '#E0E0E3' } },
        min: 0,
        max: 12,
        opposite: true,
        gridLineColor: '#707073',
        labels: { style: { color: '#E0E0E3' } },
      }, {
        title: { text: 'Temperature / CAM / Sealing Time', style: { color: '#E0E0E3' } },
        min: 0,
        max: 400,
        gridLineColor: '#707073',
        labels: { style: { color: '#E0E0E3' } },
      }],
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
        style: { color: '#F0F0F0' }
      },
      plotOptions: {
        line: {
          dataLabels: { color: '#F0F0F3' },
          marker: { enabled: false } 
        }
      },
      legend: {
        itemStyle: { color: '#E0E0E3' },
        itemHoverStyle: { color: '#FFF' },
        itemHiddenStyle: { color: '#606063' }
      },
      series: []
    });

    return () => { ws.close(); };
  }, [wsUrl]);

  return (
    <div style={{ width: '100%', height: '100%', minHeight: '400px' }}>
      {options && (
        <HighchartsReact
          highcharts={Highcharts}
          options={options}
          ref={chartRef}
          containerProps={{ style: { width: '100%', height: '100%' } }}
        />
      )}
    </div>
  );
};

export default HorizontalSealerLineChart;
