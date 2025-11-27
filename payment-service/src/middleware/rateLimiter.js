const rateLimit = require ('express-rate-limit');
const logger = require ('../logger');

const apiLimiter = rateLimit ({
    windowMs: 60 * 1000,
    max: 10,
    standardHeaders: true, 
    legacyHeaders: false,
    handler: (req, res, next, options) => {
        logger.warn('Rate limit exceeded',{
            ip: req.ip,
            path: req.path,
            method: req.method,
        });

        res.status(options.statusCode).json({
            error: 'Too many requests, please try again later.',
        });
    },
});
module.exports = apiLimiter;