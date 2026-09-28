import React, { useState } from "react";

function ChatInput({ onSubmit }) {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSubmit(input);
    setInput("");
  };

  return (
    <form onSubmit={handleSubmit} className="chat-input">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="추천받고 싶은 조건을 입력하세요..."
      />
      <button type="submit">전송</button>
    </form>
  );
}

export default ChatInput;
