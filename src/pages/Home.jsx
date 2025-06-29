import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  BookOpen, 
  Users, 
  Award, 
  Clock, 
  Star, 
  ArrowRight,
  CheckCircle,
  GraduationCap,
  MessageCircle,
  TrendingUp
} from 'lucide-react'

const Home = () => {
  const features = [
    {
      icon: Users,
      title: 'Tutorías Personalizadas',
      description: 'Conecta con tutores especializados en tu área de estudio para recibir ayuda personalizada.'
    },
    {
      icon: Clock,
      title: 'Horarios Flexibles',
      description: 'Programa sesiones de tutoría que se adapten a tu horario y disponibilidad.'
    },
    {
      icon: Award,
      title: 'Tutores Certificados',
      description: 'Todos nuestros tutores son estudiantes destacados con experiencia comprobada.'
    },
    {
      icon: MessageCircle,
      title: 'Comunicación Directa',
      description: 'Comunícate directamente con tu tutor para resolver dudas y coordinar sesiones.'
    }
  ]

  const stats = [
    { number: '500+', label: 'Estudiantes Activos' },
    { number: '150+', label: 'Tutores Disponibles' },
    { number: '1000+', label: 'Sesiones Completadas' },
    { number: '4.8/5', label: 'Calificación Promedio' }
  ]

  const testimonials = [
    {
      name: 'María González',
      role: 'Estudiante de Ingeniería',
      content: 'Gracias a STEP pude mejorar mis calificaciones en matemáticas. Mi tutor fue muy paciente y explicó todo de manera clara.',
      avatar: 'https://ui-avatars.com/api/?name=María+González&background=3b82f6&color=fff'
    },
    {
      name: 'Carlos Rodríguez',
      role: 'Tutor de Física',
      content: 'Como tutor, STEP me ha permitido ayudar a otros estudiantes mientras genero ingresos adicionales. Es una plataforma excelente.',
      avatar: 'https://ui-avatars.com/api/?name=Carlos+Rodríguez&background=22c55e&color=fff'
    },
    {
      name: 'Ana Martínez',
      role: 'Estudiante de Medicina',
      content: 'La flexibilidad de horarios y la calidad de los tutores hacen de STEP la mejor opción para recibir apoyo académico.',
      avatar: 'https://ui-avatars.com/api/?name=Ana+Martínez&background=8b5cf6&color=fff'
    }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="hero-gradient text-white py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h1 className="text-4xl md:text-6xl font-bold mb-6">
                Sistema de Tutorías
                <span className="block text-yellow-300">entre Pares</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto opacity-90">
                Conecta con tutores estudiantes y mejora tu rendimiento académico 
                con sesiones personalizadas y flexibles.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/register"
                  className="bg-white text-primary-600 hover:bg-gray-100 font-semibold py-4 px-8 rounded-lg transition-colors duration-200 flex items-center justify-center"
                >
                  Comenzar Ahora
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
                <Link
                  to="/about"
                  className="border-2 border-white text-white hover:bg-white hover:text-primary-600 font-semibold py-4 px-8 rounded-lg transition-colors duration-200"
                >
                  Conocer Más
                </Link>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-3xl md:text-4xl font-bold text-primary-600 mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-600">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              ¿Por qué elegir STEP?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Nuestra plataforma está diseñada para facilitar el aprendizaje colaborativo 
              entre estudiantes, creando una comunidad de apoyo académico.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="card text-center hover:shadow-lg transition-shadow duration-300"
              >
                <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="h-8 w-8 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              ¿Cómo funciona?
            </h2>
            <p className="text-xl text-gray-600">
              Tres simples pasos para comenzar tu experiencia de aprendizaje
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center"
            >
              <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                1
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Regístrate
              </h3>
              <p className="text-gray-600">
                Crea tu cuenta como estudiante o tutor y completa tu perfil académico.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-center"
            >
              <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                2
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Encuentra tu Tutor
              </h3>
              <p className="text-gray-600">
                Explora los perfiles de tutores disponibles y elige el que mejor se adapte a tus necesidades.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="text-center"
            >
              <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                3
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Comienza a Aprender
              </h3>
              <p className="text-gray-600">
                Programa tu primera sesión y comienza a mejorar tu rendimiento académico.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Lo que dicen nuestros usuarios
            </h2>
            <p className="text-xl text-gray-600">
              Testimonios reales de estudiantes y tutores que forman parte de nuestra comunidad
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="card"
              >
                <div className="flex items-center mb-4">
                  <img
                    src={testimonial.avatar}
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full mr-4"
                  />
                  <div>
                    <h4 className="font-semibold text-gray-900">{testimonial.name}</h4>
                    <p className="text-sm text-gray-600">{testimonial.role}</p>
                  </div>
                </div>
                <p className="text-gray-600 italic">"{testimonial.content}"</p>
                <div className="flex mt-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              ¿Listo para mejorar tu rendimiento académico?
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Únete a miles de estudiantes que ya están mejorando sus calificaciones con STEP
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="bg-white text-primary-600 hover:bg-gray-100 font-semibold py-4 px-8 rounded-lg transition-colors duration-200 flex items-center justify-center"
              >
                <GraduationCap className="mr-2 h-5 w-5" />
                Registrarse como Estudiante
              </Link>
              <Link
                to="/register"
                className="border-2 border-white text-white hover:bg-white hover:text-primary-600 font-semibold py-4 px-8 rounded-lg transition-colors duration-200 flex items-center justify-center"
              >
                <Users className="mr-2 h-5 w-5" />
                Ser Tutor
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default Home