import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import Typing from './Typing'; // Import the Typing component
import './Home.css';

function Home() {
  const { user, logout } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef(null);

  const handleLogout = async () => {
    try {
      await axios.post('http://localhost:5000/api/logout', {}, { withCredentials: true });
      logout();
    } catch (error) {
      console.error(error);
    }
  };

  const sendMessage = async () => {
    if (!user || isLoading || !inputValue.trim()) return; // Prevent sending messages if not logged in, loading, or empty input
    setIsLoading(true);
    setMessages([...messages, { user: 'user', content: inputValue }]);
    setInputValue('');

    try {
      const response = await axios.post('http://localhost:5000/api/chat', { message: inputValue }, { withCredentials: true });
      setMessages([...messages, { user: 'user', content: inputValue }, { user: 'ai', content: response.data.response }]);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, [isLoading]);

  return (
    <div className="container">
      <button className="logout" onClick={handleLogout}>Logout</button>
      <h1>Chat App</h1>
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`message-container ${msg.user}`}>
            {msg.user === 'ai' && <div className="profile-image"></div>}
            <div className={`message ${msg.user}`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && <Typing />} {/* Conditionally render the Typing component */}
      </div>
      <div className="input-area">
        <input
          type="text"
          placeholder="Type your message..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          ref={inputRef}
        />
        <button id="send-button" onClick={sendMessage}>
          <div className="send-icon"></div>
        </button>
      </div>
    </div>
  );
}

export default Home;
