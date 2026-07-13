import React, { useState } from 'react';
import { api } from '../services/api';

const EXAMPLE_CASES = [
  "Toux sèche depuis 3 jours, légère fièvre à 37.8°C, fatigue modérée.",
  "Douleur thoracique intense depuis ce matin, difficulté à respirer.",
  "Léger mal de gorge depuis hier, pas de fièvre, état général conservé.",
];

export default function PatientCaseScreen({ onNext }) {
  const [patientCase, setPatientCase] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleStart = async () => {
    if (!patientCase.trim()) { setError('Veuillez décrire le cas patient.'); return; }
    setLoading(true); setError('');
    try {
      const session = await api.startSession();
      const result = await api.startConsultation(session.session_id, patientCase);
      onNext(session.session_id, {
        patientCase,
        currentQuestion: result.current_question,
        questionCount: result.question_count,
        totalQuestions: result.total_questions,
      });
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="screen">
      <div className="card">
        <h2>📋 Saisie du cas patient</h2>
        <p className="hint">Décrivez brièvement le motif de consultation ou les symptômes principaux.</p>

        <div className="examples">
          <p className="examples-label">Exemples rapides :</p>
          {EXAMPLE_CASES.map((ex, i) => (
            <button key={i} className="example-btn" onClick={() => setPatientCase(ex)}>
              {ex}
            </button>
          ))}
        </div>

        <textarea
          className="text-area"
          rows={5}
          placeholder="Ex : Toux depuis 3 jours, fièvre légère, fatigue..."
          value={patientCase}
          onChange={e => setPatientCase(e.target.value)}
        />

        {error && <div className="error">{error}</div>}

        <button className="btn-primary" onClick={handleStart} disabled={loading}>
          {loading ? '⏳ Démarrage...' : '▶ Démarrer la consultation'}
        </button>
      </div>
    </div>
  );
}
