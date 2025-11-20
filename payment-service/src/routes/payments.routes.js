const express = require('express');
const router = express.Router();
const logger = require('../logger');
const { paymentsCreatedTotal } = require('../metric');
const {
    createPayment,
    getPaymentbyId,
    getAllPayments,
} = require('../data/paymentStore');

router.post('/', (req, res) => {
    const rawAmount = req.body.amount;
    const amount = Number(rawAmount);

    if (!Number.isFinite(amount) || amount <= 0) {
        return res.status(400).json({ error: 'Invalid amount' });
    }

    const paymentData = {
        orderId: req.body.orderId,
        userId: req.body.userId,
        amount: amount,
        currency: req.body.currency,
        method: req.body.method,
        status: req.body.status,
        };
    
    const newPayment = createPayment(paymentData);
    res.status(201).json(newPayment);
    paymentsCreatedTotal.inc();

    logger.info('Payment created',{
        paymentId: newPayment.id,
        orderId: newPayment.orderId,
        userId: newPayment.userId,
        amount: newPayment.amount,
        currency: newPayment.currency,
        method: newPayment.method,
        status: newPayment.status,
    });
});

router.get('/:id', (req, res) => {
    const paymentId = req.params.id;
    const payment = getPaymentbyId(paymentId);
    if (payment) {
        res.status(200).json(payment);
    } else {
        res.status(404).json({ error: 'Payment not found' });
        logger.warn('Payment not found', { paymentId });
    }
});

router.get('/', (req, res) => {
    const payments = getAllPayments();
    res.json({data: payments});
});

module.exports = router;
