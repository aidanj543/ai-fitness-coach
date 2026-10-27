import { useEffect, useState } from 'react';
import { getBackendHealth } from './services/api';

function App() {
  const [status, setStatus] = useState<string>('loading');

  useEffect(() => {
    let active = true;

    getBackendHealth()
      .then((data) => {
        if (active) {
          setStatus(data.status);
        }
      })
      .catch(() => {
        if (active) {
          setStatus('error');
        }
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <main>
      <h1>AI Fitness Coach</h1>
      <h2>Backend Connection</h2>
      <p>Status: {status}</p>
    </main>
  );
}

export default App;