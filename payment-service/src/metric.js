const client = require ('prom-client');

client.collectDefaultMetrics();
//thu thập các default metrics như CPU, memory, v.v

const httpRequestsTotal = new client.Counter({
    name: 'http_requests_total',
    help: 'Total number of HTTP requests',
    labelNames: ['method', 'status_code'],
});
//đếm tổng số request HTTP, phân loại theo method và status code

const paymentsCreatedTotal = new client.Counter({
    name: 'payments_created_total',
    help: 'Total number of payments created',
});
//đếm tổng số payment được tạo

module.exports = {
    httpRequestsTotal,
    paymentsCreatedTotal,
    register: client.register,
};