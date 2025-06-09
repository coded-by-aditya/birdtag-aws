import { useState } from 'react';
import { Auth } from 'aws-amplify';
import { useNavigate } from 'react-router-dom';

export default function SignUp() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: ''
  });

  const [confirmationCode, setConfirmationCode] = useState('');
  const [step, setStep] = useState('signup');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const signUp = async () => {
    if (form.password !== form.confirmPassword) {
      alert("Passwords do not match.");
      return;
    }

    try {
      await Auth.signUp({
        username: form.email,
        password: form.password,
        attributes: {
          email: form.email,
          given_name: form.firstName,
          family_name: form.lastName
        }
      });
      setStep('confirm');
    } catch (err) {
      alert(err.message || 'Sign up failed');
    }
  };

  const confirmSignUp = async () => {
    try {
      await Auth.confirmSignUp(form.email, confirmationCode);
      alert('✅ Sign-up confirmed!');
      navigate('/login'); // 🔁 Redirect after confirmation
    } catch (err) {
      alert(err.message || 'Confirmation failed');
    }
  };

  return (
    <div className="mt-20 max-w-md mx-auto p-6 bg-white shadow-md rounded">
      <h2 className="text-2xl font-bold mb-6 text-center text-blue-800">Create Your Account</h2>

      {step === 'signup' && (
        <>
          <input
            name="firstName"
            placeholder="First Name"
            value={form.firstName}
            onChange={handleChange}
            className="block mb-3 w-full border px-3 py-2 rounded"
          />
          <input
            name="lastName"
            placeholder="Last Name"
            value={form.lastName}
            onChange={handleChange}
            className="block mb-3 w-full border px-3 py-2 rounded"
          />
          <input
            name="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
            className="block mb-3 w-full border px-3 py-2 rounded"
          />
          <input
            name="password"
            placeholder="Password"
            type="password"
            value={form.password}
            onChange={handleChange}
            className="block mb-3 w-full border px-3 py-2 rounded"
          />
          <input
            name="confirmPassword"
            placeholder="Confirm Password"
            type="password"
            value={form.confirmPassword}
            onChange={handleChange}
            className="block mb-4 w-full border px-3 py-2 rounded"
          />
          <button
            onClick={signUp}
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
          >
            Sign Up
          </button>
        </>
      )}

      {step === 'confirm' && (
        <>
          <input
            placeholder="Confirmation Code"
            value={confirmationCode}
            onChange={(e) => setConfirmationCode(e.target.value)}
            className="block mb-4 w-full border px-3 py-2 rounded"
          />
          <button
            onClick={confirmSignUp}
            className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700"
          >
            Confirm Sign-Up
          </button>
        </>
      )}
    </div>
  );
}