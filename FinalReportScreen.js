import React from 'react';

export default function FinalReportScreen({ threadId, consultationData, onRestart }) {
  const { finalReport } = consultationData;

  const handlePrint = () => window.print();

  const handleCopy = () => {
    navigator.clipboard.writeText(finalReport || '');
    alert('Rapport copié dans le presse-papier.');
  };

  return (
    <div className="screen">
      <div className="card wide">
        <div className="report-header">
          <h2>📄 Rapport final d'orientation clinique</h2>
          <div className="report-actions">
            <button className="btn-secondary" onClick={handleCopy}>📋 Copier</button>
            <button className="btn-secondary" onClick={handlePrint}>🖨️ Imprimer</button>
            <button className="btn-primary" onClick={onRestart}>🔄 Nouvelle consultation</button>
          </div>
        </div>

        <div className="report-meta">
          <span>🔑 Session : {threadId}</span>
        </div>

        <div className="report-body">
          {finalReport
            ? finalReport.split('\n').map((line, i) => (
                <p key={i} className={line.startsWith('#') ? 'report-section-title' : 'report-line'}>
                  {line}
                </p>
              ))
            : <p className="no-report">Rapport non disponible.</p>
          }
        </div>

        <div className="disclaimer">
          ⚠️ Ce système ne remplace pas une consultation médicale. Projet académique uniquement.
        </div>
      </div>
    </div>
  );
}
