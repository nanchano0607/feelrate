import React from "react";
import "./login.css"; // CSS는 아래 예시 참고

function LoginPage() {
  const handleGoogleLogin = () => {
    window.location.href = 
    "http://localhost:8080/oauth2/authorization/google";
    //"http://feelrate.shop:8080/oauth2/authorization/google";
  };

  return (
    <div className="login-background">
      <div className="login-card">
        <h1>FeelRate</h1>
        <p>AI 기반 음식점 추천 서비스</p>
        <button className="google-button" onClick={handleGoogleLogin}>
          Google로 로그인
        </button>
      </div>
    </div>
  );
}

export default LoginPage;
