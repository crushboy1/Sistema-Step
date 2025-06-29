import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Calendar, 
  Edit3, 
  Save, 
  X,
  Camera,
  Star,
  Award,
  BookOpen,
  Users,
  Clock
} from 'lucide-react'

const Profile = () => {
  const { user } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: '+51 987 654 321',
    location: 'Lima, Perú',
    bio: user?.role === 'tutor' 
      ? 'Tutor especializado en matemáticas con 5 años de experiencia ayudando a estudiantes universitarios.'
      : 'Estudiante de Ingeniería de Sistemas apasionado por el aprendizaje continuo.',
    university: 'Universidad Nacional Mayor de San Marcos',
    career: user?.role === 'tutor' ? 'Matemáticas' : 'Ingeniería de Sistemas',
    semester: user?.role === 'tutor' ? 'Egresado' : '6to Semestre'
  })

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSave = () => {
    // Aquí iría la lógica para guardar los cambios
    setIsEditing(false)
  }

  const stats = user?.role === 'tutor' ? [
    { label: 'Estudiantes Enseñados', value: '127', icon: Users },
    { label: 'Sesiones Completadas', value: '342', icon: Clock },
    { label: 'Calificación Promedio', value: '4.9', icon: Star },
    { label: 'Cursos Activos', value: '8', icon: BookOpen }
  ] : [
    { label: 'Cursos Completados', value: '12', icon: BookOpen },
    { label: 'Horas de Estudio', value: '156', icon: Clock },
    { label: 'Tutores Seguidos', value: '8', icon: Users },
    { label: 'Certificados', value: '3', icon: Award }
  ]

  const achievements = user?.role === 'tutor' ? [
    { title: 'Tutor Destacado', description: 'Top 10% de tutores mejor calificados', icon: Star },
    { title: 'Mentor Experimentado', description: 'Más de 300 sesiones completadas', icon: Award },
    { title: 'Especialista en Matemáticas', description: 'Certificado en enseñanza avanzada', icon: BookOpen }
  ] : [
    { title: 'Estudiante Dedicado', description: 'Más de 100 horas de estudio', icon: Clock },
    { title: 'Aprendiz Constante', description: '12 cursos completados exitosamente', icon: BookOpen },
    { title: 'Participación Activa', description: 'Miembro activo de la comunidad', icon: Users }
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Profile Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="card mb-8"
        >
          <div className="flex flex-col md:flex-row items-center md:items-start space-y-4 md:space-y-0 md:space-x-6">
            {/* Avatar */}
            <div className="relative">
              <img
                src={user?.avatar}
                alt={user?.name}
                className="w-32 h-32 rounded-full border-4 border-white shadow-lg"
              />
              <button className="absolute bottom-2 right-2 bg-primary-600 text-white p-2 rounded-full hover:bg-primary-700 transition-colors duration-200">
                <Camera className="h-4 w-4" />
              </button>
            </div>

            {/* Basic Info */}
            <div className="flex-1 text-center md:text-left">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">{user?.name}</h1>
                  <p className="text-lg text-primary-600 capitalize">{user?.role}</p>
                </div>
                <button
                  onClick={() => setIsEditing(!isEditing)}
                  className={`mt-4 md:mt-0 flex items-center px-4 py-2 rounded-lg transition-colors duration-200 ${
                    isEditing 
                      ? 'bg-gray-100 text-gray-700 hover:bg-gray-200' 
                      : 'bg-primary-600 text-white hover:bg-primary-700'
                  }`}
                >
                  {isEditing ? (
                    <>
                      <X className="h-4 w-4 mr-2" />
                      Cancelar
                    </>
                  ) : (
                    <>
                      <Edit3 className="h-4 w-4 mr-2" />
                      Editar Perfil
                    </>
                  )}
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                <div className="flex items-center">
                  <Mail className="h-4 w-4 mr-2" />
                  {formData.email}
                </div>
                <div className="flex items-center">
                  <Phone className="h-4 w-4 mr-2" />
                  {formData.phone}
                </div>
                <div className="flex items-center">
                  <MapPin className="h-4 w-4 mr-2" />
                  {formData.location}
                </div>
                <div className="flex items-center">
                  <Calendar className="h-4 w-4 mr-2" />
                  Miembro desde Enero 2024
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
        >
          {stats.map((stat, index) => (
            <div key={index} className="card text-center">
              <div className="bg-primary-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                <stat.icon className="h-6 w-6 text-primary-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</div>
              <div className="text-sm text-gray-600">{stat.label}</div>
            </div>
          ))}
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* About Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="card"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Acerca de mí</h2>
              {isEditing ? (
                <div className="space-y-4">
                  <textarea
                    name="bio"
                    value={formData.bio}
                    onChange={handleChange}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="Cuéntanos sobre ti..."
                  />
                  <button
                    onClick={handleSave}
                    className="btn-primary flex items-center"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Guardar Cambios
                  </button>
                </div>
              ) : (
                <p className="text-gray-600 leading-relaxed">{formData.bio}</p>
              )}
            </motion.div>

            {/* Academic Info */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="card"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Información Académica</h2>
              {isEditing ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Universidad
                    </label>
                    <input
                      type="text"
                      name="university"
                      value={formData.university}
                      onChange={handleChange}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Carrera
                    </label>
                    <input
                      type="text"
                      name="career"
                      value={formData.career}
                      onChange={handleChange}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Semestre/Estado
                    </label>
                    <input
                      type="text"
                      name="semester"
                      value={formData.semester}
                      onChange={handleChange}
                      className="input-field"
                    />
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-gray-700">Universidad:</span>
                    <p className="text-gray-900">{formData.university}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-700">Carrera:</span>
                    <p className="text-gray-900">{formData.career}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-700">
                      {user?.role === 'tutor' ? 'Estado:' : 'Semestre:'}
                    </span>
                    <p className="text-gray-900">{formData.semester}</p>
                  </div>
                </div>
              )}
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* Contact Info */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="card"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Contacto</h2>
              {isEditing ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Teléfono
                    </label>
                    <input
                      type="text"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Ubicación
                    </label>
                    <input
                      type="text"
                      name="location"
                      value={formData.location}
                      onChange={handleChange}
                      className="input-field"
                    />
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center">
                    <Phone className="h-4 w-4 text-gray-400 mr-3" />
                    <span className="text-gray-900">{formData.phone}</span>
                  </div>
                  <div className="flex items-center">
                    <MapPin className="h-4 w-4 text-gray-400 mr-3" />
                    <span className="text-gray-900">{formData.location}</span>
                  </div>
                </div>
              )}
            </motion.div>

            {/* Achievements */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              className="card"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Logros</h2>
              <div className="space-y-4">
                {achievements.map((achievement, index) => (
                  <div key={index} className="flex items-start">
                    <div className="bg-primary-100 p-2 rounded-lg mr-3 mt-1">
                      <achievement.icon className="h-4 w-4 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{achievement.title}</h3>
                      <p className="text-sm text-gray-600">{achievement.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile