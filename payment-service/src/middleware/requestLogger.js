const logger = require('../logger');
const { httpRequestsTotal } = require('../metric');

function requestLogger(req, res, next) {
    const start = Date.now();

    res.on('finish', () => {
        const duration = Date.now() - start;
        logger.info(`${req.method} ${req.originalUrl} ${res.statusCode} - ${duration}ms`);
        httpRequestsTotal.inc({ method: req.method, status_code: res.statusCode });
    });

    next();
}

module.exports = requestLogger;