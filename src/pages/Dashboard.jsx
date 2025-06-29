import React from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'
import { 
  BookOpen, 
  Users, 
  Calendar, 
  TrendingUp, 
  Star, 
  Clock,
  DollarSign,
  Award,
  MessageCircle,
  Plus
} from 'lucide-react'

const Dashboard = () => {
  const { user } = useAuth()

  const stats = user?.role === 'tutor' ? [
    { label: 'Estudiantes Activos', value: '12', icon: Users, color: 'text-blue-600' },
    { label: 'Sesiones Completadas', value: '48', icon: Calendar, color: 'text-green-600' },
    { label: 'Calificación Promedio', value: '4.8', icon: Star, color: 'text-yellow-600' },
    { label: 'Ingresos del Mes', value: 'S/. 850', icon: DollarSign, color: 'text-purple-600' }
  ] : [
    { label: 'Cursos Inscritos', value: '5', icon: BookOpen, color: 'text-blue-600' },
    { label: 'Sesiones Programadas', value: '8', icon: Calendar, color: 'text-green-600' },
    { label: 'Horas de Estudio', value: '24', icon: Clock, color: 'text-orange-600' },
    { label: 'Progreso Promedio', value: '78%', icon: TrendingUp, color: 'text-purple-600' }
  ]

  const recentActivity = user?.role === 'tutor' ? [
    {
      type: 'session',
      title: 'Sesión de Matemáticas con Ana García',
      time: 'Hace 2 horas',
      status: 'completed'
    },
    {
      type: 'message',
      title: 'Nuevo mensaje de Carlos López',
      time: 'Hace 4 horas',
      status: 'unread'
    },
    {
      type: 'booking',
      title: 'Nueva reserva para Física',
      time: 'Hace 6 horas',
      status: 'pending'
    }
  ] : [
    {
      type: 'session',
      title: 'Próxima sesión de Química',
      time: 'En 2 horas',
      status: 'upcoming'
    },
    {
      type: 'assignment',
      title: 'Tarea de Matemáticas entregada',
      time: 'Hace 1 hora',
      status: 'completed'
    },
    {
      type: 'message',
      title: 'Mensaje del tutor de Física',
      time: 'Hace 3 horas',
      status: 'unread'
    }
  ]

  const upcomingSessions = [
    {
      subject: 'Matemáticas',
      tutor: 'Prof. María González',
      time: '14:00 - 15:00',
      date: 'Hoy',
      type: 'online'
    },
    {
      subject: 'Física',
      tutor: 'Prof. Carlos Ruiz',
      time: '16:00 - 17:00',
      date: 'Mañana',
      type: 'presencial'
    },
    {
      subject: 'Química',
      tutor: 'Prof. Ana Martínez',
      time: '10:00 - 11:00',
      date: 'Viernes',
      type: 'online'
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900">
            ¡Hola, {user?.name}! 👋
          </h1>
          <p className="text-gray-600 mt-2">
            {user?.role === 'tutor' 
              ? 'Aquí tienes un resumen de tu actividad como tutor'
              : 'Aquí tienes un resumen de tu progreso académico'
            }
          </p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="card hover:shadow-lg transition-shadow duration-300"
            >
              <div className="flex items-center">
                <div className={`p-3 rounded-lg bg-gray-100 ${stat.color}`}>
                  <stat.icon className="h-6 w-6" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="card"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Acciones Rápidas</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {user?.role === 'tutor' ? (
                  <>
                    <button className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors duration-200">
                      <Plus className="h-5 w-5 text-gray-400 mr-2" />
                      <span className="text-gray-600">Crear Curso</span>
                    </button>
                    <button className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors duration-200">
                      <Calendar className="h-5 w-5 text-gray-400 mr-2" />
                      <span className="text-gray-600">Programar Sesión</span>
                    </button>
                    <button className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors duration-200">
                      <MessageCircle className="h-5 w-5 text-gray-400 mr-2" />
                      <span className="text-gray-600">Ver Mensajes</span>
                    </button>
                  </>
                ) : (
                  <>
                    <button className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors duration-200">
                      <BookOpen className="h-5 w-5 text-gray-400 mr-2" />
                      <span className="text-gray-600">Buscar Cursos</span>
                    </button>
                    <button className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors duration-200">
                      <Calendar className="h-5 w-5 text-gray-400 mr-2" />
                      <span className="text-gray-600">Agendar Sesión</span>
                    </button>
                    <button className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors duration-200">
                      <Users className="h-5 w-5 text-gray-400 mr-2" />
                      <span className="text-gray-600">Mis Tutores</span>
                    </button>
                  </>
                )}
              </div>
            </motion.div>

            {/* Upcoming Sessions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              className="card"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Próximas Sesiones</h2>
              <div className="space-y-4">
                {upcomingSessions.map((session, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center">
                      <div className="bg-primary-100 p-2 rounded-lg mr-4">
                        <BookOpen className="h-5 w-5 text-primary-600" />
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900">{session.subject}</h3>
                        <p className="text-sm text-gray-600">{session.tutor}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">{session.time}</p>
                      <p className="text-sm text-gray-600">{session.date}</p>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        session.type === 'online' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {session.type}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* Recent Activity */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.6 }}
              className="card"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Actividad Reciente</h2>
              <div className="space-y-4">
                {recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-start">
                    <div className={`p-2 rounded-full mr-3 ${
                      activity.status === 'completed' ? 'bg-green-100' :
                      activity.status === 'unread' ? 'bg-blue-100' :
                      activity.status === 'pending' ? 'bg-yellow-100' :
                      'bg-gray-100'
                    }`}>
                      {activity.type === 'session' && <Calendar className="h-4 w-4 text-green-600" />}
                      {activity.type === 'message' && <MessageCircle className="h-4 w-4 text-blue-600" />}
                      {activity.type === 'booking' && <Clock className="h-4 w-4 text-yellow-600" />}
                      {activity.type === 'assignment' && <Award className="h-4 w-4 text-purple-600" />}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                      <p className="text-xs text-gray-500">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Performance Chart Placeholder */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.7 }}
              className="card"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                {user?.role === 'tutor' ? 'Ingresos del Mes' : 'Progreso Semanal'}
              </h2>
              <div className="h-48 bg-gray-100 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">Gráfico próximamente</p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard