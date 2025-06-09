import './index.css';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import { Buffer } from 'buffer';
import process from 'process';

// 🛠️ Set globals needed by Amplify
window.global = window;
window.Buffer = Buffer;
window.process = process

// 👉 Import Amplify and your config
import { Amplify } from 'aws-amplify';
import awsExports from './aws-exports';

// 👉 Configure Amplify
Amplify.configure(awsExports);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);