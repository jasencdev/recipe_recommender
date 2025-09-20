import { Routes, Route, Navigate } from 'react-router-dom'
import '../styles/App.css'

import Search from './pages/search'
import Login from './pages/login'
import ProtectedRoute from './components/ProtectedRouter'
import Registration from './pages/registration'
import Recommendations from './pages/recommendations'
import SavedRecipes from './pages/saved-recipes'
import RecipeDetail from './pages/recipe-detail'
import Collections from './pages/collections'
import ForgotPassword from './pages/forgot-password'
import ResetPassword from './pages/reset-password'

function App() {

  return (
    <Routes>
      <Route path="/" element={<ProtectedRoute><Search /></ProtectedRoute>} />
      <Route path="/search" element={<ProtectedRoute><Search /></ProtectedRoute>} />
      <Route path="/recommendations" element={<ProtectedRoute><Recommendations /></ProtectedRoute>} />
      <Route path="/saved-recipes" element={<ProtectedRoute><SavedRecipes /></ProtectedRoute>} />
      <Route path="/collections" element={<ProtectedRoute><Collections /></ProtectedRoute>} />
      <Route path="/recipe/:id" element={<ProtectedRoute><RecipeDetail /></ProtectedRoute>} />
      <Route path="/login" element={<Login />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/registration" element={<Registration />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default App
