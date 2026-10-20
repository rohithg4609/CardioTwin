import { useEffect, useRef, useState, type CSSProperties, type FormEvent } from 'react';
import { gsap } from 'gsap';
import { useGSAP } from '@gsap/react';
import {
  Activity,
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Check,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  ClipboardCheck,
  HeartPulse,
  Info,
  LayoutDashboard,
  LoaderCircle,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  Wifi,
  WifiOff,
  XCircle,
} from 'lucide-react';

gsap.registerPlugin(useGSAP);

type View = 'overview' | 'assessment' | 'history' | 'guide';
type ApiStatus = 'checking' | 'online' | 'offline';
type PatientKey =
  | 'age'
  | 'sex'
  | 'cp'
  | 'trestbps'
  | 'chol'
  | 'fbs'
  | 'restecg'
  | 'thalach'
  | 'exang'
  | 'oldpeak'
  | 'slope'
  | 'ca'
  | 'thal';
type PatientInput = Record<PatientKey, string>;
type Option = { value: string; label: string };
type FieldConfig = {
  key: PatientKey;
  label: string;
  help: string;
  placeholder?: string;
  unit?: string;
  kind: 'number' | 'select';
  min?: number;
  max?: number;
  step?: number;
  options?: Option[];
};
type Explanation = {
  feature: string;
  description: string;
  patient_value: number;
  shap_contribution: number;
  direction: string;
};
type Prediction = {
  risk_score: number;
  risk_category: string;
  predicted_class: string;
  raw_model_class: number;
  explanations: Explanation[];
};

type StepConfig = { eyebrow: string; title: string; description: string; fields: FieldConfig[] };
type HistoryRecord = {
  record_type?: string;
  date?: string;
  created_at?: string;
  patient_snapshot?: {
    patient_id?: string;
    name?: string;
    age?: number;
    sex?: string;
  };
  prediction?: Prediction;
  model_inputs?: Record<string, number>;
};

const EMPTY_PATIENT: PatientInput = {
  age: '', sex: '', cp: '', trestbps: '', chol: '', fbs: '', restecg: '', thalach: '',
  exang: '', oldpeak: '', slope: '', ca: '', thal: '',
};

const STEPS: StepConfig[] = [
  {
    eyebrow: 'Step 1 of 3 · Personal details',
    title: 'Start with the basics',
    description: 'These details identify the context used by the research model.',
    fields: [
      { key: 'age', label: 'Age', help: 'The source dataset was collected from adults. This prototype is not designed for children.', kind: 'number', min: 18, max: 120, step: 1, unit: 'years', placeholder: 'e.g. 55' },
      { key: 'sex', label: 'Sex category in source dataset', help: 'The historical dataset only encodes female and male categories. This limitation may not represent every patient.', kind: 'select', options: [{ value: '0', label: 'Female (code 0)' }, { value: '1', label: 'Male (code 1)' }] },
      { key: 'cp', label: 'Chest-pain pattern', help: 'Use the category recorded by a qualified clinician; do not try to diagnose or guess the type yourself.', kind: 'select', options: [
        { value: '1', label: 'Typical angina (code 1)' },
        { value: '2', label: 'Atypical angina (code 2)' },
        { value: '3', label: 'Non-anginal pain (code 3)' },
        { value: '4', label: 'Asymptomatic (code 4)' },
      ] },
    ],
  },
  {
    eyebrow: 'Step 2 of 3 · Measurements',
    title: 'Add recorded measurements',
    description: 'Use values from a recent clinical record and keep the listed units.',
    fields: [
      { key: 'trestbps', label: 'Resting blood pressure', help: 'Systolic resting blood pressure, as recorded by a health professional.', kind: 'number', min: 50, max: 300, step: 1, unit: 'mmHg', placeholder: 'e.g. 120' },
      { key: 'chol', label: 'Serum cholesterol', help: 'Use the total serum cholesterol value from the lab report.', kind: 'number', min: 50, max: 800, step: 1, unit: 'mg/dL', placeholder: 'e.g. 200' },
      { key: 'fbs', label: 'Fasting blood sugar above 120 mg/dL?', help: 'Select from a fasting test result. Do not estimate from symptoms or a non-fasting result.', kind: 'select', options: [{ value: '0', label: 'No — not above 120 mg/dL' }, { value: '1', label: 'Yes — above 120 mg/dL' }] },
      { key: 'restecg', label: 'Resting ECG category', help: 'This is a coded clinical ECG interpretation. Ask the clinician who reviewed the ECG if the code is not on the report.', kind: 'select', options: [
        { value: '0', label: 'Normal (code 0)' },
        { value: '1', label: 'ST–T wave abnormality (code 1)' },
        { value: '2', label: 'Left ventricular hypertrophy category (code 2)' },
      ] },
      { key: 'thalach', label: 'Maximum heart rate achieved', help: 'Heart rate documented during the exercise test, not a guessed or current pulse.', kind: 'number', min: 40, max: 250, step: 1, unit: 'beats/min', placeholder: 'e.g. 150' },
      { key: 'exang', label: 'Exercise-induced angina recorded?', help: 'Use the result documented during the clinical exercise test.', kind: 'select', options: [{ value: '0', label: 'No (code 0)' }, { value: '1', label: 'Yes (code 1)' }] },
    ],
  },
  {
    eyebrow: 'Step 3 of 3 · Clinical test details',
    title: 'Confirm the remaining test results',
    description: 'These fields are technical cardiac-test codes. Continue only if the values are available in a clinical report or have been provided by a qualified professional.',
    fields: [
      { key: 'oldpeak', label: 'ST depression relative to rest', help: 'Recorded during exercise testing. This is a clinical test measurement, not a symptom score.', kind: 'number', min: 0, max: 10, step: 0.1, unit: 'units', placeholder: 'e.g. 1.5' },
      { key: 'slope', label: 'Peak exercise ST-segment slope', help: 'Use the encoded result from the exercise ECG report.', kind: 'select', options: [
        { value: '1', label: 'Upsloping (code 1)' },
        { value: '2', label: 'Flat (code 2)' },
        { value: '3', label: 'Downsloping (code 3)' },
      ] },
      { key: 'ca', label: 'Major vessels seen by fluoroscopy', help: 'The source dataset accepts codes from 0 through 3. Ask the clinician to confirm this test-specific value.', kind: 'select', options: [
        { value: '0', label: '0 vessels (code 0)' },
        { value: '1', label: '1 vessel (code 1)' },
        { value: '2', label: '2 vessels (code 2)' },
        { value: '3', label: '3 vessels (code 3)' },
      ] },
      { key: 'thal', label: 'Thal test category', help: 'The training file contains only codes 3, 6, and 7. Use the exact code from the clinical source; never substitute a guessed value.', kind: 'select', options: [
        { value: '3', label: 'Normal (code 3)' },
        { value: '6', label: 'Fixed defect (code 6)' },
        { value: '7', label: 'Reversible defect (code 7)' },
      ] },
    ],
  },
];

const VIEW_TITLES: Record<View, string> = {
  overview: 'Overview',
  assessment: 'Risk assessment',
  history: 'Assessment history',
  guide: 'How CardioTwin works',
};

function Field({ field, value, onChange, invalid }: {
  field: FieldConfig;
  value: string;
  onChange: (key: PatientKey, value: string) => void;
  invalid: boolean;
}) {
  const helpId = `${field.key}-help`;
  const errorId = `${field.key}-error`;
  return (
    <div className={`field ${invalid ? 'field-invalid' : ''}`}>
      <label htmlFor={field.key}>{field.label}<span className="required-mark" aria-hidden="true"> *</span></label>
      <div className={`control-wrap ${field.kind === 'number' && field.unit ? 'has-unit' : ''}`}>
        {field.kind === 'select' ? (
          <select
            id={field.key}
            name={field.key}
            value={value}
            onChange={(event) => onChange(field.key, event.target.value)}
            aria-describedby={invalid ? `${helpId} ${errorId}` : helpId}
            aria-invalid={invalid}
            required
          >
            <option value="">Choose an option</option>
            {field.options?.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        ) : (
          <input
            id={field.key}
            name={field.key}
            type="number"
            value={value}
            min={field.min}
            max={field.max}
            step={field.step}
            placeholder={field.placeholder}
            onChange={(event) => onChange(field.key, event.target.value)}
            aria-describedby={invalid ? `${helpId} ${errorId}` : helpId}
            aria-invalid={invalid}
            required
          />
        )}
        {field.kind === 'number' && field.unit && <span className="input-unit">{field.unit}</span>}
      </div>
      <p className="field-help" id={helpId}>{field.help}</p>
      {invalid && <p className="field-error" id={errorId}>Please enter or select a valid value for this field.</p>}
    </div>
  );
}

function App() {
  const rootRef = useRef<HTMLDivElement>(null);
  const [view, setView] = useState<View>('overview');
  const [apiStatus, setApiStatus] = useState<ApiStatus>('checking');
  const [patient, setPatient] = useState<PatientInput>(EMPTY_PATIENT);
  const [step, setStep] = useState(0);
  const [invalidKeys, setInvalidKeys] = useState<PatientKey[]>([]);
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [historyRecords, setHistoryRecords] = useState<HistoryRecord[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState('');
  const [historyRefresh, setHistoryRefresh] = useState(0);

  useEffect(() => {
    let active = true;
    fetch('/api/health')
      .then(async (response) => {
        if (!response.ok) throw new Error('API health check failed');
        const body = await response.json() as { status?: string };
        if (!active) return;
        setApiStatus(body.status === 'healthy' ? 'online' : 'offline');
      })
      .catch(() => { if (active) setApiStatus('offline'); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (view !== 'history') return;

    const controller = new AbortController();

    async function loadHistory() {
      setHistoryLoading(true);
      setHistoryError('');

      try {
        const response = await fetch('/api/health-records', {
          signal: controller.signal,
        });

        const body = await response.json() as {
          records?: HistoryRecord[];
          count?: number;
          detail?: string;
        };

        if (!response.ok) {
          throw new Error(body.detail || 'Unable to load assessment history.');
        }

        setHistoryRecords(Array.isArray(body.records) ? body.records : []);
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') return;

        setHistoryError(
          error instanceof Error ? error.message : 'Unable to load history.'
        );
      } finally {
        if (!controller.signal.aborted) setHistoryLoading(false);
      }
    }

    void loadHistory();

    return () => controller.abort();
  }, [view, historyRefresh]);
  useGSAP(() => {
    const media = gsap.matchMedia();
    media.add('(prefers-reduced-motion: no-preference)', () => {
      gsap.fromTo('.view-enter', { opacity: 0, y: 12 }, {
        opacity: 1, y: 0, duration: 0.42, stagger: 0.055, ease: 'power2.out', clearProps: 'transform',
      });
      gsap.fromTo('.hero-orbit', { opacity: 0.55, scale: 0.96 }, {
        opacity: 1, scale: 1, duration: 0.65, ease: 'power2.out', stagger: 0.08,
      });
    });
    return () => media.revert();
  }, { dependencies: [view, step, prediction], scope: rootRef, revertOnUpdate: true });

  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }

  function navigate(next: View) {
    setView(next);
    setFormError('');
    scrollToTop();
  }

  function updateField(key: PatientKey, value: string) {
    setPatient((current) => ({ ...current, [key]: value }));
    setInvalidKeys((current) => current.filter((item) => item !== key));
    setFormError('');
  }

  function fieldIsValid(field: FieldConfig, raw: string): boolean {
    if (raw.trim() === '') return false;
    if (field.kind === 'select') return Boolean(field.options?.some((option) => option.value === raw));
    const value = Number(raw);
    if (!Number.isFinite(value)) return false;
    if (field.min !== undefined && value < field.min) return false;
    if (field.max !== undefined && value > field.max) return false;
    if (field.step === 1 && !Number.isInteger(value)) return false;
    return true;
  }

  function validateStep(stepIndex: number): boolean {
    const fields = STEPS[stepIndex].fields;
    const bad = fields.filter((field) => !fieldIsValid(field, patient[field.key])).map((field) => field.key);
    setInvalidKeys((current) => [...new Set([...current.filter((key) => !fields.some((field) => field.key === key)), ...bad])]);
    if (bad.length) {
      setFormError('Please complete the highlighted fields using values from the clinical record. You can ask a healthcare professional to help with unfamiliar fields.');
      document.getElementById(bad[0])?.focus();
      return false;
    }
    setFormError('');
    return true;
  }

  function nextStep(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!validateStep(step)) return;
    if (step < STEPS.length - 1) {
      setStep((current) => current + 1);
      scrollToTop();
    }
  }

  async function runPrediction(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!validateStep(step)) return;
    // Validate the complete form again, rather than relying only on the visible step.
    const everyInvalid = STEPS.flatMap((item) => item.fields)
      .filter((field) => !fieldIsValid(field, patient[field.key]))
      .map((field) => field.key);
    if (everyInvalid.length) {
      setInvalidKeys(everyInvalid);
      setFormError('Some required fields are incomplete. Please review each step before continuing.');
      const firstKey = everyInvalid[0];
      const firstStep = STEPS.findIndex((item) => item.fields.some((field) => field.key === firstKey));
      setStep(Math.max(firstStep, 0));
      document.getElementById(firstKey)?.focus();
      return;
    }

    setIsSubmitting(true);
    setFormError('');
    try {
      const payload = Object.fromEntries(
        (Object.keys(EMPTY_PATIENT) as PatientKey[]).map((key) => [key, Number(patient[key])]),
      );
      const response = await fetch('/api/assessment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const body = await response.json() as {
        assessment?: Prediction;
        saved_record?: unknown;
        notice?: string;
        detail?: string;
      };

      if (!response.ok) {
        throw new Error(
          body.detail ||
          'The server could not save the assessment. Please try again.'
        );
      }

      const result = body.assessment;

      if (
        !result ||
        typeof result.risk_score !== 'number' ||
        !Array.isArray(result.explanations)
      ) {
        throw new Error(
          'The API response did not match the expected CardioTwin prediction format.'
        );
      }

      setPrediction(result);
      setView('assessment');
      scrollToTop();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'Unable to reach the CardioTwin API. Check that FastAPI is running.');
    } finally {
      setIsSubmitting(false);
    }
  }

  function beginAssessment() {
    setPrediction(null);
    setPatient(EMPTY_PATIENT);
    setInvalidKeys([]);
    setFormError('');
    setStep(0);
    navigate('assessment');
  }

  const statusLabel = apiStatus === 'online' ? 'API reachable' : apiStatus === 'offline' ? 'API not reached' : 'Checking API';

  return (
    <div className="app-shell" ref={rootRef}>
      <aside className="sidebar" aria-label="Main navigation">
        <button className="brand" onClick={() => navigate('overview')} aria-label="CardioTwin overview">
          <span className="brand-mark"><HeartPulse size={23} strokeWidth={2.2} /></span>
          <span className="brand-copy"><strong>CardioTwin</strong><small>Patient portal</small></span>
        </button>

        <div className="sidebar-section-label">WORKSPACE</div>
        <nav className="side-nav">
          <button className={`nav-item ${view === 'overview' ? 'active' : ''}`} onClick={() => navigate('overview')} aria-current={view === 'overview' ? 'page' : undefined}>
            <LayoutDashboard size={18} /><span>Overview</span>
          </button>
          <button className={`nav-item ${view === 'assessment' ? 'active' : ''}`} onClick={() => navigate('assessment')} aria-current={view === 'assessment' ? 'page' : undefined}>
            <ClipboardCheck size={18} /><span>Risk assessment</span>
          </button>
          <button className={`nav-item ${view === 'history' ? 'active' : ''}`} onClick={() => navigate('history')} aria-current={view === 'history' ? 'page' : undefined}>
            <Activity size={18} /><span>Assessment history</span>
          </button>          <button className={`nav-item ${view === 'guide' ? 'active' : ''}`} onClick={() => navigate('guide')} aria-current={view === 'guide' ? 'page' : undefined}>
            <BookOpen size={18} /><span>How it works</span>
          </button>
        </nav>

        <div className="sidebar-spacer" />
        <div className="sidebar-safety">
          <div className="safety-icon"><ShieldCheck size={19} /></div>
          <strong>Research prototype</strong>
          <p>CardioTwin is not a diagnosis and does not replace professional care.</p>
          <button className="text-action" onClick={() => navigate('guide')}>Read safety notes <ChevronRight size={14} /></button>
        </div>
        <div className="api-indicator">
          <span className={`status-dot ${apiStatus}`} />
          <span>{statusLabel}</span>
          {apiStatus === 'online' ? <Wifi size={15} /> : apiStatus === 'offline' ? <WifiOff size={15} /> : <LoaderCircle size={15} className="spin" />}
        </div>
      </aside>

      <div className="content-shell">
        <header className="topbar">
          <div className="breadcrumbs"><span>CardioTwin</span><ChevronRight size={14} /><strong>{VIEW_TITLES[view]}</strong></div>
          <div className="topbar-right">
            <span className="prototype-pill"><span className="pill-dot" /> Prototype environment</span>
            <div className="profile-mark" aria-label="Patient portal icon"><HeartPulse size={19} /></div>
          </div>
        </header>

        <main id="main-content" className="main-content">
          {view === 'overview' && (
            <section className="view-enter" aria-labelledby="overview-title">
              <div className="page-heading">
                <div><p className="eyebrow">YOUR HEALTH, EXPLAINED</p><h1 id="overview-title">A clearer view of heart health.</h1><p className="page-subtitle">Understand what CardioTwin can show, what it cannot, and how to review a model output with a healthcare professional.</p></div>
                <span className="date-chip"><Sparkles size={15} /> Built for clarity</span>
              </div>

              <section className="hero-card" aria-label="Start an assessment">
                <div className="hero-content">
                  <div className="hero-tag"><span className="hero-tag-dot" /> A guided, step-by-step experience</div>
                  <h2>Health information can feel complex.<br /><em>Let's make the next step clearer.</em></h2>
                  <p>Use values from a clinical record to explore how a research model responds. No result is a diagnosis, and you never need to guess a value.</p>
                  <button className="button button-light" onClick={beginAssessment}>Start an assessment <ArrowRight size={17} /></button>
                  <div className="hero-footnote"><ShieldCheck size={14} /> Completed assessments are saved to the digital-twin history.</div>
                </div>
                <div className="hero-visual" aria-hidden="true">
                  <div className="hero-orbit orbit-one" />
                  <div className="hero-orbit orbit-two" />
                  <div className="hero-orbit orbit-three" />
                  <div className="heart-glow"><HeartPulse size={72} strokeWidth={1.45} /></div>
                  <div className="visual-caption"><span className="visual-pulse" /> Research model <small>not a medical device</small></div>
                </div>
              </section>

              <div className="section-heading-row"><div><h2>Your workspace</h2><p>What is available in this version of CardioTwin.</p></div><span className="quiet-label">Prototype overview</span></div>
              <div className="overview-grid">
                <article className="overview-card view-enter">
                  <div className="card-icon teal-icon"><Activity size={20} /></div>
                  <div className="overview-card-top"><h3>Model assessment</h3><span className="status-tag status-ready">Available</span></div>
                  <p>Submit the 13 inputs expected by the current ML API and review its output with clear limitations.</p>
                  <button className="card-link" onClick={beginAssessment}>Begin assessment <ArrowRight size={15} /></button>
                </article>
                <article className="overview-card view-enter">
                  <div className="card-icon blue-icon"><HeartPulse size={20} /></div>
                  <div className="overview-card-top"><h3>Digital twin history</h3><span className="status-tag status-ready">Saving enabled</span></div>
                  <p>Assessment saving is connected to the backend. A browsable history timeline is the next frontend step.</p>
                  <button className="card-link muted-link" onClick={() => navigate('guide')}>View current scope <ArrowRight size={15} /></button>
                </article>
                <article className="overview-card view-enter">
                  <div className="card-icon lavender-icon"><Stethoscope size={20} /></div>
                  <div className="overview-card-top"><h3>Care guidance</h3><span className="status-tag status-next">Not connected</span></div>
                  <p>The medical-care code is integrated, but it has not yet been exposed as patient-facing API endpoints.</p>
                  <button className="card-link muted-link" onClick={() => navigate('guide')}>View current scope <ArrowRight size={15} /></button>
                </article>
              </div>

              <div className="bottom-grid">
                <section className="panel readiness-panel view-enter">
                  <div className="panel-heading"><div><h2>Before you begin</h2><p>For a more reliable workflow, prepare these items first.</p></div><div className="panel-heading-icon"><ClipboardCheck size={18} /></div></div>
                  <div className="check-row"><span className="check-circle"><Check size={14} /></span><div><strong>Your clinical record</strong><p>Use recorded values rather than estimates or guesses.</p></div></div>
                  <div className="check-row"><span className="check-circle"><Check size={14} /></span><div><strong>Help with clinical codes</strong><p>Ask a qualified professional about ECG and exercise-test fields.</p></div></div>
                  <div className="check-row"><span className="check-circle"><Check size={14} /></span><div><strong>Time to review the limitations</strong><p>Model output is not an individual clinical risk estimate.</p></div></div>
                </section>
                <aside className="panel api-panel view-enter">
                  <div className="panel-heading"><div><h2>Connection status</h2><p>Local development environment</p></div><div className={`connection-icon ${apiStatus}`}><Activity size={19} /></div></div>
                  <div className="connection-row"><span className={`status-dot ${apiStatus}`} /><strong>{statusLabel}</strong></div>
                  <p className="api-explain">This checks the FastAPI health endpoint. It does not verify clinical validity or guarantee that every model dependency is ready.</p>
                  {apiStatus === 'offline' && <div className="inline-note"><Info size={15} /> Start the FastAPI server and refresh this page.</div>}
                  <button className="button button-secondary full-button" onClick={() => window.location.reload()}>Check again <ArrowRight size={16} /></button>
                </aside>
              </div>
              <div className="disclaimer-strip"><ShieldAlert size={19} /><p><strong>Need urgent medical help?</strong> Do not wait for this tool. Seek local emergency care for severe or persistent chest pain, difficulty breathing, fainting, or other urgent symptoms.</p></div>
            </section>
          )}

          {view === 'assessment' && (
            <section className="view-enter" aria-labelledby="assessment-title">
              {prediction ? (
                <PredictionView prediction={prediction} onNew={beginAssessment} onOverview={() => navigate('overview')} />
              ) : (
                <>
                  <div className="page-heading compact-heading">
                    <div><p className="eyebrow">GUIDED ASSESSMENT</p><h1 id="assessment-title">Let's enter the recorded values.</h1><p className="page-subtitle">Three short steps. Every field is required because the current model expects all 13 inputs.</p></div>
                  </div>
                  <div className="warning-banner"><Info size={19} /><div><strong>Use clinical records — don't guess.</strong><p>Several fields are specific test codes that many patients won't know. Complete this with a healthcare professional or an existing report. This research prototype does not diagnose, and its score is not a clinically validated probability.</p></div></div>
                  <div className="step-layout">
                    <aside className="step-rail" aria-label="Assessment progress">
                      <p className="rail-title">YOUR PROGRESS</p>
                      {STEPS.map((item, index) => (
                        <button key={item.title} className={`step-rail-item ${step === index ? 'current' : ''} ${step > index ? 'complete' : ''}`} onClick={() => { if (index <= step) setStep(index); }} disabled={index > step} aria-current={step === index ? 'step' : undefined}>
                          <span className="step-number">{step > index ? <Check size={15} /> : index + 1}</span>
                          <span className="step-copy"><strong>{['Personal details', 'Measurements', 'Clinical test details'][index]}</strong><small>{['Basic information', 'Recorded readings', 'Test-specific values'][index]}</small></span>
                        </button>
                      ))}
                      <div className="rail-help"><CircleHelp size={17} /><p>Unsure about a field? Leave this assessment until you can confirm it. Never enter a value just to get through the form.</p></div>
                    </aside>

                    <form className="assessment-form panel" onSubmit={step < STEPS.length - 1 ? nextStep : runPrediction} noValidate>
                      <div className="form-header"><div><p className="eyebrow">{STEPS[step].eyebrow}</p><h2>{STEPS[step].title}</h2><p>{STEPS[step].description}</p></div><div className="form-step-badge">0{step + 1}<span> / 03</span></div></div>
                      <div className="progress-track" role="progressbar" aria-label="Assessment progress" aria-valuemin={1} aria-valuemax={3} aria-valuenow={step + 1}><span style={{ width: `${((step + 1) / STEPS.length) * 100}%` }} /></div>
                      <div className="field-grid">
                        {STEPS[step].fields.map((field) => <Field key={field.key} field={field} value={patient[field.key]} onChange={updateField} invalid={invalidKeys.includes(field.key)} />)}
                      </div>
                      {step === 2 && <div className="clinical-note"><Stethoscope size={17} /><p><strong>Clinical values matter.</strong> The accepted thal codes are 3, 6, and 7, as seen in this project's training file. If a report uses a different coding scheme, ask a professional to map it correctly instead of guessing.</p></div>}
                      {formError && <div className="form-error" role="alert"><XCircle size={17} /><span>{formError}</span></div>}
                      <div className="form-footer">
                        <button type="button" className="button button-ghost" onClick={() => { if (step > 0) { setStep((value) => value - 1); setFormError(''); } else { navigate('overview'); } }}><ArrowLeft size={16} /> {step > 0 ? 'Previous step' : 'Cancel'}</button>
                        {step < STEPS.length - 1 ? (
                          <button type="submit" className="button button-primary">Continue <ArrowRight size={16} /></button>
                        ) : (
                          <button type="submit" className="button button-primary" disabled={isSubmitting || apiStatus === 'offline'}>{isSubmitting ? <><LoaderCircle size={17} className="spin" /> Processing…</> : <>Generate model output <ArrowRight size={16} /></>}</button>
                        )}
                      </div>
                      {apiStatus === 'offline' && <p className="form-bottom-note"><WifiOff size={14} /> API not reached. Start FastAPI before submitting. Your entered values remain in this page until you leave or refresh it.</p>}
                    </form>
                  </div>
                </>
              )}
            </section>
          )}

          {view === 'history' && (
            <section className="view-enter" aria-labelledby="history-title">
              <div className="page-heading">
                <div>
                  <p className="eyebrow">YOUR DIGITAL TWIN</p>
                  <h1 id="history-title">Assessment history</h1>
                  <p className="page-subtitle">
                    Review previously saved research-model assessments.
                    These outputs are not clinical diagnoses.
                  </p>
                </div>
                <button
                  className="button button-secondary"
                  onClick={() => setHistoryRefresh((value) => value + 1)}
                  disabled={historyLoading}
                >
                  <Activity size={16} />
                  {historyLoading ? 'Loading...' : 'Refresh history'}
                </button>
              </div>

              {historyError && (
                <div className="warning-banner" role="alert">
                  <Info size={19} />
                  <div>
                    <strong>History could not be loaded</strong>
                    <p>{historyError}</p>
                    <p>Check that the backend is running, then refresh.</p>
                  </div>
                </div>
              )}

              {historyLoading && historyRecords.length === 0 && (
                <section className="panel history-state">
                  <LoaderCircle size={22} className="spin" />
                  <p>Loading saved records...</p>
                </section>
              )}

              {!historyLoading && !historyError && historyRecords.length === 0 && (
                <section className="panel history-state">
                  <HeartPulse size={28} />
                  <h2>No saved records yet</h2>
                  <p>Complete an assessment to see its saved record here.</p>
                  <button className="button button-primary" onClick={beginAssessment}>
                    Start an assessment <ArrowRight size={16} />
                  </button>
                </section>
              )}

              <div className="history-list">
                {historyRecords.map((record, index) => (
                  <article
                    className="panel history-record"
                    key={`${record.created_at || record.date || 'record'}-${index}`}
                  >
                    <div className="history-record-heading">
                      <div>
                        <p className="eyebrow">
                          {record.record_type === 'ml_cardiovascular_assessment'
                            ? 'ML ASSESSMENT'
                            : 'DIGITAL TWIN RECORD'}
                        </p>
                        <h2>
                          {record.record_type === 'ml_cardiovascular_assessment'
                            ? 'Cardiovascular assessment'
                            : (record.record_type || 'Saved record')
                                .replaceAll('_', ' ')}
                        </h2>
                      </div>
                      <span className="status-tag status-ready">
                        Saved
                      </span>
                    </div>

                    <p className="history-date">
                      {record.created_at
                        ? new Date(record.created_at).toLocaleString()
                        : record.date || 'Date unavailable'}
                    </p>

                    {record.patient_snapshot && (
                      <p className="history-patient">
                        Patient: <strong>{record.patient_snapshot.name || 'Unnamed patient'}</strong>
                        {record.patient_snapshot.patient_id
                          ? ` ? ID: ${record.patient_snapshot.patient_id}`
                          : ''}
                        {record.patient_snapshot.age != null
                          ? ` ? Age: ${record.patient_snapshot.age}`
                          : ''}
                        {record.patient_snapshot.sex
                          ? ` ? ${record.patient_snapshot.sex}`
                          : ''}
                      </p>
                    )}

                    {record.prediction ? (
                      <>
                        <div className="history-metrics">
                          <div>
                            <span>Model score</span>
                            <strong>
                              {record.prediction.risk_score.toFixed(2)}
                            </strong>
                          </div>
                          <div>
                            <span>Model output</span>
                            <strong>
                              {record.prediction.predicted_class}
                            </strong>
                          </div>
                          <div>
                            <span>Model category</span>
                            <strong>
                              {record.prediction.risk_category}
                            </strong>
                          </div>
                        </div>

                        {record.prediction.explanations?.length > 0 && (
                          <details className="history-details">
                            <summary>View model explanations</summary>
                            <ul>
                              {record.prediction.explanations.map((item) => (
                                <li key={item.feature}>
                                  <strong>{item.feature}</strong>
                                  {' — '}{item.description}
                                  {' · '}{item.direction}
                                </li>
                              ))}
                            </ul>
                          </details>
                        )}
                      </>
                    ) : (
                      <p>This record does not contain an ML prediction.</p>
                    )}
                  </article>
                ))}
              </div>

              <p className="history-disclaimer">
                Historical model outputs are for research demonstration only.
                They do not establish a diagnosis or replace professional medical care.
              </p>
            </section>
          )}
          {view === 'guide' && (
            <section className="view-enter" aria-labelledby="guide-title">
              <div className="page-heading"><div><p className="eyebrow">PLAIN-LANGUAGE GUIDE</p><h1 id="guide-title">Know what the tool can — and cannot — tell you.</h1><p className="page-subtitle">The goal is transparency. You deserve to understand where a result comes from and where its limits are.</p></div></div>
              <div className="guide-grid">
                <article className="guide-card view-enter"><div className="guide-number">01</div><div className="guide-icon"><ClipboardCheck size={21} /></div><h2>Use documented values</h2><p>The current model needs 13 fields, including coded ECG and exercise-test values. These should come from clinical records; the form should never encourage a person to invent missing data.</p></article>
                <article className="guide-card view-enter"><div className="guide-number">02</div><div className="guide-icon"><Activity size={21} /></div><h2>The model produces an output</h2><p>CardioTwin uses a Random Forest trained on the 303-row UCI Cleveland dataset. It learned patterns in that dataset; it has not been established as a clinical diagnostic service.</p></article>
                <article className="guide-card view-enter"><div className="guide-number">03</div><div className="guide-icon"><Info size={21} /></div><h2>Explanations are not causes</h2><p>The feature explanations describe how inputs influenced the model's output. They do not prove that a feature caused disease or establish a person's medical condition.</p></article>
                <article className="guide-card view-enter"><div className="guide-number">04</div><div className="guide-icon"><Stethoscope size={21} /></div><h2>Review with a professional</h2><p>Do not start, stop, or change treatment from this output. A qualified healthcare professional can consider your symptoms, history, examination, and appropriate tests.</p></article>
              </div>
              <section className="panel scope-panel view-enter"><div className="panel-heading"><div><h2>What's actually connected today?</h2><p>This avoids showing demo data as if it were a real patient record.</p></div><div className="panel-heading-icon"><CheckCircle2 size={19} /></div></div>
                <div className="scope-row"><span className="scope-status connected"><Check size={14} /></span><div><strong>ML prediction API</strong><p>Connected through FastAPI `POST /api/assessment`, which runs and saves the model output.</p></div><span className="status-tag status-ready">Connected</span></div>
                <div className="scope-row"><span className="scope-status waiting"><Info size={14} /></span><div><strong>Digital twin timeline</strong><p>Assessment saving is connected to FastAPI; a browsable timeline remains to be added.</p></div><span className="status-tag status-next">Next phase</span></div>
                <div className="scope-row"><span className="scope-status waiting"><Info size={14} /></span><div><strong>Medical-care guidance</strong><p>Source modules exist, but they need carefully designed API contracts and safety validation before the patient portal can use them.</p></div><span className="status-tag status-next">Next phase</span></div>
              </section>
              <div className="disclaimer-strip"><ShieldAlert size={19} /><p><strong>Urgent symptoms should never wait for an AI result.</strong> For severe or persistent chest pain, difficulty breathing, fainting, or other urgent symptoms, seek local emergency care.</p></div>
            </section>
          )}
        </main>
        <footer className="page-footer"><span>CardioTwin · Patient portal prototype</span><span><ShieldCheck size={14} /> Research use only · Not a diagnosis</span></footer>
      </div>
    </div>
  );
}

function PredictionView({ prediction, onNew, onOverview }: { prediction: Prediction; onNew: () => void; onOverview: () => void }) {
  const boundedScore = Math.max(0, Math.min(100, prediction.risk_score));
  const scoreStyle = { '--score-width': `${boundedScore}%` } as CSSProperties;
  const modelClass = prediction.predicted_class === 'Disease class' ? 'Disease-class output' : 'No-disease-class output';
  const maxContribution = Math.max(0.0001, ...prediction.explanations.map((item) => Math.abs(item.shap_contribution)));
  return (
    <section aria-labelledby="result-title">
      <div className="page-heading compact-heading"><div><p className="eyebrow">MODEL RESPONSE</p><h1 id="result-title">Your output is ready to review.</h1><p className="page-subtitle">Read this as a research model response — not as a diagnosis or a verified estimate of your personal likelihood of disease.</p></div></div>
      <div className="result-warning"><ShieldAlert size={20} /><div><strong>This is not a medical diagnosis.</strong><p>CardioTwin is a prototype trained on a small, historical dataset. Its score is not a clinically validated individual probability. Discuss any health concerns with a qualified professional.</p></div></div>
      <div className="result-top-grid">
        <article className="result-card score-card view-enter">
          <div className="result-card-heading"><div><p className="eyebrow">MODEL SCORE</p><h2>Internal model output</h2></div><div className="card-icon teal-icon"><Activity size={20} /></div></div>
          <div className="score-value-row"><strong>{boundedScore.toFixed(1)}</strong><span> / 100</span></div>
          <div className="score-track" role="img" aria-label={`Model score ${boundedScore.toFixed(1)} out of 100`}><span style={scoreStyle} /></div>
          <div className="score-scale"><span>0</span><span>50</span><span>100</span></div>
          <div className="model-category"><span className="category-dot" /><div><small>Prototype category</small><strong>{prediction.risk_category}</strong></div></div>
          <p className="fine-print">The numerical score comes from the model's output. The scale and category thresholds have not been clinically validated for individual patients.</p>
        </article>
        <article className="result-card class-card view-enter">
          <div className="result-card-heading"><div><p className="eyebrow">CLASSIFICATION</p><h2>What the model returned</h2></div><div className="card-icon blue-icon"><ClipboardCheck size={20} /></div></div>
          <div className="class-output-icon"><Activity size={28} /></div>
          <h3>{modelClass}</h3>
          <p>The model assigned the submitted values to this class. This does not confirm or rule out a medical condition.</p>
          <div className="class-code-row"><span>Model type</span><code>Random Forest prototype</code></div>
          <div className="class-code-row"><span>Assessment history</span><code>Saved</code></div>
        </article>
      </div>

      <section className="panel explanations-panel view-enter">
        <div className="panel-heading"><div><p className="eyebrow">MODEL EXPLANATION</p><h2>What influenced this output?</h2><p>The following features were returned by the model explanation code.</p></div><div className="panel-heading-icon"><Sparkles size={19} /></div></div>
        {prediction.explanations.length ? (
          <div className="explanation-list">
            {prediction.explanations.map((item, index) => {
              const toward = item.direction.toLowerCase().includes('toward');
              const width = `${Math.max(3, Math.abs(item.shap_contribution) / maxContribution * 100)}%`;
              return <article className="explanation-row" key={`${item.feature}-${index}`}>
                <div className="explanation-main"><div className="explanation-index">{String(index + 1).padStart(2, '0')}</div><div className="explanation-copy"><strong>{item.description || item.feature}</strong><small>Model input: {item.feature} · Value: {Number(item.patient_value).toLocaleString(undefined, { maximumFractionDigits: 2 })}</small><div className="contribution-track"><span className={toward ? 'toward' : 'away'} style={{ width }} /></div></div></div>
                <div className="contribution-value"><strong>{item.shap_contribution > 0 ? '+' : ''}{item.shap_contribution.toFixed(3)}</strong><span>{toward ? 'Toward disease-class output' : 'Away from disease-class output'}</span></div>
              </article>;
            })}
          </div>
        ) : <p className="empty-explanations">The API did not return individual feature explanations for this response.</p>}
        <div className="explanation-footnote"><Info size={16} /><p>These values describe model behavior; they do not show medical causes, treatment needs, or whether any feature is dangerous for you.</p></div>
      </section>
      <div className="result-actions"><button className="button button-secondary" onClick={onOverview}>Back to overview</button><button className="button button-primary" onClick={onNew}>Start a new assessment <ArrowRight size={16} /></button></div>
    </section>
  );
}

export default App;
