const express = require('express');
const jwt = require('jsonwebtoken');
const cookieParser = require('cookie-parser');
const cors = require('cors');

const app = express();
const PORT = 3000;
const SECRET = 'very-secret-key'; 
app.use(cors({
origin: ['http://localhost:5500', 'http://127.0.0.1:5500'],
  credentials: true
}));

app.use(express.json());
app.use(cookieParser());

app.post('/login', (req, res) => {
  const { username, password } = req.body;

  if (username === 'admin' && password === '123456') {
    const token = jwt.sign(
      { sub: username, role: 'admin' },
      SECRET,
      { expiresIn: '1h' }
    );

    res.cookie('jwt_server', token, {
      httpOnly: false, 
      secure: false,
      sameSite: 'lax',
      maxAge: 60 * 60 * 1000
    });

    return res.json({
      message: 'Đăng nhập thành công',
      token
    });
  }

  return res.status(401).json({ message: 'Sai tài khoản hoặc mật khẩu' });
});

app.get('/protected', (req, res) => {
  let token = null;

  const auth = req.headers['authorization'];
  if (auth && auth.startsWith('Bearer ')) {
    token = auth.slice(7);
  }

  if (!token && req.cookies.jwt_server) {
    token = req.cookies.jwt_server;
  }

  if (!token) {
    return res.status(401).json({ message: 'Không tìm thấy token' });
  }

  try {
    const payload = jwt.verify(token, SECRET);
    return res.json({
      message: 'OK, đây là tài nguyên bảo vệ',
      payload
    });
  } catch (err) {
    return res.status(401).json({ message: 'Token không hợp lệ hoặc đã hết hạn' });
  }
});

app.listen(PORT, () => {
  console.log(`✅ Server chạy ở http://localhost:${PORT}`);
});