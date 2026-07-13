import React, { useState } from 'react';
import PatientCaseScreen from './pages/PatientCaseScreen';
import QuestionsScreen from './pages/QuestionsScreen';
import PhysicianReviewScreen from './pages/PhysicianReviewScreen';
import FinalReportScreen from './pages/FinalReportScreen';
import './App.css';

const SCREEN_ORDER = ['case', 'questions', 'physician', 'report'];
const SCREEN_LABELS = ['Cas patient', 'Questions', 'Médecin', 'Rapport'];

// FIX: Move helper above component (or use a named function declaration that hoists).
// Either way is fine; making it explicit avoids confusion.
function isCompleted(currentScreen, targetScreen) {
  return SCREEN_ORDER.indexOf(currentScreen) > SCREEN_ORDER.indexOf(targetScreen);
}

// Screens: 'case' | 'questions' | 'physician' | 'report'
export default function App() {
  const [screen, setScreen] = useState('case');
  const [threadId, setThreadId] = useState(null);
  const [consultationData, setConsultationData] = useState({});

  const goTo = (nextScreen, data = {}) => {
    setConsultationData(prev => ({ ...prev, ...data }));
    setScreen(nextScreen);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <span className="logo">🏥 OrientaClin</span>
          <span className="subtitle">Système d'orientation clinique préliminaire — Projet académique</span>
        </div>
        <div className="steps">
          {SCREEN_ORDER.map((s, i) => (
            <div
              key={s}
              className={`step ${screen === s ? 'active' : ''} ${isCompleted(screen, s) ? 'done' : ''}`}
            >
              <span className="step-num">{i + 1}</span>
              <span className="step-label">{SCREEN_LABELS[i]}</span>
            </div>
          ))}
        </div>
      </header>

      <main className="app-main">
        {screen === 'case' && (
          <PatientCaseScreen
            onNext={(tid, data) => {
              setThreadId(tid);
              goTo('questions', data);
            }}
          />
        )}
        {screen === 'questions' && (
          <QuestionsScreen
            threadId={threadId}
            initialData={consultationData}
            onNext={(data) => goTo('physician', data)}
          />
        )}
        {screen === 'physician' && (
          <PhysicianReviewScreen
            threadId={threadId}
            consultationData={consultationData}
            onNext={(data) => goTo('report', data)}
          />
        )}
        {screen === 'report' && (
          <FinalReportScreen
            threadId={threadId}
            consultationData={consultationData}
            onRestart={() => {
              setScreen('case');
              setThreadId(null);
              setConsultationData({});
            }}
          />
        )}
      </main>

      <footer className="app-footer">
        ⚠️ Ce système ne remplace pas une consultation médicale. Projet académique uniquement.
      </footer>
    </div>
  );
}
