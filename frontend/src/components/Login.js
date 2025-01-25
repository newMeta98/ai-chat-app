import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Navigate } from 'react-router-dom';
import './Home.css';

function Login() {
  const { login, user } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      console.log('Sending login request with:', { email, password }); // Add this line for debugging
      const response = await axios.post('http://localhost:5000/api/login', { email, password }, { withCredentials: true });
      console.log('Login response:', response.data); // Add this line for debugging
      login(response.data.user_id, response.data.user_name);
    } catch (error) {
      console.error('Login failed', error);
    }
  };

  if (user) return <Navigate to="/" />;

  return (
    <div className="container">
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>
      <p>
        Don't have an account? <a href="/register">Create one</a>
      </p>
    </div>
  );
}

export default Login;
