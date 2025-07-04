import { useState, useEffect } from 'react'
import './App.css'
import ApiService from './services/api'

function App() {
  const [currentView, setCurrentView] = useState('landing')
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('token')
      if (token) {
        const response = await ApiService.verifyToken()
        if (response.valid) {
          setUser(response.user)
          setCurrentView('dashboard')
        }
      }
    } catch (error) {
      console.error('Error verificando token:', error)
      ApiService.removeToken()
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (formData) => {
    try {
      setLoading(true)
      setError('')
      
      const response = await ApiService.register({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        age: parseInt(formData.age),
        weight: parseFloat(formData.weight),
        height: parseFloat(formData.height),
        goal: formData.goal,
        activity_level: 'moderate',
        experience_level: 'beginner'
      })
      
      setUser(response.user)
      setCurrentView('dashboard')
      setSuccess('¡Cuenta creada exitosamente!')
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async (formData) => {
    try {
      setLoading(true)
      setError('')
      
      const response = await ApiService.login({
        email: formData.email,
        password: formData.password
      })
      
      setUser(response.user)
      setCurrentView('dashboard')
      setSuccess('¡Bienvenido de vuelta!')
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    ApiService.logout()
    setUser(null)
    setCurrentView('landing')
    setSuccess('Sesión cerrada exitosamente')
  }

  const generateWorkoutPlan = async () => {
    try {
      setLoading(true)
      setError('')
      
      const response = await ApiService.generateWorkoutPlan(4)
      setSuccess('¡Plan de entrenamiento generado exitosamente!')
      console.log('Plan generado:', response.plan)
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  const generateNutritionPlan = async () => {
    try {
      setLoading(true)
      setError('')
      
      const response = await ApiService.generateNutritionPlan(4)
      setSuccess('¡Plan nutricional generado exitosamente!')
      console.log('Plan generado:', response.plan)
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading && currentView !== 'register' && currentView !== 'login') {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Cargando...</p>
      </div>
    )
  }

  return (
    <div className="App">
      {/* Notificaciones */}
      {error && (
        <div className="notification error">
          {error}
          <button onClick={() => setError('')}>×</button>
        </div>
      )}
      {success && (
        <div className="notification success">
          {success}
          <button onClick={() => setSuccess('')}>×</button>
        </div>
      )}

      {currentView === 'landing' && <LandingPage setCurrentView={setCurrentView} />}
      {currentView === 'register' && <RegisterForm onSubmit={handleRegister} setCurrentView={setCurrentView} loading={loading} />}
      {currentView === 'login' && <LoginForm onSubmit={handleLogin} setCurrentView={setCurrentView} loading={loading} />}
      {currentView === 'dashboard' && <Dashboard user={user} onLogout={handleLogout} setCurrentView={setCurrentView} />}
      {currentView === 'workout' && <WorkoutView user={user} onLogout={handleLogout} setCurrentView={setCurrentView} generatePlan={generateWorkoutPlan} />}
      {currentView === 'nutrition' && <NutritionView user={user} onLogout={handleLogout} setCurrentView={setCurrentView} generatePlan={generateNutritionPlan} />}
      {currentView === 'progress' && <ProgressView user={user} onLogout={handleLogout} setCurrentView={setCurrentView} />}
      {currentView === 'settings' && <SettingsView user={user} onLogout={handleLogout} setCurrentView={setCurrentView} />}
    </div>
  )
}

function LandingPage({ setCurrentView }) {
  return (
    <div className="landing-page">
      <header className="header">
        <div className="logo">
          <span className="logo-icon">⚡</span>
          <span className="logo-text">Glow-Up AI</span>
        </div>
        <div className="header-buttons">
          <button className="btn-secondary" onClick={() => setCurrentView('login')}>
            Iniciar Sesión
          </button>
          <button className="btn-primary" onClick={() => setCurrentView('register')}>
            Comenzar Gratis
          </button>
        </div>
      </header>

      <main className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Tu <span className="gradient-text">Transformación</span><br />
            Comienza Aquí
          </h1>
          <p className="hero-description">
            La plataforma de fitness más avanzada del mundo. Combina inteligencia artificial, 
            planes personalizados y seguimiento profesional para alcanzar tus objetivos.
          </p>
          <div className="hero-buttons">
            <button className="btn-primary large" onClick={() => setCurrentView('register')}>
              <span>Comenzar Gratis</span>
              <span className="btn-icon">🚀</span>
            </button>
            <button className="btn-secondary large" onClick={() => setCurrentView('login')}>
              Iniciar Sesión
            </button>
          </div>
        </div>
      </main>

      <section className="features">
        <h2>Todo lo que Necesitas para Triunfar</h2>
        <p>Herramientas profesionales y tecnología de vanguardia en una sola plataforma</p>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🏋️</div>
            <h3>Entrenamientos Personalizados</h3>
            <p>Rutinas adaptadas a tu nivel y objetivos, generadas por IA avanzada.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🥗</div>
            <h3>Planes Nutricionales</h3>
            <p>Dietas balanceadas y personalizadas para potenciar tus resultados.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>IA Adaptativa</h3>
            <p>Aprende de tu progreso y ajusta los planes automáticamente.</p>
          </div>
        </div>
      </section>

      <section className="testimonials">
        <h2>Usuarios Satisfechos Cerca de Ti</h2>
        <p>Descubre las increíbles transformaciones de personas que ya están usando nuestra plataforma</p>
        
        <div className="testimonials-grid">
          <div className="testimonial-card">
            <div className="testimonial-header">
              <h4>María González</h4>
              <p>28 años • Polanco, CDMX</p>
              <div className="achievement">🎉 Perdió 15kg en 6 meses</div>
            </div>
            <p>"Esta plataforma cambió completamente mi vida. Los planes personalizados y el seguimiento con IA hicieron que alcanzar mis objetivos fuera mucho más fácil."</p>
          </div>
          <div className="testimonial-card">
            <div className="testimonial-header">
              <h4>Carlos Rodríguez</h4>
              <p>35 años • Roma Norte, CDMX</p>
              <div className="achievement">💪 Ganó 8kg de músculo</div>
            </div>
            <p>"Los entrenamientos son perfectos para mi nivel. La IA realmente entiende mis necesidades y me ha ayudado a ganar masa muscular de forma eficiente."</p>
          </div>
          <div className="testimonial-card">
            <div className="testimonial-header">
              <h4>Ana Martínez</h4>
              <p>42 años • Condesa, CDMX</p>
              <div className="achievement">🏃‍♀️ Completó su primer maratón</div>
            </div>
            <p>"Nunca pensé que podría correr un maratón. Los planes de entrenamiento progresivos me llevaron desde cero hasta la meta en 8 meses."</p>
          </div>
        </div>
      </section>

      <section className="cta">
        <h2>¿Listo para tu Transformación?</h2>
        <p>Únete a miles de personas que ya han transformado su vida con nuestra tecnología.</p>
        <button className="btn-primary large" onClick={() => setCurrentView('register')}>
          Comenzar Mi Transformación
        </button>
      </section>
    </div>
  )
}

function RegisterForm({ onSubmit, setCurrentView, loading }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    age: '',
    weight: '',
    height: '',
    goal: ''
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <span className="logo-icon">⚡</span>
          <h2>Crear Cuenta</h2>
          <p>Completa tu perfil para generar planes personalizados</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-row">
            <div className="form-group">
              <label>Nombre Completo</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Tu nombre"
                required
              />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="tu@email.com"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Contraseña</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Edad</label>
              <input
                type="number"
                name="age"
                value={formData.age}
                onChange={handleChange}
                placeholder="25"
                required
              />
            </div>
            <div className="form-group">
              <label>Peso (kg)</label>
              <input
                type="number"
                name="weight"
                value={formData.weight}
                onChange={handleChange}
                placeholder="70"
                step="0.1"
                required
              />
            </div>
            <div className="form-group">
              <label>Altura (cm)</label>
              <input
                type="number"
                name="height"
                value={formData.height}
                onChange={handleChange}
                placeholder="175"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Objetivo Principal</label>
            <select
              name="goal"
              value={formData.goal}
              onChange={handleChange}
              required
            >
              <option value="">Selecciona tu objetivo</option>
              <option value="lose_weight">Perder peso</option>
              <option value="gain_muscle">Ganar músculo</option>
              <option value="maintain_weight">Mantener peso</option>
              <option value="improve_endurance">Mejorar resistencia</option>
            </select>
          </div>

          <button type="submit" className="btn-primary full-width" disabled={loading}>
            {loading ? 'Creando cuenta...' : 'Crear Mi Cuenta'}
          </button>

          <button type="button" className="btn-secondary full-width" onClick={() => setCurrentView('landing')}>
            Volver
          </button>
        </form>
      </div>
    </div>
  )
}

function LoginForm({ onSubmit, setCurrentView, loading }) {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <span className="logo-icon">⚡</span>
          <h2>Iniciar Sesión</h2>
          <p>Bienvenido de vuelta a tu transformación</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="tu@email.com"
              required
            />
          </div>

          <div className="form-group">
            <label>Contraseña</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
            />
          </div>

          <button type="submit" className="btn-primary full-width" disabled={loading}>
            {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </button>

          <button type="button" className="btn-secondary full-width" onClick={() => setCurrentView('landing')}>
            Volver
          </button>
        </form>
      </div>
    </div>
  )
}

function Dashboard({ user, onLogout, setCurrentView }) {
  return (
    <div className="dashboard">
      <Header user={user} onLogout={onLogout} setCurrentView={setCurrentView} />
      
      <main className="dashboard-main">
        <div className="welcome-section">
          <h1>Bienvenido de vuelta, {user?.name}</h1>
          <p>Día 1 de tu transformación</p>
        </div>

        <div className="motivation-card">
          <div className="motivation-icon">💖</div>
          <h2>Enfoque de Hoy</h2>
          <p>"El fitness es un regalo que te das a ti mismo."</p>
        </div>

        <div className="action-cards">
          <div className="action-card">
            <div className="action-icon">🏋️</div>
            <h3>Crear Plan de Entrenamiento</h3>
            <p>Genera un plan personalizado con IA</p>
            <button className="btn-primary" onClick={() => setCurrentView('workout')}>
              <span>Generar Plan</span>
              <span>⚡</span>
            </button>
          </div>

          <div className="action-card">
            <div className="action-icon">🥗</div>
            <h3>Crear Plan Nutricional</h3>
            <p>Genera un plan de alimentación personalizado con IA</p>
            <button className="btn-primary" onClick={() => setCurrentView('nutrition')}>
              <span>Generar Plan</span>
              <span>⚡</span>
            </button>
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <h3>Peso Actual</h3>
            <div className="stat-value">{user?.weight} kg</div>
          </div>
          <div className="stat-card">
            <h3>Grasa Corporal</h3>
            <div className="stat-value">18.2%</div>
          </div>
          <div className="stat-card">
            <h3>Entrenamientos</h3>
            <div className="stat-value">12</div>
          </div>
        </div>
      </main>
    </div>
  )
}

function WorkoutView({ user, onLogout, setCurrentView, generatePlan }) {
  return (
    <div className="dashboard">
      <Header user={user} onLogout={onLogout} setCurrentView={setCurrentView} />
      
      <main className="dashboard-main">
        <div className="page-header">
          <h1>Mis Rutinas</h1>
          <p>Gestiona tus fases de entrenamiento con IA</p>
        </div>

        <div className="current-plan">
          <div className="plan-header">
            <h2>Plan Actual</h2>
            <span className="plan-badge">IA</span>
          </div>
          <h3>Fase de Volumen - Hipertrofia Inicial</h3>
          <div className="plan-progress">
            <span>Semana 1 de 4</span>
            <span>2025-07-04</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{width: '25%'}}></div>
          </div>
        </div>

        <div className="weekly-schedule">
          <h3>Cronograma Semanal</h3>
          <div className="schedule-grid">
            {['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'].map((day, index) => {
              const workouts = ['Fuerza A', 'Fuerza B', 'Cardio', 'Fuerza B', 'Cardio', 'Fuerza B', 'Descanso']
              const durations = ['55 min', '55 min', '55 min', '55 min', '55 min', '55 min', '-']
              const isActive = index === 0
              
              return (
                <div key={day} className={`schedule-day ${isActive ? 'active' : ''}`}>
                  <div className="day-name">{day}</div>
                  <div className="workout-type">{workouts[index]}</div>
                  <div className="workout-duration">{durations[index]}</div>
                </div>
              )
            })}
          </div>
        </div>

        <button className="btn-primary" onClick={generatePlan}>
          <span>Generar Nuevo Plan</span>
          <span>⚡</span>
        </button>
      </main>
    </div>
  )
}

function NutritionView({ user, onLogout, setCurrentView, generatePlan }) {
  return (
    <div className="dashboard">
      <Header user={user} onLogout={onLogout} setCurrentView={setCurrentView} />
      
      <main className="dashboard-main">
        <div className="page-header">
          <h1>Mi Nutrición</h1>
          <p>Gestiona tus planes alimenticios con IA</p>
        </div>

        <div className="empty-state">
          <div className="empty-icon">🍎</div>
          <h2>¡Comienza tu viaje nutricional!</h2>
          <p>Crea tu primer plan personalizado con IA y empieza a alcanzar tus objetivos de salud.</p>
          <button className="btn-primary" onClick={generatePlan}>
            <span>Generar Mi Primer Plan</span>
            <span>⚡</span>
          </button>
        </div>
      </main>
    </div>
  )
}

function ProgressView({ user, onLogout, setCurrentView }) {
  return (
    <div className="dashboard">
      <Header user={user} onLogout={onLogout} setCurrentView={setCurrentView} />
      
      <main className="dashboard-main">
        <div className="page-header">
          <h1>Mi Progreso</h1>
          <p>Seguimiento detallado de tu transformación</p>
        </div>

        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h2>Comienza a registrar tu progreso</h2>
          <p>Registra tu peso, medidas y fotos para ver tu evolución.</p>
          <button className="btn-primary">
            Agregar Primera Medición
          </button>
        </div>
      </main>
    </div>
  )
}

function SettingsView({ user, onLogout, setCurrentView }) {
  return (
    <div className="dashboard">
      <Header user={user} onLogout={onLogout} setCurrentView={setCurrentView} />
      
      <main className="dashboard-main">
        <div className="page-header">
          <h1>Configuración</h1>
          <p>Personaliza tu experiencia</p>
        </div>

        <div className="settings-section">
          <h3>Información Personal</h3>
          <div className="settings-grid">
            <div className="setting-item">
              <label>Nombre</label>
              <input type="text" value={user?.name || ''} readOnly />
            </div>
            <div className="setting-item">
              <label>Email</label>
              <input type="email" value={user?.email || ''} readOnly />
            </div>
            <div className="setting-item">
              <label>Edad</label>
              <input type="number" value={user?.age || ''} readOnly />
            </div>
            <div className="setting-item">
              <label>Peso (kg)</label>
              <input type="number" value={user?.weight || ''} readOnly />
            </div>
            <div className="setting-item">
              <label>Altura (cm)</label>
              <input type="number" value={user?.height || ''} readOnly />
            </div>
            <div className="setting-item">
              <label>Objetivo</label>
              <input type="text" value={user?.goal || ''} readOnly />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function Header({ user, onLogout, setCurrentView }) {
  return (
    <header className="dashboard-header">
      <div className="header-left">
        <div className="logo">
          <span className="logo-icon">⚡</span>
          <span className="logo-text">Glow-Up AI</span>
        </div>
      </div>

      <nav className="header-nav">
        <button 
          className="nav-item active" 
          onClick={() => setCurrentView('dashboard')}
        >
          <span>📊</span>
          Dashboard
        </button>
        <button 
          className="nav-item" 
          onClick={() => setCurrentView('workout')}
        >
          <span>🏋️</span>
          Entrenamiento
        </button>
        <button 
          className="nav-item" 
          onClick={() => setCurrentView('nutrition')}
        >
          <span>🥗</span>
          Nutrición
        </button>
        <button 
          className="nav-item" 
          onClick={() => setCurrentView('progress')}
        >
          <span>📈</span>
          Progreso
        </button>
        <button 
          className="nav-item" 
          onClick={() => setCurrentView('settings')}
        >
          <span>⚙️</span>
          Configuración
        </button>
      </nav>

      <div className="header-right">
        <span className="user-greeting">Hola, {user?.name}</span>
        <button className="btn-secondary" onClick={onLogout}>
          Cerrar Sesión
        </button>
      </div>
    </header>
  )
}

export default App

