const payments = [];

function generatePaymentId() {
    return 'pay_' + (payments.length + 1).toString().padStart(6, '0');
}

function createPayment(data) {
    const id = generatePaymentId();
    const now = new Date().toISOString();
    const allowedMethods = ['credit_card', 'qr_code', 'bank_transfer', 'cash'];
    const allowedStatuses = ['pending', 'completed', 'failed', 'refunded'];

    const payment = {
        id,
        orderId: data.orderId || null,
        userId: data.userId || null,
        amount: data.amount,
        currency: data.currency || 'VND',
        method: allowedMethods.includes(data.method) ? data.method: 'credit_card',
        status: allowedStatuses.includes(data.status) ? data.status: 'pending',
        createdAt: now,
        updatedAt: now,
    };
    payments.push(payment);
    return payment;
}

function getPaymentbyId(id) {
    return payments.find(payment => payment.id === id);
}

function getAllPayments() {
    return payments;
}

module.exports = {
    createPayment,
    getPaymentbyId,
    getAllPayments,
};
