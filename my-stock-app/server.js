const express = require('express');
const puppeteer = require('puppeteer');
const fetch = require('node-fetch');
const { RSI, MACD, ATR } = require('technicalindicators');
const sharp = require('sharp');
const fs = require('fs');

const app = express();
const port = 3000;

const formatDateForChart = (date) => {
    if (!date) return null;
    if (date instanceof Date) {
        return date.toISOString().split('T')[0];
    } else if (typeof date === 'string') {
        return date.split('T')[0];
    }
    return date;
};

const generateChart = async (symbol, indicatorType, data) => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    let chartScript = '';

    switch (indicatorType) {
        case 'candlestick':
            chartScript = `
                const chart = LightweightCharts.createChart(document.getElementById('chart'), { width: 800, height: 300 });
                const candleSeries = chart.addCandlestickSeries();
                candleSeries.setData(${JSON.stringify(data)});
            `;
            break;
        case 'volume':
            chartScript = `
                const chart = LightweightCharts.createChart(document.getElementById('chart'), { width: 800, height: 300 });
                const volumeSeries = chart.addHistogramSeries({
                    color: 'rgba(76, 175, 80, 0.5)',
                    priceFormat: {
                        type: 'volume',
                    },
                    priceScaleId: '',
                    scaleMargins: {
                        top: 0.9,
                        bottom: 0,
                    },
                });
                volumeSeries.setData(${JSON.stringify(data)});
            `;
            break;
        case 'atr':
            chartScript = `
                const chart = LightweightCharts.createChart(document.getElementById('chart'), { width: 800, height: 300 });
                const atrSeries = chart.addLineSeries({
                    color: 'red',
                    lineWidth: 1,
                    priceScaleId: '',
                });
                atrSeries.setData(${JSON.stringify(data)});
            `;
            break;
        case 'rsi':
            chartScript = `
                const chart = LightweightCharts.createChart(document.getElementById('chart'), { width: 800, height: 300 });
                const rsiSeries = chart.addLineSeries({
                    color: 'purple',
                    lineWidth: 2,
                    priceScaleId: '',
                });
                rsiSeries.setData(${JSON.stringify(data)});
            `;
            break;
        case 'macd':
            chartScript = `
                const chart = LightweightCharts.createChart(document.getElementById('chart'), { width: 800, height: 300 });
                const macdLineSeries = chart.addLineSeries({
                    color: 'blue',
                    lineWidth: 1,
                    priceScaleId: '',
                });
                macdLineSeries.setData(${JSON.stringify(data.macdLine)});

                const signalLineSeries = chart.addLineSeries({
                    color: 'orange',
                    lineWidth: 1,
                    priceScaleId: '',
                });
                signalLineSeries.setData(${JSON.stringify(data.signalLine)});

                const histogramSeries = chart.addHistogramSeries({
                    color: 'rgba(255, 0, 0, 0.5)',
                    lineWidth: 1,
                    priceScaleId: '',
                });
                histogramSeries.setData(${JSON.stringify(data.histogram)});
            `;
            break;
    }

    await page.setContent(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>${indicatorType} Chart</title>
            <style>
                body, html { margin: 0; padding: 0; height: 100%; }
                #chart { width: 100%; height: 100%; }
            </style>
            <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
        </head>
        <body>
            <div id="chart"></div>
            <script>
                ${chartScript}
            </script>
        </body>
        </html>
    `);

    await page.waitForSelector('#chart');
    const chart = await page.$('#chart');
    const screenshotPath = `./${symbol}-${indicatorType}.png`;
    await chart.screenshot({ path: screenshotPath });
    await browser.close();

    return screenshotPath;
};

const fetchStockDataFromAPI = async (symbol) => {
    const response = await fetch(`http://127.0.0.1:5000/api/data/${symbol}`);
    const data = await response.json();
    return data;
};

app.get('/generate-chart/:symbol', async (req, res) => {
    const symbol = req.params.symbol;

    try {
        const stockData = await fetchStockDataFromAPI(symbol);

        const chartData = stockData.map(entry => ({
            time: formatDateForChart(new Date(entry.Datetime)),
            open: entry.Open,
            high: entry.High,
            low: entry.Low,
            close: entry.Close
        }));

        const volumeData = stockData.map(entry => ({
            time: formatDateForChart(new Date(entry.Datetime)),
            value: entry.Volume
        }));

        const closes = stockData.map(entry => entry.Close);
        const highs = stockData.map(entry => entry.High);
        const lows = stockData.map(entry => entry.Low);

        const rsi = RSI.calculate({ values: closes, period: 14 });
        const macd = MACD.calculate({
            values: closes,
            fastPeriod: 12,
            slowPeriod: 26,
            signalPeriod: 9,
            SimpleMAOscillator: false,
            SimpleMASignal: false
        });
        const atr = ATR.calculate({ high: highs, low: lows, close: closes, period: 14 });

        const rsiData = chartData.slice(14).map((entry, index) => ({
            time: entry.time,
            value: rsi[index]
        }));

        const macdData = {
            macdLine: chartData.slice(26).map((entry, index) => ({
                time: entry.time,
                value: macd[index].MACD
            })),
            signalLine: chartData.slice(26).map((entry, index) => ({
                time: entry.time,
                value: macd[index].signal
            })),
            histogram: chartData.slice(26).map((entry, index) => ({
                time: entry.time,
                value: macd[index].histogram,
                color: macd[index].histogram >= 0 ? 'rgba(0, 150, 136, 0.5)' : 'rgba(255, 0, 0, 0.5)'
            }))
        };

        const atrData = chartData.slice(14).map((entry, index) => ({
            time: entry.time,
            value: atr[index]
        }));

        const candlestickPath = await generateChart(symbol, 'candlestick', chartData);
        const volumePath = await generateChart(symbol, 'volume', volumeData);
        const atrPath = await generateChart(symbol, 'atr', atrData);
        const rsiPath = await generateChart(symbol, 'rsi', rsiData);
        const macdPath = await generateChart(symbol, 'macd', macdData);

        // Combine images using sharp
        const combinedImage = await sharp({
            create: {
                width: 800,
                height: 1500,
                channels: 4,
                background: { r: 255, g: 255, b: 255, alpha: 1 }
            }
        })
        .composite([
            { input: candlestickPath, top: 0, left: 0 },
            { input: volumePath, top: 300, left: 0 },
            { input: atrPath, top: 600, left: 0 },
            { input: rsiPath, top: 900, left: 0 },
            { input: macdPath, top: 1200, left: 0 }
        ])
        .png()
        .toBuffer();

        // Write the combined image to a file
        const combinedImagePath = `./combined-chart.png`;
        await fs.promises.writeFile(combinedImagePath, combinedImage);

        res.sendFile(combinedImagePath, { root: __dirname });
    } catch (error) {
        console.error('Failed to fetch data or generate chart:', error);
        res.status(500).send('Failed to generate chart.');
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
