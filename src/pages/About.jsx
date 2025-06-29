import React from 'react'
import { motion } from 'framer-motion'
import { 
  Users, 
  Target, 
  Heart, 
  Award, 
  BookOpen, 
  TrendingUp,
  CheckCircle,
  Star
} from 'lucide-react'

const About = () => {
  const values = [
    {
      icon: Heart,
      title: 'Pasión por la Educación',
      description: 'Creemos que la educación es la herramienta más poderosa para cambiar el mundo y mejorar vidas.'
    },
    {
      icon: Users,
      title: 'Comunidad Colaborativa',
      description: 'Fomentamos un ambiente donde estudiantes y tutores se apoyan mutuamente para alcanzar el éxito.'
    },
    {
      icon: Target,
      title: 'Excelencia Académica',
      description: 'Nos comprometemos a mantener los más altos estándares de calidad en todas nuestras tutorías.'
    },
    {
      icon: Award,
      title: 'Reconocimiento del Mérito',
      description: 'Valoramos y reconocemos el esfuerzo, dedicación y logros de nuestra comunidad educativa.'
    }
  ]

  const features = [
    'Tutores estudiantes certificados y experimentados',
    'Horarios flexibles que se adaptan a tu agenda',
    'Sesiones personalizadas según tus necesidades',
    'Plataforma intuitiva y fácil de usar',
    'Comunicación directa con tu tutor',
    'Seguimiento del progreso académico',
    'Precios accesibles para estudiantes',
    'Soporte técnico 24/7'
  ]

  const team = [
    {
      name: 'Dr. María González',
      role: 'Directora Académica',
      image: 'https://ui-avatars.com/api/?name=María+González&background=3b82f6&color=fff&size=150',
      description: 'PhD en Educación con 15 años de experiencia en metodologías de enseñanza.'
    },
    {
      name: 'Carlos Rodríguez',
      role: 'Coordinador de Tutores',
      image: 'https://ui-avatars.com/api/?name=Carlos+Rodríguez&background=22c55e&color=fff&size=150',
      description: 'Especialista en gestión educativa y desarrollo de programas de tutoría.'
    },
    {
      name: 'Ana Martínez',
      role: 'Responsable de Tecnología',
      image: 'https://ui-avatars.com/api/?name=Ana+Martínez&background=8b5cf6&color=fff&size=150',
      description: 'Ingeniera de Software enfocada en crear experiencias educativas digitales.'
    }
  ]

  const stats = [
    { number: '2,500+', label: 'Estudiantes Activos' },
    { number: '300+', label: 'Tutores Certificados' },
    { number: '15,000+', label: 'Sesiones Completadas' },
    { number: '4.9/5', label: 'Calificación Promedio' }
  ]

  return (
    <div className="min-h-screen bg-white">
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
              Acerca de STEP
            </h1>
            <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto opacity-90">
              Conectamos estudiantes con tutores pares para crear una comunidad 
              de aprendizaje colaborativo y exitoso.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                Nuestra Misión
              </h2>
              <p className="text-lg text-gray-600 mb-6 leading-relaxed">
                En STEP, creemos que el aprendizaje entre pares es una de las formas más 
                efectivas de educación. Nuestra misión es crear una plataforma donde 
                estudiantes puedan conectarse con tutores que han pasado por experiencias 
                similares y pueden ofrecer perspectivas únicas y relevantes.
              </p>
              <p className="text-lg text-gray-600 leading-relaxed">
                Trabajamos para democratizar el acceso a la educación de calidad, 
                haciendo que la tutoría personalizada sea accesible, flexible y 
                efectiva para todos los estudiantes.
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="relative"
            >
              <img
                src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=600&h=400&fit=crop"
                alt="Estudiantes colaborando"
                className="rounded-lg shadow-lg"
              />
              <div className="absolute -bottom-6 -right-6 bg-primary-600 text-white p-6 rounded-lg shadow-lg">
                <BookOpen className="h-8 w-8 mb-2" />
                <div className="text-2xl font-bold">5 años</div>
                <div className="text-sm opacity-90">de experiencia</div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Nuestros Valores
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Los principios que guían nuestro trabajo y definen nuestra cultura organizacional
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <value.icon className="h-8 w-8 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {value.title}
                </h3>
                <p className="text-gray-600">
                  {value.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-primary-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Nuestro Impacto
            </h2>
            <p className="text-xl opacity-90">
              Números que reflejan nuestro compromiso con la excelencia educativa
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.5 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-4xl md:text-5xl font-bold mb-2">
                  {stat.number}
                </div>
                <div className="text-lg opacity-90">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                ¿Por qué elegir STEP?
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                Ofrecemos una experiencia de tutoría única que combina la efectividad 
                del aprendizaje entre pares con la comodidad de la tecnología moderna.
              </p>
              <div className="grid gap-4">
                {features.map((feature, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className="flex items-center"
                  >
                    <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                    <span className="text-gray-700">{feature}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <img
                src="https://images.unsplash.com/photo-1556761175-b413da4baf72?w=600&h=400&fit=crop"
                alt="Plataforma STEP"
                className="rounded-lg shadow-lg"
              />
            </motion.div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Nuestro Equipo
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Profesionales apasionados por la educación y la tecnología
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {team.map((member, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="text-center"
              >
                <img
                  src={member.image}
                  alt={member.name}
                  className="w-32 h-32 rounded-full mx-auto mb-4 shadow-lg"
                />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {member.name}
                </h3>
                <p className="text-primary-600 font-medium mb-3">
                  {member.role}
                </p>
                <p className="text-gray-600">
                  {member.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              ¿Listo para formar parte de STEP?
            </h2>
            <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
              Únete a nuestra comunidad de aprendizaje y descubre cómo la tutoría 
              entre pares puede transformar tu experiencia educativa.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-white text-primary-600 hover:bg-gray-100 font-semibold py-4 px-8 rounded-lg transition-colors duration-200">
                Registrarse como Estudiante
              </button>
              <button className="border-2 border-white text-white hover:bg-white hover:text-primary-600 font-semibold py-4 px-8 rounded-lg transition-colors duration-200">
                Ser Tutor
              </button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default About