import React from "react";

const PANELS = {
  menus: { icon: "🍜", label: "메뉴", empty: "등록된 메뉴 정보가 없어요." },
  reviews: { icon: "📝", label: "리뷰", empty: "아직 방문자 후기가 없어요." },
};

export function DetailToggle({ type, detail, onClick }) {
  const { icon, label } = PANELS[type];
  const isOpen = detail?.status === "done";
  const isLoading = detail?.status === "loading";

  return (
    <button
      type="button"
      className={`detail-toggle${isOpen ? " active" : ""}`}
      onClick={onClick}
      disabled={isLoading}
      aria-expanded={isOpen}
    >
      <span aria-hidden="true">{icon}</span>
      {label}
      {isLoading && <span className="detail-toggle-status">불러오는 중…</span>}
      {isOpen && <span className="detail-toggle-count">{detail.items.length}</span>}
    </button>
  );
}

export function DetailPanel({ type, detail, onRetry }) {
  if (!detail || detail.status === "loading") return null;
  const { icon, label, empty } = PANELS[type];

  return (
    <section className={`detail-panel detail-panel-${type}`}>
      <header className="detail-panel-header">
        <span aria-hidden="true">{icon}</span>
        {type === "reviews" ? "방문자 후기" : label}
        {detail.status === "done" && <span className="detail-panel-count">{detail.items.length}</span>}
      </header>

      {detail.status === "error" && (
        <p className="detail-panel-message">
          정보를 불러오지 못했어요.{" "}
          <button type="button" className="detail-retry" onClick={onRetry}>다시 시도</button>
        </p>
      )}

      {detail.status === "done" && detail.items.length === 0 && (
        <p className="detail-panel-message">{empty}</p>
      )}

      {detail.status === "done" && detail.items.length > 0 && (
        type === "menus" ? <MenuList menus={detail.items} /> : <ReviewList reviews={detail.items} />
      )}
    </section>
  );
}

function MenuList({ menus }) {
  return (
    <ul className="menu-board">
      {menus.map((menu, idx) => (
        <li key={idx} className="menu-row">
          <span className="menu-name">{menu.menuName}</span>
          <span className="menu-leader" aria-hidden="true" />
          <span className="menu-price">{menu.price || "가격 정보 없음"}</span>
        </li>
      ))}
    </ul>
  );
}

function ReviewList({ reviews }) {
  return (
    <ul className="review-cards">
      {reviews.map((review, idx) => (
        <li key={idx} className="review-card">
          <span className="review-quote" aria-hidden="true">“</span>
          <p className="review-text">{review}</p>
        </li>
      ))}
    </ul>
  );
}
