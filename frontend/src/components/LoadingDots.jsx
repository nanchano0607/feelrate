import React, { useEffect, useState } from "react";

function LoadingDots({ text = "검색 중" }) {
  const [dotCount, setDotCount] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setDotCount((prev) => (prev + 1) % 4); // 0 → 1 → 2 → 3 → 0
    }, 500);
    return () => clearInterval(interval);
  }, []);

  const dots = ".".repeat(dotCount);

  return (
    <div className="chat-bubble bot-bubble">
      {text}
      <span>{dots}</span>
    </div>
  );
}

export default LoadingDots;
