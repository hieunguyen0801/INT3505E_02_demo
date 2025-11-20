const express = require('express');
const app = express();
const PORT = 3000;
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

app.listen(PORT, () => {
    logger.info(`Payment service is running on port ${PORT}`);
});

//chạy ứng dụng với lệnh: node src/app.js