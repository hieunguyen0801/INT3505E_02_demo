const express = require('express');
const app = express();
const PORT = 3000;
const { register } = require('./metric');
app.use(express.json());
const logger = require('./logger');
const requestLogger = require('./middleware/requestLogger');
app.use(requestLogger);

app.get('/health', (req, res) => {
  logger.info('Health check requested');
  res.status(200).json({ status: 'ok' });
});

const paymentRoutes = require('./routes/payments.routes');
app.use('/payments', paymentRoutes);

app.get('/metrics', async (req, res) => {
  try {
    res.set('Content-Type', register.contentType);
    const metrics = await register.metrics();
    res.send(metrics);
  } catch (err) {
    logger.error('Error generating metrics', { error: err.message });
    res.status(500).send('Error generating metrics');
  }
});


app.listen(PORT, () => {
    logger.info(`Payment service is running on port ${PORT}`);
});

//chạy ứng dụng với lệnh: node src/app.js