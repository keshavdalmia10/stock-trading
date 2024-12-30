const express = require('express');
const puppeteer = require('puppeteer');
const fetch = require('node-fetch');
const fs = require('fs');
const sharp = require('sharp');

const app = express();
const port = 3000;

const generateChart = async (symbol, indicatorType, data, interval, height = 300) => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    const formatTime = (time) => {
        const date = new Date(time * 1000);
        return date.toLocaleDateString();
    };

    const getWatermarkText = (baseText) => {
        return `${baseText} - ${interval}`;
    };

    let chartScript = `
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
            <div id="chart" style="height: ${height}px;"></div>
            <script>
                const chart = LightweightCharts.createChart(document.getElementById('chart'), { width: 800, height: ${height} });
                chart.applyOptions({
                    layout: { textColor: '#000' },
                    watermark: { color: '${indicatorType === 'candlestick' ? 'blue' : 'green'}', visible: true, text: '${getWatermarkText(indicatorType)}', fontSize: 24, horzAlign: 'left', vertAlign: 'top' },
                    timeScale: { timeVisible: true, timeFormatter: ${formatTime.toString()} }
                });
                const series = chart.add${indicatorType === 'candlestick' ? 'Candlestick' : 'Histogram'}Series({
                    color: '${indicatorType === 'volume' ? 'rgba(76, 175, 80, 0.5)' : 'undefined'}',
                    priceFormat: { type: '${indicatorType === 'volume' ? 'volume' : 'undefined'}' },
                    priceScaleId: '',
                    scaleMargins: {
                        top: 0.9,
                        bottom: 0,
                    },
                });
                series.setData(${JSON.stringify(data)});
            </script>
        </body>
        </html>
    `;

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

        const candlestickPath = await generateChart(symbol, 'candlestick', chartData, interval, 450);
        const volumePath = await generateChart(symbol, 'volume', volumeData, interval, 150);

        const combinedImage = await sharp({
            create: {
                width: 800,
                height: 600, // Adjusted height for compositing
                channels: 4,
                background: { r: 255, g: 255, b: 255, alpha: 1 }
            }
        })
        .composite([
            { input: candlestickPath, top: 0, left: 0 },
            { input: volumePath, top: 450, left: 0 } // Adjusted top position
        ])
        .png()
        .toBuffer();

        const combinedImagePath = `./${symbol}-${interval}-chart.png`;
        await fs.promises.writeFile(combinedImagePath, combinedImage);
        const filesToDelete = [candlestickPath, volumePath];
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
