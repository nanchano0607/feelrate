import React, { useState, useRef, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import ChatInput from "../components/ChatInput";
import LoadingDots from "../components/LoadingDots";
import { DetailPanel, DetailToggle } from "../components/RestaurantDetail";
import "./chatbot.css";

const DETAIL_RESPONSE_KEY = { menus: "menus", reviews: "review" };

function RecommendPage() {
  const [messages, setMessages] = useState([]);
  // key: `${placeId}:${type}` → { status: "loading" | "done" | "error", items: [] }
  const [details, setDetails] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [searchParams] = useSearchParams();
  const userId = searchParams.get("user_id");

  const bottomRef = useRef(null);

  const handleInput = async (input) => {
  // 1. 사용자의 입력을 먼저 메시지에 추가
  const newMessage = { input, result: null };
  setMessages((prev) => [...prev, newMessage]);
  setIsLoading(true); // 검색중 표시

  try {
    const response = await fetch(`http://localhost:8000/start-recommendation?user_id=${userId}&user_input=${encodeURIComponent(input)}`);
    const data = await response.json();

    // 2. 마지막 메시지에 결과 추가
    setMessages((prev) => {
      const updated = [...prev];
      updated[updated.length - 1] = { ...updated[updated.length - 1], result: data };
      return updated;
    });
  } catch (err) {
    console.error("❌ 요청 실패:", err);
  } finally {
    setIsLoading(false); // 검색중 종료
  }
};
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const setDetail = (key, detail) =>
    setDetails((prev) => {
      const next = { ...prev };
      if (detail) next[key] = detail;
      else delete next[key];
      return next;
    });

  const toggleDetail = async (placeId, type) => {
    const key = `${placeId}:${type}`;
    const current = details[key];
    if (current?.status === "loading") return;
    if (current?.status === "done") {
      setDetail(key, null);
      return;
    }

    setDetail(key, { status: "loading", items: [] });
    try {
      const res = await fetch(`http://localhost:8000/restaurant/${placeId}/${type}?user_id=${userId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setDetail(key, { status: "done", items: data[DETAIL_RESPONSE_KEY[type]] ?? [] });
    } catch (err) {
      console.error(`❌ ${type} 조회 실패:`, err);
      setDetail(key, { status: "error", items: [] });
    }
  };

  
  return (
    <div className="chat-container">
      <div className="blur-circle blue" />
      <div className="blur-circle pink" />

      <div className="chat-header">
        <div className="logo">✨</div>
        <h2>Ask our AI anything</h2>
      </div>

      <div className="chat-box">
        {messages.map((msg, idx) => {
          let result = msg.result?.result;
          if (typeof result === "string" && result.trim().startsWith("[")) {
            try {
              // 백틱과 'json' 제거
              const clean = result.replace(/```json|```/g, "").trim();
              result = JSON.parse(clean);
            } catch {
              console.warn("⚠️ 파싱 실패:", result);
            }
          }

          return (
            <React.Fragment key={idx}>
              <div className="chat-message-group">
                <div className="chat-label user">ME</div>
                <div className="chat-bubble user-bubble">{msg.input}</div>

                <div className="chat-label bot">AI</div>
                <div className="chat-bubble bot-bubble">
                  {msg.result === null ? null : Array.isArray(result) && result.length > 0 ? (
              <div>
                {/* 🔽 추가된 문장 */}
                <p className="search-description">
                  <strong>“{msg.input}”</strong>에 대한 검색 결과입니다.
                </p>

                <p>
                  <strong>🎯 추천 식당:</strong>
                </p>

                      {result.map((r, i) => (
                        <div key={i} className="restaurant-card">
                          <p>
                            <a href={r.url} target="_blank" rel="noreferrer">
                              {r.name}
                            </a>
                          </p>
                          <p>{r.reason}</p>
                          <p>
                            🤖 AI 평점: {r.aiRating} / ⭐ 실제 평점: {r.realRating}
                          </p>
                          <div className="restaurant-actions">
                            {["menus", "reviews"].map((type) => (
                              <DetailToggle
                                key={type}
                                type={type}
                                detail={details[`${r.placeId}:${type}`]}
                                onClick={() => toggleDetail(r.placeId, type)}
                              />
                            ))}
                          </div>

                          {["menus", "reviews"].map((type) => (
                            <DetailPanel
                              key={type}
                              type={type}
                              detail={details[`${r.placeId}:${type}`]}
                              onRetry={() => toggleDetail(r.placeId, type)}
                            />
                          ))}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p>😢 관련된 식당을 찾지 못했어요.</p>
                  )}
                </div>
              </div>
            </React.Fragment>
          );
        })}

        {isLoading && (
          <div className="chat-message-group">
            <LoadingDots />
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <ChatInput onSubmit={handleInput} />
    </div>
  );
}

export default RecommendPage;
