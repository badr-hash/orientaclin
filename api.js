const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

async function request(method, path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Erreur réseau');
  }
  return res.json();
}

export const api = {
  startSession: () => request('POST', '/sessions/start'),
  startConsultation: (thread_id, patient_initial_case) =>
    request('POST', '/consultation/start', { thread_id, patient_initial_case }),
  resumeWithAnswer: (thread_id, answer) =>
    request('POST', '/consultation/resume', { thread_id, answer }),
  resumeWithPhysician: (thread_id, physician_treatment) =>
    request('POST', '/consultation/resume', { thread_id, physician_treatment }),
  getConsultation: (thread_id) => request('GET', `/consultation/${thread_id}`),
  getReport: (thread_id) => request('GET', `/consultation/${thread_id}/report`),
};
