import React, { useState } from 'react';
import { api } from '../services/api';

export default function PhysicianReviewScreen({ threadId, consultationData, onNext }) {
  const [treatment, setTreatment] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { diagnosticSummary, interimCare } = consultationData;

  const handleSubmit = async () => {
    if (!treatment.trim()) { setError('Veuillez saisir un traitement ou une conduite à tenir.'); return; }
    setLoading(true); setError('');
    try {
      const result = await api.resumeWithPhysician(threadId, treatment);
      onNext({ physicianTreatment: treatment, finalReport: result.final_report });
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="screen">
      <div className="card wide">
        <h2>👨‍⚕️ Revue du médecin traitant</h2>
        <p className="hint physician-hint">
          Vous êtes le médecin traitant. Examinez la synthèse clinique préliminaire et proposez un traitement ou une conduite à tenir.
        </p>

        <div className="two-col">
          <div className="info-box">
            <h3>🔬 Synthèse clinique préliminaire</h3>
            <pre className="pre-text">{diagnosticSummary || 'Non disponible'}</pre>
          </div>

          <div className="info-box">
            <h3>💊 Recommandation intermédiaire</h3>
            <pre className="pre-text">{interimCare || 'Non disponible'}</pre>
          </div>
        </div>

        <div className="physician-input-section">
          <h3>✍️ Votre traitement / Conduite à tenir</h3>
          <textarea
            className="text-area"
            rows={6}
            placeholder="Ex: Paracétamol 1g x3/jour, repos, hydratation. Consulter si aggravation..."
            value={treatment}
            onChange={e => setTreatment(e.target.value)}
          />
        </div>

        {error && <div className="error">{error}</div>}

        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading ? '⏳ Génération du rapport...' : '📄 Valider & générer le rapport final'}
        </button>
      </div>
    </div>
  );
}
