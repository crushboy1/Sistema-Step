import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'
import { 
  Search, 
  Filter, 
  Star, 
  Clock, 
  DollarSign, 
  Users, 
  BookOpen,
  Plus,
  MapPin,
  Calendar
} from 'lucide-react'

const Courses = () => {
  const { user } = useAuth()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')

  const categories = [
    { id: 'all', name: 'Todos' },
    { id: 'matematicas', name: 'Matemáticas' },
    { id: 'fisica', name: 'Física' },
    { id: 'quimica', name: 'Química' },
    { id: 'biologia', name: 'Biología' },
    { id: 'programacion', name: 'Programación' },
    { id: 'idiomas', name: 'Idiomas' }
  ]

  const courses = [
    {
      id: 1,
      title: 'Cálculo Diferencial e Integral',
      tutor: 'María González',
      tutorAvatar: 'https://ui-avatars.com/api/?name=María+González&background=3b82f6&color=fff',
      category: 'matematicas',
      price: 25,
      rating: 4.9,
      students: 45,
      duration: '2 horas',
      description: 'Aprende los fundamentos del cálculo con ejercicios prácticos y explicaciones claras.',
      image: 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&h=250&fit=crop',
      schedule: 'Lun, Mié, Vie - 18:00',
      mode: 'online'
    },
    {
      id: 2,
      title: 'Física Mecánica',
      tutor: 'Carlos Rodríguez',
      tutorAvatar: 'https://ui-avatars.com/api/?name=Carlos+Rodríguez&background=22c55e&color=fff',
      category: 'fisica',
      price: 30,
      rating: 4.8,
      students: 32,
      duration: '1.5 horas',
      description: 'Domina los conceptos de mecánica clásica con problemas resueltos paso a paso.',
      image: 'https://images.unsplash.com/photo-1636466497217-26a8cbeaf0aa?w=400&h=250&fit=crop',
      schedule: 'Mar, Jue - 16:00',
      mode: 'presencial'
    },
    {
      id: 3,
      title: 'Química Orgánica',
      tutor: 'Ana Martínez',
      tutorAvatar: 'https://ui-avatars.com/api/?name=Ana+Martínez&background=8b5cf6&color=fff',
      category: 'quimica',
      price: 28,
      rating: 4.7,
      students: 28,
      duration: '2 horas',
      description: 'Comprende las reacciones orgánicas y mecanismos de síntesis.',
      image: 'https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=400&h=250&fit=crop',
      schedule: 'Sáb - 10:00',
      mode: 'online'
    },
    {
      id: 4,
      title: 'Programación en Python',
      tutor: 'Luis Fernández',
      tutorAvatar: 'https://ui-avatars.com/api/?name=Luis+Fernández&background=f59e0b&color=fff',
      category: 'programacion',
      price: 35,
      rating: 4.9,
      students: 67,
      duration: '3 horas',
      description: 'Aprende Python desde cero hasta proyectos avanzados.',
      image: 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=400&h=250&fit=crop',
      schedule: 'Lun, Mié - 19:00',
      mode: 'online'
    },
    {
      id: 5,
      title: 'Inglés Conversacional',
      tutor: 'Sarah Johnson',
      tutorAvatar: 'https://ui-avatars.com/api/?name=Sarah+Johnson&background=ef4444&color=fff',
      category: 'idiomas',
      price: 20,
      rating: 4.8,
      students: 89,
      duration: '1 hora',
      description: 'Mejora tu fluidez en inglés con conversaciones prácticas.',
      image: 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400&h=250&fit=crop',
      schedule: 'Todos los días - 17:00',
      mode: 'online'
    },
    {
      id: 6,
      title: 'Biología Molecular',
      tutor: 'Dr. Roberto Silva',
      tutorAvatar: 'https://ui-avatars.com/api/?name=Roberto+Silva&background=06b6d4&color=fff',
      category: 'biologia',
      price: 32,
      rating: 4.6,
      students: 23,
      duration: '2.5 horas',
      description: 'Explora los procesos moleculares de la vida.',
      image: 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400&h=250&fit=crop',
      schedule: 'Vie - 14:00',
      mode: 'presencial'
    }
  ]

  const filteredCourses = courses.filter(course => {
    const matchesSearch = course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         course.tutor.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || course.category === selectedCategory
    return matchesSearch && matchesCategory
  })

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
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {user?.role === 'tutor' ? 'Mis Cursos' : 'Explorar Cursos'}
              </h1>
              <p className="text-gray-600 mt-2">
                {user?.role === 'tutor' 
                  ? 'Gestiona tus cursos y crea nuevos'
                  : 'Encuentra el curso perfecto para ti'
                }
              </p>
            </div>
            {user?.role === 'tutor' && (
              <button className="btn-primary mt-4 md:mt-0 flex items-center">
                <Plus className="h-5 w-5 mr-2" />
                Crear Nuevo Curso
              </button>
            )}
          </div>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mb-8"
        >
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                type="text"
                placeholder="Buscar cursos o tutores..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Category Filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <select
                className="pl-10 pr-8 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent appearance-none bg-white"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </motion.div>

        {/* Courses Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course, index) => (
            <motion.div
              key={course.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300"
            >
              {/* Course Image */}
              <div className="relative h-48 overflow-hidden">
                <img
                  src={course.image}
                  alt={course.title}
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-4 right-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    course.mode === 'online' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-blue-100 text-blue-800'
                  }`}>
                    {course.mode}
                  </span>
                </div>
              </div>

              {/* Course Content */}
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                    {course.title}
                  </h3>
                  <div className="flex items-center ml-2">
                    <Star className="h-4 w-4 text-yellow-400 fill-current" />
                    <span className="text-sm text-gray-600 ml-1">{course.rating}</span>
                  </div>
                </div>

                {/* Tutor */}
                <div className="flex items-center mb-3">
                  <img
                    src={course.tutorAvatar}
                    alt={course.tutor}
                    className="w-8 h-8 rounded-full mr-2"
                  />
                  <span className="text-sm text-gray-600">{course.tutor}</span>
                </div>

                {/* Description */}
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                  {course.description}
                </p>

                {/* Course Info */}
                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <Calendar className="h-4 w-4 mr-2" />
                    {course.schedule}
                  </div>
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      {course.duration}
                    </div>
                    <div className="flex items-center">
                      <Users className="h-4 w-4 mr-1" />
                      {course.students} estudiantes
                    </div>
                  </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <div className="flex items-center">
                    <DollarSign className="h-5 w-5 text-green-600" />
                    <span className="text-xl font-bold text-gray-900">
                      {course.price}
                    </span>
                    <span className="text-sm text-gray-600 ml-1">/sesión</span>
                  </div>
                  
                  {user?.role === 'tutor' ? (
                    <div className="flex space-x-2">
                      <button className="btn-secondary text-sm py-1 px-3">
                        Editar
                      </button>
                      <button className="btn-primary text-sm py-1 px-3">
                        Ver
                      </button>
                    </div>
                  ) : (
                    <button className="btn-primary text-sm py-2 px-4">
                      Inscribirse
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Empty State */}
        {filteredCourses.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="text-center py-12"
          >
            <BookOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No se encontraron cursos
            </h3>
            <p className="text-gray-600">
              Intenta ajustar tus filtros de búsqueda
            </p>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default Courses