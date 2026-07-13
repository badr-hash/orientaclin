import React, { useState } from 'react';
import { api } from '../services/api';

export default function QuestionsScreen({ threadId, initialData, onNext }) {
  const [currentQuestion, setCurrentQuestion] = useState(initialData.currentQuestion);
  // FIX: questionCount represents how many questions have been answered (0-based index of CURRENT question).
  // We use initialData.questionCount which starts at 0 (first question not yet answered).
  const [questionCount, setQuestionCount] = useState(initialData.questionCount || 0);
  const [totalQuestions] = useState(initialData.totalQuestions || 5);
  const [answer, setAnswer] = useState('');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnswer = async () => {
    if (!answer.trim()) { setError('Veuillez saisir une réponse.'); return; }
    setLoading(true); setError('');

    const qa = { question: currentQuestion, answer };

    try {
      const result = await api.resumeWithAnswer(threadId, answer);
      const newHistory = [...history, qa];
      setHistory(newHistory);
      setAnswer('');

      if (result.status === 'awaiting_physician') {
        // All questions answered, diagnostic done
        onNext({
          qaHistory: newHistory,
          diagnosticSummary: result.diagnostic_summary,
          interimCare: result.interim_care,
        });
      } else {
        // Next question
        setCurrentQuestion(result.current_question);
        setQuestionCount(result.question_count);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  // FIX: Progress shows how many questions are DONE (history.length), not questionCount.
  // questionCount from backend is 0-indexed "next question index", which equals answered count.
  const answeredCount = history.length;
  const progress = (answeredCount / totalQuestions) * 100;
  const isLastQuestion = answeredCount + 1 === totalQuestions;

  return (
    <div className="screen">
      <div className="card">
        <h2>💬 Questions cliniques</h2>

        <div className="progress-bar-wrap">
          <div className="progress-bar" style={{ width: `${progress}%` }} />
          <span className="progress-label">Question {answeredCount + 1} / {totalQuestions}</span>
        </div>

        {history.length > 0 && (
          <div className="qa-history">
            {history.map((qa, i) => (
              <div key={i} className="qa-item done">
                <div className="qa-q">✅ Q{i + 1}: {qa.question}</div>
                <div className="qa-a">→ {qa.answer}</div>
              </div>
            ))}
          </div>
        )}

        <div className="current-question">
          <div className="q-badge">Q{answeredCount + 1}</div>
          <p className="q-text">{currentQuestion}</p>
        </div>

        <textarea
          className="text-area"
          rows={3}
          placeholder="Votre réponse..."
          value={answer}
          onChange={e => setAnswer(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleAnswer()}
        />

        {error && <div className="error">{error}</div>}

        <button className="btn-primary" onClick={handleAnswer} disabled={loading}>
          {loading
            ? (isLastQuestion ? '⏳ Analyse en cours...' : '⏳ Chargement...')
            : (isLastQuestion ? '✔ Terminer & analyser' : 'Question suivante →')}
        </button>

        {loading && isLastQuestion && (
          <p className="loading-msg">L'agent diagnostique analyse vos réponses...</p>
        )}
      </div>
    </div>
  );
}
