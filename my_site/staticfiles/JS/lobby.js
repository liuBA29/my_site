// static/chat/js/test-script.js

console.log("✅ test-script.js успешно подключен!");

document.addEventListener("DOMContentLoaded", function () {
  const joinBtn = document.getElementById("room-join");
  if (joinBtn) {
    joinBtn.addEventListener("click", function () {
      console.log("🔘 Кнопка 'Join Chat' нажата (из test-script.js)");
    });
  }
});
