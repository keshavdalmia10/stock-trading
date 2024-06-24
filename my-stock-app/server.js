const express = require('express');
const puppeteer = require('puppeteer');
const fetch = require('node-fetch');
const { RSI, MACD, ATR } = require('technicalindicators');
const sharp = require('sharp');
const fs = require('fs');

const app = express();
const port = 3000;

const generateChart = async (symbol, indicatorType, data, interval) => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    let chartScript = '';

    const formatTime = (time) => {
        const date = new Date(time * 1000);
        return date.toLocaleDateString();
    };

    const getWatermarkText = (baseText) => {
        return `${baseText} - ${interval}`;
    };

    switch (indicatorType) {
        case 'candlestick':
            chartScript = `
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Candlestick Chart</title>
                    <style>
                        body, html { margin: 0; padding: 0; height: 100%; }
                        #chart { width: 100%; height: 100%; }
                    </style>
                    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
                </head>
                <body>
                    <div id="chart"></div>
                    <script>
                        const chart = LightweightCharts.createChart(document.getElementById('chart'), { width: 800, height: 300 });
                        chart.applyOptions({
                            layout: { textColor: '#000' },
                            watermark: { color: 'blue', visible: true, text: '${getWatermarkText("Candlestick")}', fontSize: 24, horzAlign: 'left', vertAlign: 'top' },
                            timeScale: { timeVisible: true, timeFormatter: ${formatTime.toString()} }
                        });
                        const candleSeries = chart.addCandlestickSeries();
                        candleSeries.setData(${JSON.stringify(data)});
                    </script>
                </body>
                </html>
            `;
            break;
        case 'volume':
            chartScript = `
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Volume Chart</title>
                    <style>
                        body, html { margin: 0; padding: 0; height: 100%; }
                        #chart { width: 100%; height: 100%; }
                    </style>
                    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
                </head>
                <body>
                    <div id="chart"></div>
                    <script>
                        const chart = LightweightCharts.createChart(document.getElementById('chart'), { width: 800, height: 300 });
                        chart.applyOptions({
                            layout: { textColor: '#000' },
                            watermark: { color: 'green', visible: true, text: '${getWatermarkText("Volume")}', fontSize: 24, horzAlign: 'left', vertAlign: 'top' },
                            timeScale: { timeVisible: true, timeFormatter: ${formatTime.toString()} }
                        });
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
                    </script>
                </body>
                </html>
            `;
            break;
        case 'atr':
            chartScript = `
                <!DOCTYPE html>
                <html>
                <head>
                    <title>ATR Chart (14)</title>
                    <style>
                        body, html { margin: 0; padding: 0; height: 100%; }
                        #chart { width: 100%; height: 100%; }
                    </style>
                    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
                </head>
                <body>
                    <div id="chart"></div>
                    <script>
                        const chart = LightweightCharts.createChart(document.getElementById('chart'), { width: 800, height: 300 });
                        chart.applyOptions({
                            layout: { textColor: '#000' },
                            watermark: { color: 'red', visible: true, text: '${getWatermarkText("ATR")}', fontSize: 24, horzAlign: 'left', vertAlign: 'top' },
                            timeScale: { timeVisible: true, timeFormatter: ${formatTime.toString()} }
                        });
                        const atrSeries = chart.addLineSeries({
                            color: 'red',
                            lineWidth: 1,
                            priceScaleId: '',
                        });
                        atrSeries.setData(${JSON.stringify(data)});
                    </script>
                </body>
                </html>
            `;
            break;
        case 'rsi':
            chartScript = `
                <!DOCTYPE html>
                <html>
                <head>
                    <title>RSI Chart (14)</title>
                    <style>
                        body, html { margin: 0; padding: 0; height: 100%; }
                        #chart { width: 100%; height: 100%; }
                    </style>
                    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
                </head>
                <body>
                    <div id="chart"></div>
                    <script>
                        const chart = LightweightCharts.createChart(document.getElementById('chart'), { width: 800, height: 300 });
                        chart.applyOptions({
                            layout: { textColor: '#000' },
                            watermark: { color: 'purple', visible: true, text: '${getWatermarkText("RSI")}', fontSize: 24, horzAlign: 'left', vertAlign: 'top' },
                            timeScale: { timeVisible: true, timeFormatter: ${formatTime.toString()} }
                        });
                        const rsiSeries = chart.addLineSeries({
                            color: 'purple',
                            lineWidth: 2,
                            priceScaleId: '',
                        });
                        rsiSeries.setData(${JSON.stringify(data)});
                    </script>
                </body>
                </html>
            `;
            break;
        case 'macd':
            chartScript = `
                <!DOCTYPE html>
                <html>
                <head>
                    <title>MACD Chart (12, 26)</title>
                    <style>
                        body, html { margin: 0; padding: 0; height: 100%; }
                        #chart { width: 100%; height: 100%; }
                    </style>
                    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
                </head>
                <body>
                    <div id="chart"></div>
                    <script>
                        const chart = LightweightCharts.createChart(document.getElementById('chart'), { width: 800, height: 300 });
                        chart.applyOptions({
                            layout: { textColor: '#000' },
                            watermark: { color: 'blue', visible: true, text: '${getWatermarkText("MACD")}', fontSize: 24, horzAlign: 'left', vertAlign: 'top' },
                            timeScale: { timeVisible: true, timeFormatter: ${formatTime.toString()} }
                        });
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
                    </script>
                </body>
                </html>
            `;
            break;
    }

    await page.setContent(chartScript);
    await page.waitForSelector('#chart');
    const chart = await page.$('#chart');
    const screenshotPath = `./${symbol}-${indicatorType}-${interval}.png`;
    await chart.screenshot({ path: screenshotPath });
    await browser.close();

    return screenshotPath;
};

const fetchStockDataFromAPI = async (symbol, period, interval) => {
    const response = await fetch(`https://stock-trading-flask-13fc31362bcf.herokuapp.com/api/data/${symbol}/${period}/${interval}`);
    const data = await response.json();
    return data;
};

app.get('/generate-chart/:symbol/:period/:interval', async (req, res) => {
    const { symbol, period, interval } = req.params;

    try {
        const stockData = await fetchStockDataFromAPI(symbol, period, interval);

        const chartData = stockData.map(entry => ({
            time: new Date(entry.Datetime).getTime() / 1000,
            open: entry.Open,
            high: entry.High,
            low: entry.Low,
            close: entry.Close
        }));

        const volumeData = stockData.map(entry => ({
            time: new Date(entry.Datetime).getTime() / 1000,
            value: entry.Volume
        }));

        const closes = stockData.map(entry => entry.Close);
        const highs = stockData.map(entry => entry.High);
        const lows = stockData.map(entry => entry.Low);

        const rsi = RSI.calculate({ values: closes, period: 14 });
        const atr = ATR.calculate({ high: highs, low: lows, close: closes, period: 14 });

        const rsiData = chartData.slice(14).map((entry, index) => ({
            time: entry.time,
            value: rsi[index]
        }));

        const atrData = chartData.slice(14).map((entry, index) => ({
            time: entry.time,
            value: atr[index]
        }));

        const candlestickPath = await generateChart(symbol, 'candlestick', chartData, interval);
        const volumePath = await generateChart(symbol, 'volume', volumeData, interval);
        const atrPath = await generateChart(symbol, 'atr', atrData, interval);
        const rsiPath = await generateChart(symbol, 'rsi', rsiData, interval);

        let macdPath;
        let macdData;

        if (!(interval === '15m' && period === '1d')) {
            const macd = MACD.calculate({
                values: closes,
                fastPeriod: 12,
                slowPeriod: 26,
                signalPeriod: 9,
                SimpleMAOscillator: false,
                SimpleMASignal: false
            });

            macdData = {
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

            macdPath = await generateChart(symbol, 'macd', macdData, interval);
        }

        // Composite images conditionally
        let compositeElements = [
            { input: candlestickPath, top: 0, left: 0 },
            { input: volumePath, top: 300, left: 0 },
            { input: atrPath, top: 600, left: 0 },
            { input: rsiPath, top: 900, left: 0 },
        ];

        let currentHeight = 1200;
        if (macdPath) {
            compositeElements.push({ input: macdPath, top: currentHeight, left: 0 });
            currentHeight += 300;
        }

        const combinedImage = await sharp({
            create: {
                width: 800,
                height: currentHeight,
                channels: 4,
                background: { r: 255, g: 255, b: 255, alpha: 1 }
            }
        })
        .composite(compositeElements)
        .png()
        .toBuffer();

        // Write the combined image to a file
        const combinedImagePath = `./${symbol}-${interval}-chart.png`;
        await fs.promises.writeFile(combinedImagePath, combinedImage);
        const filesToDelete = [candlestickPath, volumePath, atrPath, rsiPath];
        if (macdPath) filesToDelete.push(macdPath);
        await Promise.all(filesToDelete.map(file => fs.promises.unlink(file)));
        res.sendFile(combinedImagePath, { root: __dirname });
    } catch (error) {
        console.error('Failed to fetch data or generate chart:', error);
        res.status(500).send('Failed to generate chart.');
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
