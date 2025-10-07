# library-demo-v0.1

Demo Thư viện thỏa mãn nguyên tắc Client-Server



**Kiến trúc:**



\[Browser: http://localhost:5173]  --->  HTTP + JSON  --->  \[API Server: http://localhost:3000]

&nbsp;     Client (index.html + script.js)                         Server (Express, /api/\*)

&nbsp;     - Render UI                                             - Xử lý tài nguyên "books"

&nbsp;     - Gọi fetch()                                           - Trả JSON + status code



**Chạy nhanh:**

**1) Server (cổng 3000)**



npm i

npm i cors

node server.js

\# mở thử: http://localhost:3000/api/books  -> JSON



**2) Client (cổng 5173)**



\# chạy một static server cho thư mục client/

npx http-server client -p 5173 -c-1

\# mở: http://localhost:5173



**Cấu hình endpoint linh hoạt (trong index.html):**

<script>window.API\_BASE = 'http://localhost:3000/api';</script>



**Các điểm thỏa mãn nguyên tắc Client-Server:**



**Tách biệt vai trò:**



* Client chạy ở 5173 (UI tĩnh).



* Server chạy ở 3000 (API JSON).



* Dừng Client hoặc Server thì bên còn lại vẫn chạy bình thường (chỉ mất kết nối HTTP).



**Không phụ thuộc lẫn nhau:**



* Đổi giao diện/bố cục → không sửa server.



* Đổi cách lưu trữ server (in-memory → DB) → không sửa client nếu giữ API.



