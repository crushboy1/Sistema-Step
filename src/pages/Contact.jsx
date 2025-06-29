import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Mail, 
  Phone, 
  MapPin, 
  Clock, 
  Send, 
  MessageCircle,
  HelpCircle,
  Users,
  CheckCircle
} from 'lucide-react'

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  })
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    // Simular envío del formulario
    setTimeout(() => {
      setIsSubmitted(true)
      setFormData({ name: '', email: '', subject: '', message: '' })
    }, 1000)
  }

  const contactInfo = [
    {
      icon: Mail,
      title: 'Correo Electrónico',
      details: 'contacto@step.edu.pe',
      description: 'Respuesta en 24 horas'
    },
    {
      icon: Phone,
      title: 'Teléfono',
      details: '+51 1 234 5678',
      description: 'Lun - Vie: 9:00 AM - 6:00 PM'
    },
    {
      icon: MapPin,
      title: 'Ubicación',
      details: 'Lima, Perú',
      description: 'Oficinas principales'
    },
    {
      icon: Clock,
      title: 'Horario de Atención',
      details: '9:00 AM - 6:00 PM',
      description: 'Lunes a Viernes'
    }
  ]

  const faqItems = [
    {
      question: '¿Cómo funciona el sistema de tutorías?',
      answer: 'Conectamos estudiantes con tutores pares que han destacado en las materias que necesitas. Puedes buscar tutores, ver sus perfiles y programar sesiones según tu disponibilidad.'
    },
    {
      question: '¿Cuáles son los costos de las tutorías?',
      answer: 'Los precios varían según el tutor y la materia, pero mantenemos tarifas accesibles para estudiantes. El promedio está entre S/. 20-35 por sesión de una hora.'
    },
    {
      question: '¿Cómo puedo convertirme en tutor?',
      answer: 'Regístrate como tutor, completa tu perfil académico y pasa por nuestro proceso de verificación. Necesitas tener buen rendimiento en las materias que quieres enseñar.'
    },
    {
      question: '¿Las sesiones son presenciales u online?',
      answer: 'Ofrecemos ambas modalidades. Puedes elegir sesiones presenciales en ubicaciones convenientes o sesiones online a través de nuestra plataforma integrada.'
    }
  ]

  const supportOptions = [
    {
      icon: MessageCircle,
      title: 'Chat en Vivo',
      description: 'Habla con nuestro equipo de soporte',
      action: 'Iniciar Chat'
    },
    {
      icon: HelpCircle,
      title: 'Centro de Ayuda',
      description: 'Encuentra respuestas a preguntas frecuentes',
      action: 'Ver Artículos'
    },
    {
      icon: Users,
      title: 'Comunidad',
      description: 'Únete a nuestro foro de estudiantes',
      action: 'Acceder al Foro'
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Contáctanos
            </h1>
            <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto opacity-90">
              ¿Tienes preguntas? Estamos aquí para ayudarte. 
              Contáctanos y te responderemos lo antes posible.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Contact Info */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
            {contactInfo.map((info, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="card text-center hover:shadow-lg transition-shadow duration-300"
              >
                <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <info.icon className="h-8 w-8 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {info.title}
                </h3>
                <p className="text-lg font-medium text-primary-600 mb-1">
                  {info.details}
                </p>
                <p className="text-sm text-gray-600">
                  {info.description}
                </p>
              </motion.div>
            ))}
          </div>

          <div className="grid lg:grid-cols-2 gap-12">
            {/* Contact Form */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="card"
            >
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Envíanos un Mensaje
              </h2>
              
              {isSubmitted ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-center py-8"
                >
                  <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    ¡Mensaje Enviado!
                  </h3>
                  <p className="text-gray-600">
                    Gracias por contactarnos. Te responderemos pronto.
                  </p>
                  <button
                    onClick={() => setIsSubmitted(false)}
                    className="btn-primary mt-4"
                  >
                    Enviar Otro Mensaje
                  </button>
                </motion.div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                        Nombre Completo
                      </label>
                      <input
                        type="text"
                        id="name"
                        name="name"
                        required
                        className="input-field"
                        placeholder="Tu nombre"
                        value={formData.name}
                        onChange={handleChange}
                      />
                    </div>
                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                        Correo Electrónico
                      </label>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        required
                        className="input-field"
                        placeholder="tu@email.com"
                        value={formData.email}
                        onChange={handleChange}
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
                      Asunto
                    </label>
                    <select
                      id="subject"
                      name="subject"
                      required
                      className="input-field"
                      value={formData.subject}
                      onChange={handleChange}
                    >
                      <option value="">Selecciona un asunto</option>
                      <option value="general">Consulta General</option>
                      <option value="tutor">Quiero ser Tutor</option>
                      <option value="technical">Soporte Técnico</option>
                      <option value="billing">Facturación</option>
                      <option value="feedback">Comentarios y Sugerencias</option>
                    </select>
                  </div>
                  
                  <div>
                    <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                      Mensaje
                    </label>
                    <textarea
                      id="message"
                      name="message"
                      rows={6}
                      required
                      className="input-field"
                      placeholder="Escribe tu mensaje aquí..."
                      value={formData.message}
                      onChange={handleChange}
                    />
                  </div>
                  
                  <button
                    type="submit"
                    className="btn-primary w-full flex items-center justify-center"
                  >
                    <Send className="h-5 w-5 mr-2" />
                    Enviar Mensaje
                  </button>
                </form>
              )}
            </motion.div>

            {/* Support Options */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="space-y-8"
            >
              <div className="card">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  Otras Formas de Contacto
                </h2>
                <div className="space-y-4">
                  {supportOptions.map((option, index) => (
                    <div key={index} className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200">
                      <div className="bg-primary-100 p-3 rounded-lg mr-4">
                        <option.icon className="h-6 w-6 text-primary-600" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">{option.title}</h3>
                        <p className="text-sm text-gray-600">{option.description}</p>
                      </div>
                      <button className="btn-secondary text-sm">
                        {option.action}
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* FAQ Preview */}
              <div className="card">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  Preguntas Frecuentes
                </h2>
                <div className="space-y-4">
                  {faqItems.slice(0, 2).map((faq, index) => (
                    <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0">
                      <h3 className="font-semibold text-gray-900 mb-2">
                        {faq.question}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {faq.answer}
                      </p>
                    </div>
                  ))}
                </div>
                <button className="btn-secondary w-full mt-4">
                  Ver Todas las Preguntas
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Preguntas Frecuentes
            </h2>
            <p className="text-xl text-gray-600">
              Encuentra respuestas rápidas a las preguntas más comunes
            </p>
          </motion.div>

          <div className="space-y-6">
            {faqItems.map((faq, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="card"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  {faq.question}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {faq.answer}
                </p>
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
              ¿No encontraste lo que buscabas?
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Nuestro equipo de soporte está listo para ayudarte con cualquier consulta
            </p>
            <button className="bg-white text-primary-600 hover:bg-gray-100 font-semibold py-4 px-8 rounded-lg transition-colors duration-200">
              Contactar Soporte Directo
            </button>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default Contact