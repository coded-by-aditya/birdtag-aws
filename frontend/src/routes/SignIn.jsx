import { useState } from 'react';
import { Auth } from 'aws-amplify';

export default function SignIn() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const signIn = async () => {
    try {
      await Auth.signIn(form.email, form.password);
      window.location.href = '/upload'; // ✅ triggers full reload so NavBar updates
    } catch (err) {
      setError(err.message || 'Something went wrong');
    }
  };

  return (
    <div className="mt-20 max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">Sign In</h2>
      <input
        name="email"
        placeholder="Email"
        value={form.email}
        onChange={handleChange}
        className="block mb-2 w-full border px-2 py-1"
      />
      <input
        name="password"
        type="password"
        placeholder="Password"
        value={form.password}
        onChange={handleChange}
        className="block mb-4 w-full border px-2 py-1"
      />
      <button
        onClick={signIn}
        className="bg-blue-600 text-white px-4 py-2 rounded w-full"
      >
        Sign In
      </button>
      {error && <p className="text-red-600 mt-2 text-sm">{error}</p>}
    </div>
  );
}